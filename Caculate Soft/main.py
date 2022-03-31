import os
import pandas as pd
import numpy as np
from datetime import datetime
from time import gmtime, strftime
# from readLog import caculate_performance
from const import sourceCol, timeCol, messageCol, alarmFolder, outputFolder

listObject = os.listdir(alarmFolder)
# filePath = alarmFolder + '/' + listObject[-5]

def alarm_seperate_by_machine(logs):

    logMachine = {}  # { "machine name": DataFrame { "Event time": ..., "Message": .... } }

    #get machine name from Original source
    nameList = [name[:name.index('.')] for name in logs[sourceCol]] # eg BLD.BL3110RUN -> get BLD

    #sort machine name alphabetically
    machineName = sorted(list(set(nameList)))

    for name in machineName:
        logMachine[name] = logs[logs[sourceCol].str.startswith(name) == True]
        logMachine[name].sort_values(by = timeCol, inplace = True)
        eventTime = logMachine[name][timeCol]
        roundTime = []
        for i in range(len(eventTime)):
            t = eventTime.iloc[i]
            rountT = datetime(t.year, t.month, t.day, t.hour, t.minute, t.second, microsecond = 0)
            roundTime.append(rountT)
        # update new Event time with microsecond is round to 0
        logMachine[name][timeCol] = roundTime
        # delete duplicated items
        logMachine[name].drop_duplicates(inplace=True)

    # print(logMachine)
    return logMachine, machineName

def caculate_stop_time(logOneMachine):
    # logInput = logDevices[machineName]
    stopTime = pd.Timedelta(0)
    # if len(stopMessages) == 0:
    #     return 0
    # for i in range(len(stopMessages)):
    #     print(stopMessages.iloc[i][messageCol])
    stopIndexs = np.where(logOneMachine[messageCol].str.endswith("STOP") == True) #tuple
    stopIndexs = list(reversed(list(stopIndexs[0])))
    # remove adjacent number
    for x in stopIndexs:
        # print(x)
        if (x - 1) in stopIndexs:
            stopIndexs.remove(x)
    stopIndexs = list(reversed(stopIndexs))
    logLen = len(logOneMachine)
    [dataStopTime, dataStopMessage, dataRunTime, dataRunMessage] = [[], [], [], []]
    # print(stopIndexs)
    for x in stopIndexs:
        if x >= (logLen - 1):
            # print("end", x, logLen)
            break
        findRun = x + 1
        endLoop = False
        while logOneMachine.iloc[findRun][messageCol].endswith("RUN") == False:
            if findRun < (logLen - 1):
                findRun = findRun + 1
            elif findRun >= (logLen - 1):
                endLoop = True
                break
        ###
        dataStopTime.append(logOneMachine.iloc[x][timeCol])
        dataStopMessage.append(logOneMachine.iloc[x][messageCol])
        dataRunTime.append(logOneMachine.iloc[findRun][timeCol])
        dataRunMessage.append(logOneMachine.iloc[findRun][messageCol])
        # calulate delta time
        deltaT = logOneMachine.iloc[findRun][timeCol] - logOneMachine.iloc[x][timeCol]
        stopTime += deltaT
        # totalStopTime = reduce(lambda x,y: x+y, stopTime)

        #End of the alarm report, finish
        if endLoop == True:
            break
    dataViewer = pd.DataFrame({
        "From STOP Time": dataStopTime,
        "STOP Message": dataStopMessage,
        "To RUN Time": dataRunTime,
        "RUN Message": dataRunMessage
    })

    operatedTime = logOneMachine.iloc[-1][timeCol] - logOneMachine.iloc[0][timeCol]

    #div by zero error
    if operatedTime == pd.Timedelta(0):
        return 0

    performance = (1 - stopTime/operatedTime)*100
    performance = round(performance, 2)

    # format time to display
    # stopTime     = "{:0>8}".format(str(stopTime))
    # operatedTime = "{:0>8}".format(str(operatedTime))
    stopTime = strftime("%H:%M:%S", gmtime(int(stopTime.total_seconds())))
    operatedTime = strftime("%H:%M:%S", gmtime(int(operatedTime.total_seconds())))
    # print(dataViewer.head())
    caculatedData = pd.DataFrame({
        "Stop time":[stopTime],
        "Operated time": [operatedTime],
        "Performance": [str(performance) + "%"]
    })

    excelOutputDf = pd.concat([caculatedData, dataViewer], ignore_index=True, axis=0)
    
    # caculatedData.append(dataViewer, ignore_index=True)
    # print(excelOutputDf)
    
    # with pd.ExcelWriter("testOutput.xlsx", mode='a',if_sheet_exists='replace') as outputFile:
    #     excelOutputDf.to_excel(outputFile, sheet_name=name, index=False, startrow=0)
    
    return performance

def summary_performace_by_day(filePath):

    performanceSum = {
    }

    # alarmDate = filePath[-24:-14]
    # performanceSum["Date"] = [alarmDate]
    # print(alarmDate)
    # read alarm report file
    logs = pd.read_excel(filePath, skiprows=3)
    #remove rows include N/A values
    logs.dropna(axis=0, thresh=3, inplace=True)

    #remove cols include N/A values
    logs.dropna(axis=1, thresh=3, inplace=True)

    # alarm report date
    alarmDate = logs[timeCol].median().date()
    performanceSum["Date"] = [alarmDate]

    #alarm seperate by machine, and return machine name list
    logAllMachine, nameAllMachine = alarm_seperate_by_machine(logs)
    # print(logAllMachine)
    for name in nameAllMachine:
        performanceSum[name] = [caculate_stop_time(logAllMachine[name])]
    
    # print(performanceSum)
    return performanceSum

def summary_performance_by_month(listFile):
    
    monthSummaryList = []
    completeNum = len(listFile)
    percentRun = 0
    for oneFile in listFile:
        percentRun += 1
        filePath = alarmFolder + oneFile
        # onedaySummaryDf = summary_performace_by_day(filePath)
        # print(onedaySummaryDf)
        onedaySummaryDf = pd.DataFrame(summary_performace_by_day(filePath))
        # print(onedaySummaryDf)
        monthSummaryList.append(onedaySummaryDf)
        print("Caculating.... ", percentRun, '/', completeNum)
    monthSummaryDf = pd.concat(monthSummaryList)
    monthSummaryDf.fillna(0, inplace = True)
    print(monthSummaryDf)
    return monthSummaryDf

monthSumDf = summary_performance_by_month(listObject)
excelOutputFilePath = outputFolder + 'Performance Of Machine 3-2022.xlsx'
monthSumDf.to_excel(excelOutputFilePath, sheet_name="03.2022", index=False)

# filePath = filePath = alarmFolder + '/' + listObject[0]
# summary_performace_by_day(filePath)