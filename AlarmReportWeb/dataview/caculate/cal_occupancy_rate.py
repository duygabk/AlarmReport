import pandas as pd
import numpy as np
from datetime import datetime
# from readLog import caculate_performance
from .const import sourceCol, timeCol, messageCol, severityCol, dateCol, alarmFileHead, _short_stop_time_, _machine_list_

def alarm_seperate_by_machine(logs):

    logMachine = {}  # { "machine name": DataFrame { "Event time": ..., "Message": .... } }

    #get machine name from Original source
    nameHaveDot = list(set([name for name in logs[sourceCol] if '.' in name]))
    # print(list(set(nameHaveDot)))
    nameList = [name[:name.index('.')] for name in nameHaveDot] # eg BLD.BL3110RUN -> get BLD

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

def caculate_stop_time(logOneMachine, machine):

    stopTime = pd.Timedelta(0)
    # Add 23/4/2022
    # Count short stop time
    shortStopCount = 0
    totalStopCount = 0

    #Filter by Severity 300 RUN/STOP messages
    severity300 = logOneMachine[logOneMachine[severityCol] == 300]

    stopIndexs = np.where(severity300[messageCol].str.endswith("STOP") == True) #tuple
    # STOP message index list
    stopIndexs = list(stopIndexs[0])

    # remove adjacent number
    removeList = [ x for x in stopIndexs if x - 1 in stopIndexs ]
    stopIndexs = [ x for x in stopIndexs if x not in removeList ]

    # From STOP --> RUN is one time Machine Stop, ==> find RUN message
    logLen = len(severity300)
    ## To show detail info
    # [dataStopTime, dataStopMessage, dataRunTime, dataRunMessage] = [[], [], [], []]
    # Get Short Stop detail info
    ss_from_stop, ss_to_start, ss_count = 0, 0, 0
    ss_detail_dict = {'times': [], 'from STOP': [], 'to RUN': []}
    for x in stopIndexs:
        if x >= (logLen - 1):
            break
        findRun = x + 1
        endLoop = False
        while severity300.iloc[findRun][messageCol].endswith("RUN") == False:
            if findRun < (logLen - 1):
                findRun = findRun + 1
            elif findRun >= (logLen - 1):
                endLoop = True
                break
        ## To show detail info    
        # dataStopTime.append(severity300.iloc[x][timeCol])
        # dataStopMessage.append(severity300.iloc[x][messageCol])
        # calulate delta time
        if findRun >= stopIndexs[-1] and severity300.iloc[findRun][messageCol].endswith("RUN") == False:
            deltaT = logOneMachine.iloc[-1][timeCol] - severity300.iloc[x][timeCol]
            # To show detail info
            # dataRunTime.append(logOneMachine.iloc[-1][timeCol])
            # dataRunMessage.append(logOneMachine.iloc[-1][messageCol])
        else:
            deltaT = severity300.iloc[findRun][timeCol] - severity300.iloc[x][timeCol]
            ## To show Detail info
            # dataRunTime.append(severity300.iloc[findRun][timeCol])
            # dataRunMessage.append(severity300.iloc[findRun][messageCol])

        stopTime += deltaT
        # add 23/04/2022 --> short stop counter
        totalStopCount += 1
        # only machine of finishing line
        if machine in _machine_list_:
            if deltaT <= _short_stop_time_: 
                shortStopCount += 1
                ss_from_stop = pd.to_datetime(severity300.iloc[x][timeCol]).time().strftime("%H:%M:%S")
                ss_to_start = pd.to_datetime(severity300.iloc[findRun][timeCol]).time().strftime("%H:%M:%S")
                ss_detail_dict['times'].append(shortStopCount)
                ss_detail_dict['from STOP'].append(ss_from_stop)
                ss_detail_dict['to RUN'].append(ss_to_start)
        
        #End of the alarm report, finish
        if endLoop == True:
            break

    operatedTime = logOneMachine.iloc[-1][timeCol] - logOneMachine.iloc[0][timeCol]
    
    #div by zero error
    if operatedTime == pd.Timedelta(0):
        return 0, 0

    oneDay = pd.Timedelta("1 days")

    runTime = operatedTime - stopTime

    if stopTime == pd.Timedelta(0):
        performance = operatedTime/oneDay
    else:
        performance = runTime/oneDay
    # print(operatedTime.total_seconds(), stopTime.total_seconds(), performance)
    performance = round(performance, 3)

    #debug
    # if machine in _machine_list_:
    #     print(ss_detail_dict)
    ss_summary_dict = {
        'ss_count': shortStopCount,
        'total': totalStopCount,
        'detail': ss_detail_dict
    }
    # return tuple contain machine performance and short stop detail time dict, total stop counter
    return performance, ss_summary_dict

def summary_performace_by_day(filePath):

    performanceSumDict = {}
    shortTimeStopDict = {}

    logs = pd.read_excel(filePath, skiprows=3)
    #remove rows include N/A values
    logs.dropna(axis=0, thresh=3, inplace=True)

    #remove cols include N/A values
    logs.dropna(axis=1, thresh=3, inplace=True)

    # alarm report date
    alarmDate = logs[timeCol].median().date()
    performanceSumDict["Date"] = shortTimeStopDict["Date"] = [alarmDate]

    #alarm seperate by machine, and return machine name list
    logAllMachine, nameAllMachine = alarm_seperate_by_machine(logs)
    # print(logAllMachine)
    # Save machine name to file txt
    # with open(os.getcwd() + '/dataview/caculate/machine_name.txt', 'w') as f:
    #     f.writelines('\n'.join(nameAllMachine))

    for name in nameAllMachine:
        # print(name)
        perform, ss_summary_dict = caculate_stop_time(logAllMachine[name], machine = name)
        performanceSumDict[name] = [perform]
        if name in _machine_list_:
            shortTimeStopDict[name] = [ss_summary_dict]
    # Return 2 dict as {'Date': [2022-04-11], 'M1601': [0.85], 'M2601': [0.3] ...}
    # and short time stop dict {'Date': [2022-04-11], 'M1601': [5], 'M2601': [25] ...}
    # print('summary by day function: ', performanceSumDict)
    return performanceSumDict, shortTimeStopDict

# Check Alarm File name --> Incorrect return Error Message
def check_file_name(filePaths, headText = alarmFileHead ):

    alarmFilesFiltered = [f for f in filePaths if str(f).startswith(headText) == True]

    if len(alarmFilesFiltered) == 0:
        return {
            'error': True,
            'message': 'Invalid Required File Name!!!'
        }

    return {
        'error': False,
        'message': 'No Error',
        'files': alarmFilesFiltered
    }
