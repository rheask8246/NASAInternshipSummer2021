import os
import argparse

'''
This program compares events between the standard and Kalman event reconstructions
and outputs how many events match between them.
Author: Rhea Senthil Kumar
'''

#command line/variable setup
#CWD = os.getcwd()
parser = argparse.ArgumentParser(description='Count matching event ids from 2 event reconstruction files.')
parser.add_argument("-s", "--standardtra", type=str, default="FarFieldPointSource_1MeV.inc1.id1.tra")
parser.add_argument("-k", "--kalmantra", type=str)
args = parser.parse_args()

if args.standardtra != "":
    StdFile = args.standardtra

if args.kalmantra != "":
    KalmanFile = args.kalmantra

#collects all ids from one tra file and stores in a list
def id_list(file):
    openFile = open(file, "r")
    eventList = []
    for line in openFile:
        strpLine = line.strip()
        if len(strpLine) > 2 and strpLine[0] == 'I' and strpLine[1] == 'D':
            eventList.append(strpLine)
    return eventList

#iterates through lists and counts how many ids are the same
def eventMatch(stdFile, kalmanFile):
    stdList = id_list(stdFile)
    kalmanList = id_list(kalmanFile)
    count = 0
    for i in range(len(stdList)):
        if stdList[i] in kalmanList:
            count += 1
    return count
print("Number of events in standard reconstruction: " + str(len(id_list(StdFile))))
print("Number of events in Kalman reconstruction: " + str(len(id_list(KalmanFile))))
print("Number of shared events: " + eventMatch(StdFile, KalmanFile))
