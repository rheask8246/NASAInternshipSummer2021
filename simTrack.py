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
    lines = openFile.readlines()
    for i in range(0, len(lines)):
        line = lines[i]
        if len(line) > 2 and line[0] == 'I' and line[1] == 'D':
            j = i+1
            iterline = lines[j]
            while iterline[0] != 'I' and iterline[1] != 'D' and j < len(lines):
                if iterline[3] == 'I' and iterline[4] == "N" and iterline[5] == "I" and iterline[6] == "T":
                    checkLine = lines[j+1]
                    if checkLine[3] == "P" and checkLine[4] == "A" and checkLine[5] == "I" and checkLine[6] == "R":
                        strpLine = line.strip()
                        eventList.append(strpLine)
                        pairCount += 1
                        break
                j += 1
    return pairCount

print("Number of pair events: " + str(numPair(SimFile)))
print("Pair event IDs: " + eventList)
