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

pairEventList = []
compEventList = []

#collects all ids from one tra file and stores in a list. Returns number of pair events.
def numPair(file):
    openFile = open(file, "r")
    pairCount = 0
    comptonCount = 0
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
                pairEventList.append(currID)
            elif splitLine[1] = "COMP":
                comptonCount += 1
                compEventList.append(currID)
        #elif len(values) > 1 and values[1] == "INIT" and
    openFile.close()
    return comptonCount, pairCount

counts = numPair(SimFile)
print("Compton events: {0[0]}, Pair events: {0[1]}".format(counts))
#print("Pair event IDs: " + str(eventList))
