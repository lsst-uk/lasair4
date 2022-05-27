from django.contrib import admin
from lasair.models import Annotators, Myqueries, Areas, Watchlists

from django import forms
class MyqueriesModelForm( forms.ModelForm ):
    description = forms.CharField( widget=forms.Textarea )
    selected    = forms.CharField( widget=forms.Textarea )
    conditions  = forms.CharField( widget=forms.Textarea )
    real_sql    = forms.CharField( widget=forms.Textarea )
    class Meta:
        model = Myqueries
        fields = '__all__'

class Myqueries_Admin( admin.ModelAdmin ):
    form = MyqueriesModelForm

admin.site.register(Myqueries, Myqueries_Admin)
admin.site.register(Annotators)
admin.site.register(Areas)
admin.site.register(Watchlists)
