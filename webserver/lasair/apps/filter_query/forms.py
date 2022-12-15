from django import forms
from .models import filter_query
from crispy_forms.helper import FormHelper
from src import db_connect
from lasair.apps.annotator.models import Annotators
from lasair.apps.watchmap.models import Watchmap
from lasair.apps.watchlist.models import Watchlist
from django.db.models import Q


class filterQueryForm(forms.ModelForm):

    msl = db_connect.readonly()
    cursor = msl.cursor(buffered=True, dictionary=True)
    watchlists = forms.ChoiceField(widget=forms.Select)
    watchmaps = forms.ChoiceField(widget=forms.Select)
    annotators = forms.ChoiceField(widget=forms.Select)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        if self.request.user.is_authenticated:
            email = self.request.user.email
            watchlists = Watchlist.objects.filter(Q(user=self.request.user) | Q(public__gte=1))
            watchmaps = Watchmap.objects.filter(Q(user=self.request.user) | Q(public__gte=1))
            annotators = Annotators.objects.filter(Q(user=self.request.user) | Q(public__gte=1))
        else:
            email = ''
            watchlists = Watchlist.objects.filter(public__gte=1)
            watchmaps = Watchmap.objects.filter(public__gte=1)
            annotators = Annotators.objects.filter(public__gte=1)

        # ADD WATCHLIST SELECTION TO THE FORM
        watchlistTypes, watchlistTypes2 = [], []
        if self.request.user.is_authenticated:
            watchlistTypes[:] = [(w.wl_id, w.name + f" ({w.user})") for w in watchlists if w.user.id == self.request.user.id]
        watchlistTypes2[:] = [(w.wl_id, w.name + f" ({w.user})") for w in watchlists if w.user.id != self.request.user.id]
        watchlistTypes = [(None, "Select a Watchlist    ")] + watchlistTypes + watchlistTypes2
        self.fields['watchlists'].required = False
        self.fields['watchlists'].choices = watchlistTypes
        self.fields['watchlists'].widget.choices = watchlistTypes

        # ADD WATCHMAP SELECTION TO THE FORM
        watchmapTypes, watchmapTypes2 = [], []
        if self.request.user.is_authenticated:
            watchmapTypes[:] = [(w.ar_id, w.name + f" ({w.user})") for w in watchmaps if w.user.id == self.request.user.id]
        watchlistTypes2[:] = [(w.ar_id, w.name + f" ({w.user})") for w in watchmaps if w.user.id != self.request.user.id]
        watchmapTypes = [(None, "Select a Watchmap    ")] + watchmapTypes + watchlistTypes2
        self.fields['watchmaps'].required = False
        self.fields['watchmaps'].choices = watchmapTypes
        self.fields['watchmaps'].widget.choices = watchmapTypes

        # ADD ANNOTATOR SELECTION TO THE FORM
        annotatorTypes, annotatorTypes2 = [], []
        if self.request.user.is_authenticated:
            annotatorTypes[:] = [(w.topic, w.topic + f" ({w.user})") for w in annotators if w.user.id == self.request.user.id]
        annotatorTypes2[:] = [(w.topic, w.topic + f" ({w.user})") for w in annotators if w.user.id != self.request.user.id]
        annotatorTypes = [(None, "Select an Annotator")] + annotatorTypes + annotatorTypes2
        self.fields['annotators'].required = False
        self.fields['annotators'].choices = annotatorTypes
        self.fields['annotators'].widget.choices = annotatorTypes

    class Meta:

        notificationTypes = (
            (0, 'muted'),
            (1, 'email stream (daily)'),
            (2, 'kafka stream')
        )
        model = filter_query
        widgets = {
            'name': forms.TextInput(attrs={'size': 80, 'placeholder': 'Make it memorable', 'required': 'true', 'value': "Make it memorable"}),
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'A detailed description of your watchlist. Remember to add a citation to the original data source.', 'required': 'true'}),
            'public': forms.CheckboxInput(),
            'selected': forms.Textarea(),
            'conditions': forms.Textarea(),
            'real_sql': forms.Textarea(),
            'active': forms.Select(choices=notificationTypes)
        }
        fields = ['name', 'description', 'active', 'public', 'selected', 'conditions', 'real_sql', 'watchlists', 'watchmaps']

    def clean(self):
        cleaned_data = super(filterQueryForm, self).clean()
        if self.request:
            action = self.request.POST.get('action')

    def save(self, commit=True):
        # do something with self.cleaned_data['temp_id']
        return super(filterQueryForm, self).save(commit=commit)


class UpdateFilterQueryForm(forms.ModelForm):

    class Meta:
        notificationTypes = (
            (0, 'muted'),
            (1, 'email stream (daily)'),
            (2, 'kafka stream')
        )
        model = filter_query
        widgets = {
            'name': forms.TextInput(attrs={'size': 80, 'placeholder': 'Make it memorable', 'required': 'true', 'value': "Make it memorable"}),
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'A detailed description of your watchlist. Remember to add a citation to the original data source.', 'required': 'true'}),
            'public': forms.CheckboxInput(),
            'selected': forms.Textarea(),
            'conditions': forms.Textarea(),
            'real_sql': forms.Textarea(),
            'active': forms.Select(choices=notificationTypes)
        }
        fields = ['name', 'description', 'active', 'public', 'selected', 'conditions', 'real_sql']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()

        instance = kwargs.get('instance', {})

        for i in self.fields:
            if i in ["public"]:
                if instance.__dict__[i]:
                    self.initial[i] = True
                else:
                    self.initial[i] = False
            else:
                self.fields[i].widget.attrs['value'] = instance.__dict__[i]
            # self.fields[i].initial = instance.__dict__[i]
