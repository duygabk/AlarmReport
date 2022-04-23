from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .forms import DateFilter, FileForm, YmFileForm
import pandas as pd
# utils modules
from .caculate.cal_occupancy_rate import check_file_name, filter_alarm_files, summary_performace_by_day
from .caculate.convert import convert_df_to_table
from .caculate.ym_and_chart import get_machine_list_to_show, load_data_for_chart_v2_by_machine_date, load_dataframe_to_view, load_line_chart_data_filter_by_date, read_ym_to_Df, save_ym_to_excel, save_one_day_data_to_excel, map_performance_ym_by_date
from .caculate.const import _shortStopTimeFilePath_, _performanceSummaryFilePath_
# Create your views here.
def index(request):
    # return HttpResponse("DataView Page")
    return render(request, 'pages/index.html')

def chart(request):
    selected = []
    from_to_date = {
        'fromDate': '',
        'toDate': ''
    }
    if request.method == 'POST':
        selected = request.POST.getlist('machine')
        # print(selected)
        from_to_date['fromDate'] = request.POST['from_date']
        from_to_date['toDate'] = request.POST['to_date']

    # filter from-to date
    # Get mapping by date from machine perfornamce and yeild month
    machineList = get_machine_list_to_show()
    mapList = map_performance_ym_by_date(selected, from_to_date = from_to_date)

    resultList = [] # list of dict {'machine': machineName, 'table': mapTable}
    if len(mapList):
        for m in mapList:
            table = convert_df_to_table(m['mapDf'])
            resultList.append({
                'machine': m['machine'],
                'table': table
            })
    # print(mapData)

    # dateForm = DateFilter()

    return render(request, 'pages/chart.html', context={"machine": machineList, "selected": selected, 'mapList': resultList, 'from_to_date': from_to_date})

def chart_v2(request):
    machineList = get_machine_list_to_show()
    selectM = machineList[0]
    chartType = 'line'
    from_to_date = {
        'fromDate': '',
        'toDate': ''
    }
    if request.method == 'POST':
        selectM = request.POST['machine']
        chartType = request.POST['chart_type']
        from_to_date['fromDate'] = request.POST['from_date']
        from_to_date['toDate'] = request.POST['to_date']
        print(selectM, chartType, from_to_date)

    # Regression Line Data
    chartData = {}
    chartData['regression'], chartData['scratter'] = load_data_for_chart_v2_by_machine_date(machine = selectM, from_to_date = from_to_date)
    # Regression Line Map table (DataFrame)
    map_table = map_performance_ym_by_date(selectedMachine=[selectM], from_to_date = from_to_date)[0]['mapDf']
    table = convert_df_to_table(map_table)
    # print(table)

    line_chart_data = load_line_chart_data_filter_by_date(machineList = machineList, from_to_date = from_to_date)

    # print(chartData)

    context = {
        'regression': chartData['regression'],
        'scratter': chartData['scratter'],
        'table': table,
        'machines': machineList,
        'select': selectM,
        'chart_type': chartType,
        'from_to_date': from_to_date,
        'line_chart_data': line_chart_data,
    }
    return render(request, 'pages/chart_v2.html', context)

def load_alarm_file(request):
    if request.method == 'POST':
        # bind data to form
        form = FileForm(request.POST, request.FILES)
        alarmFiles = request.FILES.getlist('alarmFiles')  
        
        # Check Alarm File Name --> Return list of alarm file only, if not return error
        checkFileName = check_file_name(alarmFiles)

        if checkFileName['error']:
            return render(request, 'pages/error.html', {'message': checkFileName['message'], 'from': 'loaddata'})

        print(checkFileName['files'])
        # print(alarmFiles)
        tableList = []
        if len(checkFileName['files']):
            for f in checkFileName['files']:
                performanceDict, shortTimeStopDict = summary_performace_by_day(f) 
                # Save to database
                if save_one_day_data_to_excel(filePath = _performanceSummaryFilePath_, oneDayDataDict = performanceDict) == False or save_one_day_data_to_excel(filePath=_shortStopTimeFilePath_, oneDayDataDict=shortTimeStopDict) == False:
                    return render(request, 'pages/error.html', {'message': 'Write to Excel Failed!!!', 'from': 'loaddata'})
                # table to view
                tableList.append(pd.DataFrame(performanceDict))

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
        form = YmFileForm(request.POST, request.FILES)
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
    from_to_date = {
        'fromDate': '',
        'toDate': ''
    }
    if request.method == 'POST':
        select = request.POST['summarySelect']
        from_to_date['fromDate'] = request.POST['from_date']
        from_to_date['toDate'] = request.POST['to_date']

    # summaryDf = load_performance_to_view(from_to_date = from_to_date) if select == "performance" else load_ym_to_view(from_to_date = from_to_date)
    summaryDf = load_dataframe_to_view(type=select, from_to_date = from_to_date)
    
    table = convert_df_to_table(summaryDf)

    # print(table)
    return render(request, 'pages/summary.html', {'table': table, 'select': select, 'from_to_date': from_to_date})

# Delete data by date
def delete_performance(request):
    dateStr = request.GET.get('date')
    print(dateStr)
    return HttpResponseRedirect('/dataview/summary/')
