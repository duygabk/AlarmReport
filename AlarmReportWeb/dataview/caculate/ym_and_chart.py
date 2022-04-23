from typing import final
import pandas as pd
import openpyxl
import os
import seaborn as sns
import matplotlib.pyplot as plt
from scipy import stats
import json
from .const import dateCol, m1601Col, m2601Col, m3601Col, ma1605Col, ma2605Col, _ymFilePath_, _performanceSummaryFilePath_, _file_path_map

def save_one_day_data_to_excel(filePath = _performanceSummaryFilePath_, oneDayDataDict = {}):
    # print(filePath)
    #Create file if not exist
    if os.path.exists(filePath) == False:
        openpyxl.Workbook().save(filePath)
        dataDf = pd.DataFrame(oneDayDataDict)
        dataDf.to_excel(filePath, index = False)
    else:
        try:
            #read performance summary Dataframe
            summaryDf = pd.read_excel(filePath)
            # filter by Date
            #convert datetime column to just date
            summaryDf[dateCol] = pd.to_datetime(summaryDf[dateCol]).dt.date

            # print( oneDayDataDict[dateCol][0] in list(summaryDf[dateCol]) )
            if oneDayDataDict[dateCol][0] in list(summaryDf[dateCol]):
                summaryDf.drop(summaryDf[summaryDf[dateCol] == oneDayDataDict[dateCol][0]].index, inplace=True)
            summaryDf = pd.concat([summaryDf, pd.DataFrame(oneDayDataDict)])
            summaryDf.sort_values(by = dateCol, inplace = True)
            summaryDf.fillna(0, inplace = True)
            summaryDf.to_excel(filePath, index = False)
        except Exception as e:
            print(e)
            return False
        finally:
            # print('Write Performance to Excel OK')
            return True

# def load_performance_to_view(filePath = _performanceSummaryFilePath_, from_to_date={'fromDate':'', 'toDate': ''}):
#     # print(filePath)
#     summaryDf = pd.read_excel(filePath)
#     summaryDf[dateCol] = pd.to_datetime(summaryDf[dateCol]).dt.date

#     # filter by from_to_date
#     fromDate = pd.to_datetime(from_to_date['fromDate']).date() if from_to_date['fromDate'] != '' else summaryDf.iloc[0][dateCol]

#     toDate = pd.to_datetime(from_to_date['toDate']).date() if from_to_date['toDate'] != '' else summaryDf.iloc[-1][dateCol]

#     return summaryDf[summaryDf[dateCol] >= fromDate][summaryDf[dateCol] <= toDate]

def load_dataframe_to_view(type = 'performance', from_to_date={'fromDate':'', 'toDate': ''}):
    # print(filePath)
    filePath = _file_path_map[type]

    try:
        summaryDf = pd.read_excel(filePath)
    except Exception as e:
        print(e)
        return False

    summaryDf[dateCol] = pd.to_datetime(summaryDf[dateCol]).dt.date

    # filter by from_to_date
    fromDate = pd.to_datetime(from_to_date['fromDate']).date() if from_to_date['fromDate'] != '' else summaryDf.iloc[0][dateCol]

    toDate = pd.to_datetime(from_to_date['toDate']).date() if from_to_date['toDate'] != '' else summaryDf.iloc[-1][dateCol]

    return summaryDf[summaryDf[dateCol] >= fromDate][summaryDf[dateCol] <= toDate]

# Read Yeild Month File and return DataFrame
def read_ym_to_Df(filePath):
    ymDf = pd.read_excel(filePath, sheet_name = '4-2022')
    # Rename Columns as Machine Name
    ymDf.rename(columns={'YM1601': m1601Col, 'YM1605': ma1605Col, 'YM2601': m2601Col, 'YM2605': ma2605Col, 'YM3601': m3601Col}, inplace = True)
    # ymDf.columns = [dateCol, m1601Col, ma1605Col, m2601Col, ma2605Col, m3601Col]
    # print(ymDf, ymDf.columns)
    ymDf.dropna(axis=0, thresh=4, inplace=True)
    ymDf.dropna(axis=1, thresh=3, inplace=True)

    return ymDf

# Save Yeild Month to Excel File as DataBase
def save_ym_to_excel(ymDf):
    ymDf[dateCol] = pd.to_datetime(ymDf[dateCol]).dt.date
    ymDf.sort_values(by = dateCol, inplace = True)
    ymDf.to_excel(_ymFilePath_, index = False)
    return

def load_ym_to_view(filePath = _ymFilePath_, from_to_date = {'fromDate': '', 'toDate': ''}):
    ymDf = pd.read_excel(filePath)
    ymDf[dateCol] = pd.to_datetime(ymDf[dateCol]).dt.date

    fromDate = pd.to_datetime(from_to_date['fromDate']).date() if from_to_date['fromDate'] != '' else ymDf.iloc[0][dateCol]
    toDate = pd.to_datetime(from_to_date['toDate']).date() if from_to_date['toDate'] != '' else ymDf.iloc[-1][dateCol]

    return ymDf[ymDf[dateCol] >= fromDate][ymDf[dateCol] <= toDate]

def get_machine_list_to_show():
    machine_list = list(load_ym_to_view().columns)[1:]
    # print('get machine list', machine_list)
    return machine_list

# Mapping Machine performance and Yeild Month by Date
# 15/04 --> add filter from-to date
# Return DataFrame
def map_performance_ym_by_date(selectedMachine = [], from_to_date = {'fromDate': '', 'toDate': ''}):
    
    # filter from_to_date
    performanceDf = load_dataframe_to_view(type='performance', from_to_date = from_to_date)
    # ymDf = load_ym_to_view()
    ymDf = load_dataframe_to_view(type='yieldmonth', from_to_date = from_to_date)
    # machineList = list(ymDf.columns)[1:]
    # print(machineList)

    sameDateList = [d for d in performanceDf[dateCol].to_list() if d in ymDf[dateCol].to_list() ]
    # print(sameDateList)
    performanceData = []
    ymData = []
    for x in sameDateList:
        performanceData.append(
            performanceDf[performanceDf[dateCol] == x]
        )
        ymData.append(
            ymDf[ymDf[dateCol] == x]
        )
    # filtered data put in dataframe
    pfChartDataDf = pd.concat(performanceData, ignore_index = True)
    pfChartDataDf = pfChartDataDf[list(ymDf.columns)]
    ymChartDataDf = pd.concat(ymData, ignore_index = True)
    # print(pfChartDataDf, ymChartDataDf)
    
    response = []
    for m in selectedMachine:
        # print(m)
        dataSet = pd.DataFrame({
            dateCol: sameDateList,
            'Performance': pfChartDataDf[m].to_list(),
            'YeildMonth': ymChartDataDf[m].to_list()
        })
        # print(dataSet)
        response.append({
            'machine': m,
            'mapDf': dataSet
        })
        imgPath = os.getcwd() + '/static/chart/' + m + '.png'
        # draw regression line
        sns.set_style('whitegrid')
        sns.lmplot(x ='Performance', y ='YeildMonth', data = dataSet)
        # plt1 = plt.figure(figsize=(4, 4))
        plt.title(m)
        plt.savefig(imgPath)
        # plt.show()
    # Return list of DataFrame {'Date': [...], 'Performance': [...], 'YeildMonth': [...]}
    return response

# print chart by Highcharts js
def load_data_for_chart_v2_by_machine_date(machine, from_to_date):
    chartDataDf = map_performance_ym_by_date(selectedMachine = [machine], from_to_date = from_to_date)[0]['mapDf']
    
    xAxis_pf = chartDataDf['Performance'].to_list()
    yAxis_ym = chartDataDf['YeildMonth'].to_list()
    # print(xAxis_pf)
    scraterData = [[xAxis_pf[i], yAxis_ym[i]] for i in range(len(xAxis_pf))]
    # Regression line
    slope, intercept, r, p, std_err = stats.linregress(x=xAxis_pf, y=yAxis_ym)

    def myfunc(x):
        return slope * x + intercept
    
    x_min = min(xAxis_pf)
    x_max = max(xAxis_pf)

    regressionData = [[0, myfunc(x_min)], [x_max, myfunc(x_max)]]

    return regressionData, scraterData

# print base line chart by Highcharts js
# return dict {'Date': [,,,], 'M1601': [0.3, 0.5....]}
def load_line_chart_data_filter_by_date(machineList, from_to_date):
    # Get machine performance filter by date
    performDf = load_dataframe_to_view(type='performance', from_to_date = from_to_date)
    # Get require columns --> Data||M1601||MA1605....
    # getColumns = machineList.copy() # copy list values
    machineListCopy = list(machineList) # create copy of origin list
    # machineListCopy.insert(0, dateCol)

    # response = performDf.to_dict('split')
    response = {}
    for col in machineListCopy:
        response[col] = performDf[col].to_list()
    response[dateCol] = performDf[dateCol].astype(str).to_list()

    # return json format
    res_json = json.dumps(response)
    # print(res_json, type(res_json))
    return res_json