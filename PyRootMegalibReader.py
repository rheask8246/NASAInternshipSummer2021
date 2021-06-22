#!/usr/bin/env python
"""
------------------------------------------------------------------------

A script to read in simulated MEGALib events & store infomation as pandas dataframes.

Author: Henrike Fleischhack (fleischhack@cua.edu)
Date: August 13th, 2020

------------------------------------------------------------------------
"""

import os
import time
import sys
import fileinput
import numpy
from itertools import product, combinations, repeat
from collections import OrderedDict
import glob
import pandas
import math
import pickle

import gzip

from astropy.coordinates import cartesian_to_spherical, spherical_to_cartesian

from matplotlib import pyplot

import ROOT

ROOT.gSystem.Load("$(MEGALIB)/lib/libMEGAlib.so")

# Initialize MEGAlib
G = ROOT.MGlobal()
G.Initialize()

#We can use these to make printing of MEGAlib (and other root classes) easier.
def MegaPrint(self):
    try:
        return self.Data()
    except:
        return ":("
    
def MegaToStringPrint(self):
    try:
        return self.ToString().Data()
    except:
        return ":("

def MegaNamePrint(self):
    try:
        return self.GetName().Data()
    except:
        return ":("

setattr(ROOT.MString, '__str__', MegaPrint)
setattr(ROOT.MVector, '__str__', MegaToStringPrint)
setattr(ROOT.MSimHT, '__str__', MegaToStringPrint)
setattr(ROOT.MSimIA, '__str__', MegaToStringPrint)
setattr(ROOT.MComptonEvent, '__str__', MegaToStringPrint)
setattr(ROOT.MPairEvent, '__str__', MegaToStringPrint)
setattr(ROOT.MPhysicalEvent, '__str__', MegaToStringPrint)
setattr(ROOT.MDDetector, '__str__', MegaNamePrint)
setattr(ROOT.MDVoxel3D,  '__str__', MegaNamePrint)
setattr(ROOT.MDStrip2D,  '__str__', MegaNamePrint)


def MegaSimEventToDict(Event, Geometry):

    theDict = {}
       
    theHits = []
       
    theDict["ID"] = Event.GetID()
    
    pos1 = Event.GetIAAt(1).GetPosition()
    vol = Geometry.GetVolume( pos1 )
    
    theDict["TrueFirstIAVolume"] = vol.GetName().Data()
    
    if vol.IsSensitive():
        theDict["TrueFirstIADetector"] = vol.GetDetector().GetName().Data()
    else:
        theDict["TrueFirstIADetector"] = "passive"
    
    theDict["TrueFirstIAX"] = pos1.GetX()
    theDict["TrueFirstIAY"] = pos1.GetY()
    theDict["TrueFirstIAZ"] = pos1.GetZ()
       
    #First interaction type
    theDict["TrueType"] = Event.GetIAAt(1).GetProcess().Data()

    #The ED keyword (Total energy deposit in active material)
    ED = 0.0;
        
    for iH in range(0, Event.GetNHTs()):
        theHit = Event.GetHTAt(iH)
        Ehit = theHit.GetEnergy()
        ED += Ehit
        
        detectorType = theHit.GetDetector()
           
        theKey = "NHit_{}".format( detectorType )
        theDict[ theKey ] = theDict.get(theKey, 0) + 1
               
        theKey = "EHit_{}".format( detectorType )
        theDict[ theKey ] = theDict.get(theKey, 0) + Ehit/1e3
        
        hitDict = {}
        hitPos = theHit.GetPosition()
        hitDict["ID"] = theDict["ID"]
               
        hitDict["HitX"] = hitPos.GetX()
        hitDict["HitY"] = hitPos.GetY()
        hitDict["HitZ"] = hitPos.GetZ()
        hitDict["HitEnergy"] = Ehit/1e3
                
        hitDict["HitDetector"] = Geometry.GetDetector( theHit.GetPosition() ).GetName().Data()
        theHits.append( hitDict )
           
    for iH in range(0, Event.GetNGRs()):
        ED += Event.GetGRAt(iH).GetEnergy()
    theDict["ED"] = ED
         
    #The EC keyword (Escapes)
    EC = 0.0;
    for iA in range(0, Event.GetNIAs()):
        if (Event.GetIAAt(iA).GetProcess().Data() == "ESCP"):
            EC += Event.GetIAAt(iA).GetMotherEnergy()
    theDict["EC"] = EC
         
    #Deposits in non-sensitive material
    theDict["NS"] = Event.GetEnergyDepositNotSensitiveMaterial()
       
    #incoming gamma-ray energy
    theDict["TrueEnergy"] = Event.GetICEnergy()/1e3
       
    #First interaction type
    theDict["TrueType"] = Event.GetIAAt(1).GetProcess().Data()
       
    initialPhotonDirection = -1*Event.GetICOrigin()
       
    theDict["TrueTheta"] = initialPhotonDirection.Theta()
    theDict["TruePhi"] =  initialPhotonDirection.Phi()

    if theDict["TrueType"] == "COMP":
        theDict["TrueThetaC"] = Event.GetICScatterAngle()       #True Compton angle
        theDict["TrueThetaE"] = Event.GetICElectronD().Angle(Event.GetICOrigin()) #True electron angle
        
    if theDict["TrueType"] == "PAIR":
        theDict["TruePairAngle"] = Event.GetIPPositronDir().Angle(Event.GetIPElectronDir() )
    
    
    return theDict, theHits


def readSimFile( FileName, GeometryName ):
    
    fileinfo = {}
    fileinfo["filename"] = FileName

    theEvents = []
    theHits = []

    #parse some info by hand
    
    if FileName[-2:] == "gz":
        import gzip
        op = gzip.open
    else:
        op = open
    
    with op(FileName, mode="rt") as fp:
        for line in fp:
            fields = line.replace(";", " ").split()
        
            if len(fields) < 1:
                continue
            
            keyword = fields[0]

            if keyword == "SimulationStartAreaFarField":
                fileinfo["Area"] = float(fields[1])
            elif keyword == "BeamType" and fields[1] == "FarFieldPointSource":
                fileinfo["SourceTheta"] = numpy.deg2rad(float(fields[2]))
                fileinfo["SourcePhi"] = numpy.deg2rad(float(fields[3]))
            elif keyword == "SpectralType" and fields[1] == "Mono":
                fileinfo["SourceEnergy"] = float(fields[2])/1000 #keV to MeV
            
            #first event! We'll use MEGAlib for the rest.
            if keyword == "SE":
                break

    # Use MEGAlib reader for the rest
    Geometry = ROOT.MDGeometryQuest()
    
    if Geometry.ScanSetupFile(ROOT.MString(GeometryName)) == True:
        print("Geometry " + GeometryName + " loaded!")
    else:
        print("Unable to load geometry " + GeometryName + " - Aborting!")
        quit()

    Reader = ROOT.MFileEventsSim(Geometry)
    if Reader.Open(ROOT.MString(FileName)) == False:
        print("Unable to open file " + FileName + ". Aborting!")
        quit()

    fileinfo["Area"] = Reader.GetSimulationStartAreaFarField()

    while True:
    
        Event = Reader.GetNextEvent()
        if not Event:
            break
        ROOT.SetOwnership(Event, True)
        
        eventDict, hitList = MegaSimEventToDict(Event, Geometry)
        theEvents.append( eventDict )
        theHits.extend( hitList )
               
    fileinfo["thrownEvents"] = Reader.GetSimulatedEvents()

    df = pandas.DataFrame(theEvents)
    
    #cleanup
    df.fillna(0, inplace=True)
    for b in ["NHit_1", "NHit_2", "NHit_4", "NHit_8"]:
        if b in df.columns:
            df = df.astype( {b:'int32' } )
        
    df.set_index("ID", inplace = True)


    df2 = pandas.DataFrame(theHits)
    df2.fillna(0, inplace = True)
    
    try:
        df2.set_index("ID", inplace = True)
    except:
        pass

    return df, df2, fileinfo
    
    
def MegaTraEventToDict( Event):

    theDict = {}
    
    theDict["ID"] = Event.GetId()
           
    theType = Event.GetTypeString().Data()
    
    theDict["RecoType"] = theType
        
    if theType == "Unidentifiable":
        theDict["RecoType"] = "bad"

        theDict["Subtype"] = " ({})".format(Event.GetBadString().Data() )
            

    if theType == "Compton":
        
        comptonPhotonEnergy = Event.Eg()/1e3
        comptonElectronEnergy = Event.Ee()/1e3
        
        totalEnergy = comptonPhotonEnergy+comptonElectronEnergy
        theDict["RecoEnergy"] = totalEnergy

        theDict["RecoThetaC_Cal"] = Event.Phi()
        theDict["RecoThetaE_Cal"] = Event.Epsilon()

        theDict["RecoDeltaTheta"] = Event.DeltaTheta()
                
        if Event.HasTrack():
            theDict["Subtype"] = " (tracked)"
        else:
            theDict["Subtype"] = " (untracked)"
                
        originalGammaDirection = -Event.GetOIDirection()
        scatteredGammaDirection = Event.C2() - Event.C1()
        theDict["RecoThetaC_Track"] = originalGammaDirection.Angle( scatteredGammaDirection )
    
    elif theType == "Pair":
    
        pairEnergy = Event.GetEnergy()/1e3
        theDict["RecoEnergy"] = pairEnergy
        theDict["RecoTheta"] = Event.GetOrigin().Theta()
        theDict["RecoPhi"] = Event.GetOrigin().Phi()
        theDict["RecoPairAngle"] = Event.GetOpeningAngle()
        theDict["RecoDelAngle"] = Event.GetOrigin().Angle(-Event.GetOIDirection())
        
    return theDict



def readTraFile( FileName ):
    
    theEvents = []

    Reader = ROOT.MFileEventsTra()
    if Reader.Open(ROOT.MString(FileName)) == False:
        print("Unable to open file " + FileName + ". Aborting!")
        quit()

    while True:
    
        Event = Reader.GetNextEvent()
        if not Event:
            break
        ROOT.SetOwnership(Event, True)
        
        eventDict = MegaTraEventToDict(Event)
        theEvents.append( eventDict )

    if len(theEvents) > 0:
        df = pandas.DataFrame(theEvents)
       
        #cleanup
        df["Subtype"] = df["Subtype"].fillna( "" )
        df.set_index("ID", inplace = True)

        return df
    
    else:
        return None
        

def readOneSetOfSims( geometry, simFileName, traFileName = None ):
   
    print (geometry, simFileName, traFileName)
   
    if traFileName is None:
        traFileName = simFileName.replace(".sim", ".tra")
    
    simDfName = simFileName + ".csv"
    hitDfName = simFileName.replace(".sim", ".hits.csv" ).replace(".gz", "")
    simInfoName = simFileName + ".pkl"
    dfName = traFileName + ".csv"
    
    simData, hitData, simInfo = readSimFile(simFileName, geometry)
    simData.to_csv( simDfName )
    hitData.to_csv( hitDfName )
    with open(simInfoName,"wb") as f:
        pickle.dump(simInfo,f)


    recData = readTraFile(traFileName)
        
    #0 events in file
    if recData is None:
        return simData, hitData, simInfo, None, None, None
        
    df = simData.join(recData)
    
    df["RecoType"] = df["RecoType"].fillna( "no trigger" )
    df["Subtype"] = df["Subtype"].fillna( "" )
                
    df["LongType"] = df.RecoType + df.Subtype

    df.to_csv(dfName)
 

    return simData, hitData, simInfo, df
    
    
#Usage: Import this file and then call e.g.
#_, _, _, df1 = readOneSetOfSims( "/Users/hfleisc1/amego_software/ComPair/Geometry/AMEGO_Midex/TradeStudies/Tracker/BasePixelTracker/AmegoBase.geo.setup", "/Users/hfleisc1/amego_software/ComPair/simfiles/test_pixel/sim/FarFieldPointSource_100.000MeV_Cos0.8_Phi0.0.inc1.id1.sim", "/Users/hfleisc1/amego_software/ComPair/simfiles/test_pixel/revan/FarFieldPointSource_100.000MeV_Cos0.8_Phi0.0.inc1.id1.tra",   )
