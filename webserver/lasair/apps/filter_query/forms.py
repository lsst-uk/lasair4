from django import forms
from .models import filter_query
from crispy_forms.helper import FormHelper


class filterQueryForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()

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
            # print(instance.__dict__[i])

            if i in ["public", "active"]:
                if instance.__dict__[i]:
                    self.initial[i] = True
                else:
                    self.initial[i] = False

            else:
                self.fields[i].widget.attrs['value'] = instance.__dict__[i]
            # self.fields[i].initial = instance.__dict__[i]
