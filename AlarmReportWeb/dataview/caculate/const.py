import os
import pandas as pd

timeCol = "Event time"
statusCol = "Status"
messageCol = "Message"
severityCol = "Severity"
sourceCol = "Original source"

# Summary output file path
_performanceSummaryFilePath_ = os.getcwd() + "/dataview/outputs/performance_summary.xlsx"
dateCol = 'Date'
m1601Col = "M1601"
m2601Col = "M2601"
m3601Col = "M3601"
ma1605Col = "MA1605"
ma2605Col = "MA2605"
_ymFilePath_ = os.getcwd() + "/dataview/outputs/ym_summary.xlsx"

_machine_list_ = [m1601Col, m2601Col, m3601Col, ma1605Col, ma2605Col]

# FileName check
alarmFileHead = "Denka Alarm Daily Report"
ymFileHead = "YieldMonth_Finishing"

# Short stop time
_short_stop_time_ = pd.Timedelta(minutes = 10)
_shortStopTimeFilePath_ = os.getcwd() + "/dataview/outputs/short_stop_summary.xlsx"

# file path map dict
PERFORMANCE = 'performance'
YIELDMONTH = 'yieldmonth'
SHORTSTOP = 'shortstop'

_file_path_map = {
    PERFORMANCE: _performanceSummaryFilePath_,
    YIELDMONTH: _ymFilePath_,
    SHORTSTOP: _shortStopTimeFilePath_ 
}