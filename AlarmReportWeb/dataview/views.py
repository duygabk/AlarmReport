from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .forms import NameForm, FileForm
import pandas as pd

# Create your views here.
def index(request):
    # return HttpResponse("DataView Page")
    return render(request, 'pages/index.html')

def chart(request):
    # return HttpResponse("Chart")
    return render(request, 'pages/chart.html', context={"aaa": 10000})

def loaddata(request):
    if request.method == 'POST':
        # bind data to form
        form = FileForm(request.POST, request.FILES)
        alarmFile = request.FILES['alarmFiles']
        #test read alarm file and represent into table
        alarmDF = pd.read_excel(alarmFile, skiprows=3)
        alarmDF.dropna(axis=1, inplace=True)
        print(alarmDF.head())
        cols = alarmDF.columns
        for x in cols: print(x)
        return render(request, 'pages/loaddata.html', {'data': alarmDF.head(10)})
    else:
        form = FileForm()
    return render(request, 'pages/loaddata.html', {'form': form})

def get_name(request):
    if request.method == 'POST':
        form = NameForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data
            print(name)
            return HttpResponse("name")
    else:
        form = NameForm()
    return render(request, 'dataview/name.html', { 'form': form })