from django import forms
from django.contrib import admin


class MyqueriesModelForm(forms.ModelForm):
    description = forms.CharField(widget=forms.Textarea)
    selected = forms.CharField(widget=forms.Textarea)
    conditions = forms.CharField(widget=forms.Textarea)
    real_sql = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = Myqueries
        fields = '__all__'


class Myqueries_Admin(admin.ModelAdmin):
    form = MyqueriesModelForm
