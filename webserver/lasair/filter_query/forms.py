from django import forms
from django.contrib import admin
from .models import filter_query


class filterQueryForm(forms.ModelForm):
    description = forms.CharField(widget=forms.Textarea)
    selected = forms.CharField(widget=forms.Textarea)
    conditions = forms.CharField(widget=forms.Textarea, required=False)
    real_sql = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = filter_query
        fields = '__all__'
