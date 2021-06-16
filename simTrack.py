import argparse

'''
This program tracks the IDs and number of pair events in a sim file.
Author: Rhea Senthil Kumar
'''

#command line/variable setup
parser = argparse.ArgumentParser(description='Count matching event ids from 2 event reconstruction files.')
parser.add_argument("-s", "--simfile", type=str, default="FarFieldPointSource_1MeV.inc1.id1.sim")
args = parser.parse_args()

if args.simfile != "":
    SimFile = args.simfile

eventList = []

#collects all ids from one tra file and stores in a list. Returns number of pair events.
def numPair(file):
    openFile = open(file, "r")
    pairCount = 0
    currID = ""
    for line in openFile:
        values = line.split()
        if len(values) > 1 and values[0] == "ID":
            currID = line.strip()
        if len(values) > 1 and values[1] == "INIT":
            nextLine = openFile.next()
            splitLine = nextLine.split()
            if splitLine[1] == "PAIR":
                pairCount += 1
                eventList.append(currID)
        #elif len(values) > 1 and values[1] == "INIT" and
    openFile.close()
    return pairCount

print("Number of pair events: " + str(numPair(SimFile)))
#print("Pair event IDs: " + str(eventList))
