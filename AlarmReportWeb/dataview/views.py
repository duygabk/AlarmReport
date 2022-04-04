from django.shortcuts import render
from django.http import HttpResponse


# Create your views here.
def index(request):
    # return HttpResponse("DataView Page")
    return render(request, 'dataview/index.html')

def chart(request):
    # return HttpResponse("Chart")
    return render(request, 'dataview/chart.html', context={"aaa": 10000})

def loaddata(request):
    file = request.FILES
    print(file)
    return HttpResponse(file)