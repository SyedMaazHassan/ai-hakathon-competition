from django import forms
from .models import Job

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ["description"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 10, "placeholder": "Paste full job description here..."})
        }
