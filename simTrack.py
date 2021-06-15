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

    for line in openFile:
        values = line.split()
        if values[0] == "ID":
            print(line.strip())
    openFile.close()

print("Number of pair events: " + str(numPair(SimFile)))
print("Pair event IDs: " + eventList)
