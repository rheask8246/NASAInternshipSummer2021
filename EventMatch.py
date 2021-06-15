import argparse

'''
This program compares events between the standard and Kalman event reconstructions
and outputs how many events match between them.
Author: Rhea Senthil Kumar
'''

#command line/variable setup
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

#counts number of events that are only in standard list
def excStdList(stdFile, kalmanFile):
    stdList = id_list(stdFile)
    kalmanList = id_list(kalmanFile)
    countstd = 0
    for i in range(len(stdList)):
        if stdList[i] not in kalmanList:
            countstd += 1
    return countstd

#counts number of events that are only in kalman list
def excKalmanList(stdFile, kalmanFile):
    stdList = id_list(stdFile)
    kalmanList = id_list(kalmanFile)
    countkalman = 0
    for i in range(len(kalmanList)):
        if kalmanList[i] not in stdList:
            countkalman += 1
    return countkalman

print("Number of events in standard reconstruction: " + str(len(id_list(StdFile))))
print("Number of events in Kalman reconstruction: " + str(len(id_list(KalmanFile))))
print("Number of shared events: " + str(eventMatch(StdFile, KalmanFile)))
print("Number of events only in standard reconstruction: " + str(excStdList(StdFile, KalmanFile)))
print("Number of events only in Kalman reconstruction: " + str(excKalmanList(StdFile, KalmanFile)))
#todo: can clean the calcualtions up
