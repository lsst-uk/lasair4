from django import forms
from .models import Watchmap
from crispy_forms.helper import FormHelper
from django.db.models import Q


class WatchmapForm(forms.ModelForm):

    watchmap_file = forms.FileField()

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.fields['watchmap_file'].required = True

    class Meta:
        model = Watchmap
        widgets = {
            'name': forms.TextInput(attrs={'size': 80, 'placeholder': 'Make it memorable', 'required': True}),
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'A detailed description of your watchmap.', 'required': True}),
            'public': forms.CheckboxInput(),
            'active': forms.CheckboxInput()
        }
        fields = ['name', 'description', 'active', 'public', 'watchmap_file']

    def clean(self):
        cleaned_data = super(WatchmapForm, self).clean()

        name = self.cleaned_data.get('name')
        if self.request:
            action = self.request.POST.get('action')

        if action == "save":
            if Watchmap.objects.filter(Q(user=self.request.user) & Q(name=name)).exists():
                msg = 'You already have a watchmap by that name, please choose another.'
                self.add_error('name', msg)

    def save(self, commit=True):
        # do something with self.cleaned_data['temp_id']
        return super(WatchmapForm, self).save(commit=commit)


class UpdateWatchmapForm(forms.ModelForm):

    class Meta:
        model = Watchmap
        widgets = {
            'name': forms.TextInput(attrs={'size': 80, 'placeholder': 'Make it memorable', 'required': True}),
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'A detailed description of your watchmap.', 'required': True}),
            'public': forms.CheckboxInput(),
            'active': forms.CheckboxInput()
        }
        fields = ['name', 'description', 'active', 'public']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()

        instance = kwargs.get('instance', {})

        for i in self.fields:
            # print(instance.__dict__[i])

            if i in ["public", "active"]:
                if instance.__dict__[i]:
                    self.initial[i] = True
                else:
                    self.initial[i] = False

            else:
                self.fields[i].widget.attrs['value'] = instance.__dict__[i]
            # self.fields[i].initial = instance.__dict__[i]
