
from django import forms


#load file Form
class FileForm(forms.Form):
    alarmFiles = forms.FileField(label="Select AlarmReport File", max_length=200)
    dateSelect = forms.Select(attrs=[1,2,3], choices=[1,2,3])

