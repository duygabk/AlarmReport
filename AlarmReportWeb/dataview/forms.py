
from django import forms


#load file Form
class FileForm(forms.Form):
    # alarmFiles = forms.FileField(label="Select AlarmReport File", max_length=200)
    # dateSelect = forms.Select(attrs=[1,2,3], choices=[1,2,3])
    alarmFiles = forms.FileField(label="Select Files", widget=forms.ClearableFileInput(attrs={'multiple': True}))

class YmFileForm(forms.Form):
    # No Label, No Multilpe
    yieldmonth = forms.FileField(max_length=200)

class DateFilter(forms.Form):
    date_from = forms.DateInput()
    date_to = forms.DateInput()