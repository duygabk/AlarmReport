import numpy as np
import os
import openpyxl
from pyecharts import options as opts
from pyecharts.charts import Bar
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from const import outputFolder, yeildFolder

#month machine performance summary file
performFileName = 'Performance Of Machine 3-2022.xlsx'
sheetName = '03.2022'

#month yield summary file
yeildFileName = 'YieldMonth_Finishing.xlsx'
yeildSheet = "3-2022"

# to test Bar chart, need return to 2 list: date and performance
def read_performance():
    performanceDf = pd.read_excel(
        io = outputFolder + performFileName,
    )

    return performanceDf
    # print(performanceDf.info())
    days = performanceDf["Date"].tolist()
    # print(type(days[0]))

    # remove Date column
    performanceDf.drop(["Date"], axis = 1, inplace = True)
    machineName = performanceDf.columns.tolist()

    print(
        days,
        machineName
    )
    barChart = (
        Bar()
        .add_xaxis(days)
        .set_global_opts(
            title_opts=opts.TitleOpts(title="Demo Chart", subtitle="SubTilte Demo")
        )
    )
    for m in machineName:
        barChart.add_yaxis(m, performanceDf[m].tolist())
    barChart.render()

def read_yeild():
    yeildDf = pd.read_excel(yeildFolder + yeildFileName, sheet_name=yeildSheet)
    yeildDf.fillna(0, inplace=True)
    # cols = yeildDf.columns.tolist()
    # print(yeildDf, cols)
    return yeildDf

def performance_yield_by_machine(machineName):
    performDf = read_performance()
    yieldDf = read_yeild()
    dateCol = "Date"
    # print(performDf[dateCol])
    # print(yieldDf[dateCol])

    sameDate = [x for x in performDf[dateCol].tolist() if x in yieldDf[dateCol].tolist()]

    performData = []
    yieldData = []
    for x in sameDate:
        performData.append(
            performDf[performDf[dateCol] == x]
        )
        yieldData.append(
            yieldDf[yieldDf[dateCol] == x]
        )
    # filtered data put in dataframe
    performDataDf = pd.concat(performData, ignore_index = True)
    yieldDataDf = pd.concat(yieldData, ignore_index = True)
    # print(performDataDf,yieldDataDf)

    #draw linear regression using seaborn
    x = performDataDf[machineName]
    y = yieldDataDf[machineName]

    if len(x) != len(y):
        print("Error Occurred!!!! Repair you code or input file")
        return
    
    dataSet = pd.DataFrame({
        "Date": [x.date() for x in sameDate],
        "Performance": x,
        "Yield": y
    })

    #save to excel file
    filePath = outputFolder + "DrawChart.xlsx"
    #create new file if not exist
    if os.path.exists(filePath) == False:
        openpyxl.Workbook().save(filePath)
    with pd.ExcelWriter(path=filePath, mode='a', if_sheet_exists = 'replace') as f:
        dataSet.to_excel(f, sheet_name=machineName, index=False)

    # sns.set(title = machineName)
    sns.set_style('whitegrid')
    sns.lmplot(x ='Performance', y ='Yield', data = dataSet)
    plt.title(machineName)
    plt.savefig(machineName + '.png')
    plt.show()
    
    # print(dataSet.head())

    # sns.regplot(x="Yield", y="Performance", data=dataDf)
    

performance_yield_by_machine("MA1605")
# read_performance()