from matplotlib import pyplot as plt
import numpy as np
import csv
import math

"""
Generate a new CSV file to current location. Named: currentfilename_resulr.csv
@:param: Current file name
"""


def csvCreator(fileName):
    sumList = getSum(fileName)
    DerivativeList = derivative(sumList)
    plt.plot(sumList)
    dampList = getDamp(DerivativeList)
    processTuples = getSitToStandProcess(dampList, DerivativeList)
    acuteAngleNum = []
    for singleTuple in processTuples:
        acuteAngleNum.append(get_acute_angle_count(singleTuple, fileName))
    outputFileName = str(fileName).split(".csv")[0]
    outputFileName = outputFileName + "_result" + ".csv"
    with open(outputFileName, 'w') as csvfile:
        filewriter = csv.writer(csvfile, delimiter=',',
                                quotechar='"', quoting=csv.QUOTE_MINIMAL)
        index = 0
        filewriter.writerow(['index', 'time', 'Type'])
        for values in processTuples:
            if len(values) == 3:
                filewriter.writerow([index, getTime(values), values[2]])
            else:
                filewriter.writerow([index, getTime(values)])
            index = index + 1


"""
Function to the the sum of each row in the CSV file
Input: Name of the csv file in the path
Output: List of values represent the sum value of each row
"""


def getSum(fileName):
    with open(fileName) as csvfile:
        next(csvfile)
        next(csvfile)
        next(csvfile)
        next(csvfile)
        sumList = []
        for rows in csvfile:
            rowNum = 0
            data = rows.split(",")
            del data[0: 4]
            del data[-1]
            sum = 0
            for a in data:
                sum = sum + int(a)
            sumList.append(sum)
        return sumList


"""
Plot the graph and set all the y lines to visualize the data
"""


def plotSum(fileName):
    sumList = getSum(fileName)
    DerivativeList = derivative(sumList)
    plt.plot(sumList)
    dampList = getDamp(DerivativeList)
    processTuples = getSitToStandProcess(dampList, DerivativeList)
    DotList = []
    for ProcessTuples in processTuples:
        DotList.append(ProcessTuples[0])
        DotList.append(ProcessTuples[1])
        get_acute_angle_count(ProcessTuples, fileName)
    for value in DotList:
        plt.axvline(x=value, color='red')
    plt.show()
    return


"""
Function to get the derivative list of input list
Param: List of values
Return: List of derivation of input list 
"""


def derivative(sumList):
    result = []
    for x in range(0, len(sumList) - 1):
        difference = sumList[x + 1] - sumList[x]
        result.append(difference)
    return result


"""
Function to retuen the damp of a dataset
param: The derivative list 
return: List of points represent the damp 
"""


def getDamp(devList):  # Each spike means a sitdown
    dampPoints = []
    minValue = min(devList)
    for index in range(0, len(devList) - 1):
        if devList[index] < minValue * (0.1):  # if value small than 0.5*MinValue, consider as a stand
            while devList[index] > devList[index + 1] and devList[index + 1] < devList[index + 2]:
                index = index + 1
            if len(dampPoints) > 1:
                if abs(dampPoints[-1] - index) > 10:
                    dampPoints.append(index)
            else:
                dampPoints.append(index)
    return dampPoints


"""
Find the end of damp 
@param: the location of damp, list that contains that damp 
return: The index number of the list that is the start of the damp 
"""


def getPrecedingStablePoint(dampIndex, devList):
    while dampIndex > 0 and abs(devList[dampIndex]) > 200:
        dampIndex = dampIndex - 1
    if dampIndex - 10 > 0:
        dampIndex = dampIndex - 10
    return dampIndex


"""
Find the start of the damp 
@param: The location of damp, list that contains the damp 
return: The index of the list that is the end of the damp 
"""


def getSuccedingStablePoint(dampIndex, devList):
    while dampIndex < (len(devList) - 1) and abs(devList[dampIndex]) > 200:
        dampIndex = dampIndex + 1
    if dampIndex + 10 < len(devList):
        dampIndex = dampIndex + 10
    return dampIndex


"""
Return list of tuples for sit to stand process
"""


def getSitToStandProcess(dampList, devList):
    SitToStandList = []
    for dampIndex in dampList:
        start = getPrecedingStablePoint(dampIndex, devList)
        end = getSuccedingStablePoint(dampIndex, devList)
        if end - start < 30:
            processTuple = (start, end, "fast")
        else:
            processTuple = (start, end, "slow")
        if len(SitToStandList) > 0:
            lastTuple = SitToStandList[-1]
            if abs(processTuple[0] - lastTuple[1]) < 40:
                start = lastTuple[0]
                end = processTuple[1]
                newTuple = (start, end, "bouncing")
                SitToStandList[-1] = newTuple
            else:
                SitToStandList.append(processTuple)
        else:
            SitToStandList.append(processTuple)

    # sanitizer for the tuple list
    for index in range(0, len(SitToStandList) - 1):
        currentTuple = SitToStandList[index]
        nextTuple = SitToStandList[index + 1]
        if currentTuple[1] > nextTuple[0]:
            SitToStandList[index] = (0, 0)
    SitToStandList = list(dict.fromkeys(SitToStandList))
    if (0, 0) in SitToStandList:
        SitToStandList.remove((0, 0))
    return SitToStandList


"""
Caculate the number of acute abgle based on the tuple and the CSV filename
"""


def get_acute_angle_count(segment, FileName):
    # find the start and end point of the sit-to-stand
    start = segment[0]
    end = segment[1]

    my_list = []
    with open(FileName, "r") as csvfile:
        # skipping headers
        next(csvfile)
        next(csvfile)
        next(csvfile)
        next(csvfile)

        x_coordinate = []
        y_coordinate = []
        colNum = 0
        for rec in csv.reader(csvfile, delimiter=','):
            if start < colNum < end:
                rowdata = []
                i = 0
                for x in rec:
                    if i == 0:
                        # convert time to ms
                        rowdata.append(x)
                    elif x == '':
                        # skip the last element of a row
                        break
                    else:
                        rowdata.append(int(x))
                    i = i + 1

                xsum = (rowdata[7] * 1 + rowdata[19] * 2 + rowdata[6] * 3 + rowdata[18] * 4 + rowdata[5] * 5 + rowdata[
                    17] * 6 + rowdata[4] * 7 + rowdata[16] * 8) + (
                               rowdata[11] * 1 + rowdata[23] * 2 + rowdata[10] * 3 + rowdata[22] * 4 + rowdata[
                           9] * 5 + rowdata[21] * 6 + rowdata[8] * 7 + rowdata[20] * 8) + (
                               rowdata[15] * 1 + rowdata[27] * 2 + rowdata[14] * 3 + rowdata[26] * 4 + rowdata[
                           13] * 5 + rowdata[25] * 6 + rowdata[12] * 7 + rowdata[24] * 8)
                ysum = (rowdata[7] * 1 + rowdata[11] * 2 + rowdata[15] * 3) + (
                        rowdata[19] * 1 + rowdata[23] * 2 + rowdata[27] * 3) + (
                               rowdata[6] * 1 + rowdata[10] * 2 + rowdata[14] * 3) + (
                               rowdata[18] * 1 + rowdata[22] * 2 + rowdata[26] * 3) + (
                               rowdata[5] * 1 + rowdata[9] * 2 + rowdata[13] * 3) + (
                               rowdata[17] * 1 + rowdata[21] * 2 + rowdata[25] * 3) + (
                               rowdata[4] * 1 + rowdata[8] * 2 + rowdata[12] * 3) + (
                               rowdata[16] * 1 + rowdata[20] * 2 + rowdata[24] * 3)
                psum = rowdata[4] + rowdata[5] + rowdata[6] + rowdata[7] + rowdata[8] + rowdata[9] + rowdata[10] + \
                       rowdata[11] + rowdata[12] + rowdata[13] + rowdata[14] + rowdata[15] + rowdata[16] + rowdata[17] + \
                       rowdata[18] + rowdata[19] + rowdata[20] + rowdata[21] + rowdata[22] + rowdata[23] + rowdata[24] + \
                       rowdata[25] + rowdata[26] + rowdata[27]
                x = xsum / psum
                y = ysum / psum
                x_coordinate.append(x)
                y_coordinate.append(y)
                my_list.append(rowdata)
            colNum = colNum + 1
    vector = []
    # find all coordinates x,y for all rows
    for index in range(0, len(x_coordinate) - 1):
        vector.append([x_coordinate[index + 1] - x_coordinate[index], y_coordinate[index + 1] - y_coordinate[index]])

    angle = []
    acute_angle_count = 0
    for index in range(0, len(vector) - 1):
        r1 = vector[index]
        r2 = vector[index + 1]
        den = np.linalg.norm(r1) * np.linalg.norm(r2)
        num = np.dot(r1, r2)
        if den > 0.00025:
            angle.append((math.acos(num / den)) * 180 / np.pi)
            acute_angle_count = acute_angle_count + 1
    return acute_angle_count


"""
Calculate the time difference for each tuple
The unit is millisecond 
"""


def getTime(processTuple):
    if (processTuple[1] > processTuple[0]):
        return 100 * (processTuple[1] - processTuple[0])
    else:
        return 0


# plotSum("slow_set.csv")
csvCreator("fast_set.csv")
