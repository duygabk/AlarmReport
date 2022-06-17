import json
import os
import mimetypes
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .forms import FileForm, YmFileForm
import pandas as pd
from datetime import date, datetime
# utils modules
from .caculate.cal_occupancy_rate import check_file_name, summary_performace_by_day
from .caculate.convert import convert_df_to_table
from .caculate.ym_and_chart import get_machine_list_to_show, load_data_for_chart_v2_by_machine_date, load_dataframe_to_view, load_chart_data_filter_by_date, read_ym_to_Df, save_ym_to_excel, save_one_day_data_to_excel, map_performance_ym_by_date
from .caculate.const import PERFORMANCE, SHORTSTOP, _shortStopTimeFilePath_, _performanceSummaryFilePath_, ymFileHead

# For Download Excel File
download_dataframe = pd.DataFrame()

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
    global download_dataframe
    machineList = get_machine_list_to_show()
    selectM = machineList[0]
    chartType = 'line'
    # get data from 1st of current month
    from_to_date = {
        'fromDate': datetime.now().strftime("%Y-%m") + '-01',
        'toDate': ''
    }
    if request.method == 'POST':
        selectM = request.POST['machine']
        chartType = request.POST['chart_type']
        from_to_date['fromDate'] = request.POST['from_date']
        from_to_date['toDate'] = request.POST['to_date']
        print(selectM, chartType, from_to_date)

    # Regression Line Data
    chartData = {'regression': [], 'scratter': []}
    table = {}
    chart_data = ''
    if chartType == 'regression':
        chartData['regression'], chartData['scratter'] = load_data_for_chart_v2_by_machine_date(machine = selectM, from_to_date = from_to_date)
        # Regression Line Map table (DataFrame)
        map_table = map_performance_ym_by_date(selectedMachine=[selectM], from_to_date = from_to_date)[0]['mapDf']
        # for download function
        download_dataframe = map_table
        table = convert_df_to_table(map_table)
        # print(table)
    else:
        # chart_data json format "Date": [], "M1601": [].....
        chart_data = load_chart_data_filter_by_date(type = PERFORMANCE if chartType == 'line' else SHORTSTOP, machineList = machineList, from_to_date = from_to_date)
        download_dataframe = pd.DataFrame(json.loads(chart_data))

    # print(chartData)

    context = {
        'regression': chartData['regression'],
        'scratter': chartData['scratter'],
        'table': table,
        'machines': machineList,
        'select': selectM,
        'chart_type': chartType,
        'from_to_date': from_to_date,
        'chart_data': chart_data,
    }
    return render(request, 'pages/chart_v2.html', context)

#Short Stop Chart detail
def chart_detail(request):
    return render(request, 'pages/chart_detail.html')
    
def get_ss_detail(request):
    print('get ss chart detail')
    return HttpResponseRedirect('/dataview/chart_v2/chart_detail/')
    return render(request, template_name='pages/chart_detail.html')

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

        # Check file name
        checkFileName = check_file_name(filePaths=[ymFile], headText = ymFileHead)
        if checkFileName['error']:
            return render(request, 'pages/error.html', { 'message': checkFileName['message'], 'from': 'yeildmonth' })
            
        ymFile = checkFileName['files'][0]
        # Check Read Ym Error
        readData = read_ym_to_Df(ymFile)
        if readData['error']:
            return render(request, 'pages/error.html', { 'message': readData['message'], 'from': 'yeildmonth' })

        ymDf = readData['data']
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
def load_data(request):
    return render(request=request, template_name='pages/load_data.html')

# show summary of machine occupancy rate
def get_summary(request):
    # By default, print performance
    global download_dataframe
    select = 'performance'
    from_to_date = {
        'fromDate': datetime.now().strftime("%Y-%m") + '-01',
        'toDate': ''
    }
    if request.method == 'POST':
        select = request.POST['summarySelect']
        from_to_date['fromDate'] = request.POST['from_date']
        from_to_date['toDate'] = request.POST['to_date']
    
    summaryDf = load_dataframe_to_view(type=select, from_to_date = from_to_date)

    # Read file Error
    if (isinstance(summaryDf, bool)):
        return render(request, 'pages/error.html', {'message': 'LOAD FILE ERROR', 'from': 'summary'})

    # for download feature
    download_dataframe = summaryDf
    # convert to table to view
    table = convert_df_to_table(summaryDf)

    # print(table)
    return render(request, 'pages/summary.html', {'table': table, 'select': select, 'from_to_date': from_to_date})

# Delete data by date
def delete_performance(request):
    dateStr = request.GET.get('date')
    print(dateStr)
    return HttpResponseRedirect('/dataview/summary/')

# download excel file handler
def download_excel(request):
    # Get param
    # req = json.loads(request.body.decode("utf-8"))
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    filename = 'book1.xlsx'
    filepath = BASE_DIR + '/static/' + filename

    # Export data to excel file
    print(download_dataframe)
    download_dataframe.to_excel(filepath, index=False)

    # Open the file for reading content
    path = open(filepath, 'rb')
    # Set the mime type
    mime_type, _ = mimetypes.guess_type(filepath)
    # Set the return value of the HttpResponse
    response = HttpResponse(path, content_type=mime_type)
    # Set the HTTP header for sending to browser
    response['Content-Disposition'] = "attachment; filename=%s" % filename
    # Return the response value
    return response
