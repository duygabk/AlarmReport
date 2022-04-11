from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from matplotlib.style import context
from .forms import FileForm, YmFileForm
import pandas as pd
# utils modules
from .caculate.cal_occupancy_rate import summary_performace_by_day
from .caculate.convert import convert_df_to_table
from .caculate.ym_and_chart import get_machine_list_to_show, load_performance_to_view,load_ym_to_view ,read_ym_to_Df, save_ym_to_excel, save_performance_to_excel, map_performance_ym_by_date
# Create your views here.
def index(request):
    # return HttpResponse("DataView Page")
    return render(request, 'pages/index.html')

def chart(request):
    selected = []
    if request.method == 'POST':
        selected = request.POST.getlist('machine')
        print(selected)
    # Get mapping by date from machine perfornamce and yeild month
    machineList = get_machine_list_to_show()
    mapList = map_performance_ym_by_date(selected)

    resultList = [] # list of dict {'machine': machineName, 'table': mapTable}
    if len(mapList):
        for m in mapList:
            table = convert_df_to_table(m['mapDf'])
            resultList.append({
                'machine': m['machine'],
                'table': table
            })
    # print(mapData)
    return render(request, 'pages/chart.html', context={"machine": machineList, "selected": selected, 'mapList': resultList})

def load_alarm_file(request):
    if request.method == 'POST':
        # bind data to form
        form = FileForm(request.POST, request.FILES)
        alarmFiles = request.FILES.getlist('alarmFiles')  
        # print(alarmFiles)
        tableList = []
        if len(alarmFiles):
            for f in alarmFiles:
                performanceDict = summary_performace_by_day(f) 
                # Save to database
                save_performance_to_excel( oneDayPerformance = performanceDict)
                #format date to display in html view
                # performanceDict["Date"][0] = performanceDict["Date"][0].strftime("%Y-%m-%d") # eg: 2022-03-30
                # table = convert_df_to_table(pd.DataFrame(performanceDict))
                tableList.append(pd.DataFrame(performanceDict))
                # print(table)
        # table = pd.concat(tableList, ignore_index = True)
        tableDf = pd.concat(tableList, ignore_index = True)
        tableDf.fillna(0, inplace = True)
        table = convert_df_to_table(tableDf)
        # print(tableList)
        context = {
            'form': False,
            'table': table
        }
        return render(request, 'pages/load_alarm_file.html', context)     
    else:
        form = FileForm()
    context = {
        'table': False,
        'form': form
    }
    return render(request, 'pages/load_alarm_file.html', context)


# load yeild month from excel file
def load_yeild_month(request):
    if request.method == 'POST':
        form = FileForm(request.POST, request.FILES)
        ymFile = request.FILES['yieldmonth']
        # aa = pd.read_excel(ymFile, sheet_name="4-2022")
        # print(aa)
        ymDf = read_ym_to_Df(ymFile)  
        save_ym_to_excel(ymDf)
        table = convert_df_to_table(ymDf)
        context = {
            'form': False,
            'table': table
        }
        return render(request, 'pages/yeildmonth.html', context)
    else:
        form = YmFileForm()
        context = {
            'form': form,
            'table': False
        }
        return render(request, 'pages/yeildmonth.html', context)

#############################################################################################################
# show summary of machine occupancy rate
def get_summary(request):
    # By default, print performance
    select = 'performance'
    if request.method == 'POST':
        select = request.POST['summarySelect']
        print(select)

    summaryDf = load_performance_to_view() if select == "performance" else load_ym_to_view()
    
    table = convert_df_to_table(summaryDf)

    # print(table)
    return render(request, 'pages/summary.html', {'table': table, 'select': select})
