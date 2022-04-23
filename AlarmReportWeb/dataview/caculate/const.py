import os
import pandas as pd

timeCol = "Event time"
statusCol = "Status"
messageCol = "Message"
severityCol = "Severity"
sourceCol = "Original source"
machineCol = "Machine"
unknownCol = "What"
alarmFolder = './AlarmFiles/'
outputFolder = './OutputFiles/'
yeildFolder = './YeildFiles/'

# Summary output file path
_performanceSummaryFilePath_ = os.getcwd() + "/dataview/outputs/performance_summary.xlsx"
dateCol = 'Date'
m1601Col = "M1601"
m2601Col = "M2601"
m3601Col = "M3601"
ma1605Col = "MA1605"
ma2605Col = "MA2605"
_ymFilePath_ = os.getcwd() + "/dataview/outputs/ym_summary.xlsx"

# FileName check
alarmFileHead = "Denka Alarm Daily Report"

# Short stop time
_short_stop_time_ = pd.Timedelta(minutes = 10)
_shortStopTimeFilePath_ = os.getcwd() + "/dataview/outputs/short_stop_summary.xlsx"

# file path map dict
_file_path_map = {
    'performance': _performanceSummaryFilePath_,
    'yieldmonth': _ymFilePath_,
    'shortstop': _shortStopTimeFilePath_ 
}