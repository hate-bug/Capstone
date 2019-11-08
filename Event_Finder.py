from matplotlib import pyplot as plt

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
        processTuple = (start, end)
        if len(SitToStandList) > 0:
            lastTuple = SitToStandList[-1]
            if abs(processTuple[0] - lastTuple[1]) < 40:
                start = lastTuple[0]
                end = processTuple[1]
                newTuple = (start, end)
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


plotSum("slow_set.csv")
