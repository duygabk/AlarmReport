# print("test python")
from datetime import datetime
from functools import reduce
import os
from time import gmtime, strftime
from turtle import color
import numpy as np
import openpyxl
import pandas as pd
import matplotlib.pyplot as plt

listObjects = os.listdir("./AlarmFiles")

# print(
#     listObjects,
#     type(listObjects)
# )



files = [f for f in listObjects if os.path.isfile(f)]

# print(files)
# read machine alarm reports
# logs = pd.read_excel(files[0], sheet_name=[0],index_col=4)
# logs = logs.dropna(inplace=True)
# logs = pd.read_excel(files[0], index_col=8, skiprows=3)
logs = pd.read_excel(files[0], skiprows=3)

# cutLogs = logs.loc
#remove rows include N/A values
logs.dropna(axis=0, thresh=3, inplace=True)

#remove cols include N/A values
logs.dropna(axis=1, thresh=3, inplace=True)

#rename columns
logs.rename(columns={ 
    list(logs)[-2] : "what",
    list(logs)[-1] : "Device" 
    }, inplace=True)

# print(logs, logs.info()) 
# print(
#     logs[0:20],
#     type(logs.columns.values)
# )

deviceName = list(set(logs["Device"]))
devicePerformance = []
# device1 = logs[logs["Device"] == "MA3601"]

logDevices = {}
timeCol     = "Event time"
statusCol   = "Status"
messageCol  = "Message"
severityCol = "Severity"
#Save and write to excel file, seperate by device name

def log_seperate_by_machine(machineName):
    # device log is wrote to dict, dict key is device name
    logDevices[machineName] = logs[logs["Device"] == machineName]
    # save to excel file, sheet name is decive name
    logDevices[machineName].sort_values(by=timeCol, inplace=True)
    eventTime = logDevices[machineName][timeCol]
    roundTime = []
    for i in range(len(eventTime)):
        t = eventTime.iloc[i]
        rountT = datetime(t.year, t.month, t.day, t.hour, t.minute, t.second, microsecond = 0)
        roundTime.append(rountT)
    # update new Event time with microsecond is round to 0
    # logDevices[dev].update(newLogDf)
    logDevices[machineName][timeCol] = roundTime
    # delete duplicated items
    logDevices[machineName].drop_duplicates(inplace=True)
    # save to excel file, sheetname seperate by device name
    with pd.ExcelWriter("logDevices.xlsx", mode='a', if_sheet_exists='replace') as logsExcel:
        logDevices[machineName].to_excel(logsExcel, sheet_name = machineName, index=False, startrow=0)

for dev in deviceName:
    log_seperate_by_machine(dev)

# filter by Severity
def log_filter_by_severity(logInput, severityNum):
    return logInput[logInput[severityCol == severityNum]]

# filter by message
def caculate_performance(machineName):
    logInput = logDevices[machineName]
    # stopMessages = logInput[logInput[messageCol].str.endswith("STOP") == True]
    stopTime = pd.Timedelta(0)
    # if len(stopMessages) == 0:
    #     return 0
    # for i in range(len(stopMessages)):
    #     print(stopMessages.iloc[i][messageCol])
    stopIndexs = np.where(logInput[messageCol].str.endswith("STOP") == True) #tuple
    stopIndexs = list(reversed(list(stopIndexs[0])))
    # remove adjacent number
    for x in stopIndexs:
        # print(x)
        if (x - 1) in stopIndexs:
            stopIndexs.remove(x)
    stopIndexs = list(reversed(stopIndexs))
    logLen = len(logInput)
    [dataStopTime, dataStopMessage, dataRunTime, dataRunMessage] = [[], [], [], []]
    # print(stopIndexs)
    for x in stopIndexs:
        if x >= (logLen - 1):
            # print("end", x, logLen)
            break
        findRun = x + 1
        endLoop = False
        while logInput.iloc[findRun][messageCol].endswith("RUN") == False:
            if findRun < (logLen - 1):
                findRun = findRun + 1
            elif findRun >= (logLen - 1):
                endLoop = True
                break
        ###
        dataStopTime.append(logInput.iloc[x][timeCol])
        dataStopMessage.append(logInput.iloc[x][messageCol])
        dataRunTime.append(logInput.iloc[findRun][timeCol])
        dataRunMessage.append(logInput.iloc[findRun][messageCol])
        # calulate delta time
        deltaT = logInput.iloc[findRun][timeCol] - logInput.iloc[x][timeCol]
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

    operatedTime = logInput.iloc[-1][timeCol] - logInput.iloc[0][timeCol]

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
    
    with pd.ExcelWriter("testOutput.xlsx", mode='a',if_sheet_exists='replace') as outputFile:
        excelOutputDf.to_excel(outputFile, sheet_name=machineName, index=False, startrow=0)
    
    return performance

# Caculate stop time of all device
for dev in deviceName:
    performance = caculate_performance(dev)
    devicePerformance.append(performance)

# Draw chart
def draw_chart_by_day(machineList, performanceList):
    x_axis = np.array(machineList)
    y_axis = np.array(performanceList)

    plt.bar(x_axis, y_axis, color="#4CAF50", width=0.5)
    plt.savefig('chart_by_day.png', dpi=150)
    # plt.show()
    wb = openpyxl.Workbook()
    ws = wb.active  
    ws.title = "Chart by day"

    img = openpyxl.drawing.image.Image('chart_by_day.png')

    img.anchor = 'B2' 
    
    ws.add_image(img)
    wb.save(filename = 'chart.xlsx')


draw_chart_by_day(deviceName, devicePerformance)

# caculate_stop_time("DRY")

# function device_stop_time(deviceName)
# input: device name
# output: { "bad time": xxx, "run time": }  
def device_stop_time(deviceName):
    badKey = "Bad time"
    runKey = "Run time"
    device1 = logDevices[deviceName] #Test one device, hard code, remove after
    badStatus = device1[device1[statusCol] != "Good"]
    totalRun = device1[timeCol].iloc[-1] - device1[timeCol].iloc[0]

    if len(badStatus) == 0:
        return {
            badKey: 0,
            runKey: totalRun
        }

    stopTime = []
    for i in range(len(badStatus)):
        badTime = badStatus.iloc[i][timeCol]
        # from bad status to good status return time
        goodTime = device1[device1[timeCol] > badTime][device1[statusCol] == "Good"].iloc[0][timeCol]
        stopTime.append(goodTime - badTime)
    totalStop = reduce(lambda x,y: x+y, stopTime)
    # totalRun = max(device1[timeCol]) - min(device1[timeCol])
    totalRun = device1[timeCol].iloc[-1] - device1[timeCol].iloc[0]
