import pandas as pd
import openpyxl
import os
import seaborn as sns
import matplotlib.pyplot as plt
from .const import dateCol, m1601Col, m2601Col, m3601Col, ma1605Col, ma2605Col, ymFilePath, summaryFilePath

def save_performance_to_excel(filePath = summaryFilePath,oneDayPerformance = {}):
    # print(filePath)
    #Create file if not exist
    if os.path.exists(filePath) == False:
        openpyxl.Workbook().save(filePath)
        dataDf = pd.DataFrame(oneDayPerformance)
        dataDf.to_excel(filePath, index = False)    
    else:
        #read performance summary Dataframe
        summaryDf = pd.read_excel(filePath)
        # filter by Date
        #convert datetime column to just date
        summaryDf[dateCol] = pd.to_datetime(summaryDf[dateCol]).dt.date

        print( oneDayPerformance[dateCol][0] in list(summaryDf[dateCol]) )
        if oneDayPerformance[dateCol][0] in list(summaryDf[dateCol]):
            summaryDf.drop(summaryDf[summaryDf[dateCol] == oneDayPerformance[dateCol][0]].index, inplace=True)
        summaryDf = pd.concat([summaryDf, pd.DataFrame(oneDayPerformance)])
        summaryDf.sort_values(by = dateCol, inplace = True)
        summaryDf.fillna(0, inplace = True)
        summaryDf.to_excel(filePath, index = False)

        return

def load_performance_to_view(filePath = summaryFilePath):
    # print(filePath)
    summaryDf = pd.read_excel(filePath)
    summaryDf[dateCol] = pd.to_datetime(summaryDf[dateCol]).dt.date
    # summaryDict = summaryDf.to_dict('list')
    #    
    # return as DataFrame
    return summaryDf

# Read Yeild Month File and return DataFrame
def read_ym_to_Df(filePath):
    ymDf = pd.read_excel(filePath, sheet_name = '4-2022')
    # Rename Columns as Machine Name
    ymDf.columns = [dateCol, m3601Col, ma1605Col, ma2605Col, m1601Col, m2601Col ]
    # print(ymDf, ymDf.columns)
    ymDf.dropna(axis=0, thresh=4, inplace=True)
    ymDf.dropna(axis=1, thresh=3, inplace=True)

    # print(ymDf)

    return ymDf

# Save Yeild Month to Excel File as DataBase
def save_ym_to_excel(ymDf):
    ymDf[dateCol] = pd.to_datetime(ymDf[dateCol]).dt.date
    ymDf.sort_values(by = dateCol, inplace = True)
    ymDf.to_excel(ymFilePath, index = False)
    return

def load_ym_to_view(filePath = ymFilePath):
    ymDf = pd.read_excel(filePath)
    ymDf[dateCol] = pd.to_datetime(ymDf[dateCol]).dt.date
    return ymDf

def get_machine_list_to_show():
    return list(load_ym_to_view().columns)[1:]

# Mapping Machine performance and Yeild Month by Date
def map_performance_ym_by_date(selectedMachine = []):
    
    performanceDf = load_performance_to_view()
    ymDf = load_ym_to_view()
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

    return response