from django import forms
from .models import Watchlists
from crispy_forms.helper import FormHelper


class CatalogueWatchlistForm(forms.ModelForm):

    cones_textarea = forms.CharField(widget=forms.Textarea(attrs={'rows': 7, 'placeholder': 'Paste a source list. RA and Dec in decimal degrees, a unique source ID and an optional source-specific association radius in arcsec\n\nRA, Dec, ID <,radius>\nRA, Dec, ID <,radius>\n...'}))
    cones_file = forms.FileField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.fields['cones_textarea'].required = False
        self.fields['cones_file'].required = False

    class Meta:
        model = Watchlists
        widgets = {
            'name': forms.TextInput(attrs={'size': 80, 'placeholder': 'Make it memorable'}),
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'A detailed description of your watchlist. Remember to add a citation to the original data source.'}),
        }
        fields = ['name', 'description', 'active', 'public', 'radius', 'cones_textarea', 'cones_file']

    def clean(self):
        cleaned_data = super(CatalogueWatchlistForm, self).clean()
        conetext = cleaned_data.get("cones_textarea")
        conefile = cleaned_data.get("cones_file")
        if not conetext and not conefile and 1 == 0:
            raise forms.ValidationError("Please either paste your catalogue contents or upload a catalogue file.")

    def save(self, commit=True):
        # do something with self.cleaned_data['temp_id']
        return super(CatalogueWatchlistForm, self).save(commit=commit)


class UpdateCatalogueWatchlistForm(forms.ModelForm):

    class Meta:
        model = Watchlists
        widgets = {
            'name': forms.TextInput(attrs={'size': 80, 'placeholder': "asdasd"}),
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'A detailed description of your watchlist. Remember to add a citation to the original data source.'}),
            'public': forms.CheckboxInput(),
            'active': forms.CheckboxInput()
        }
        fields = ['name', 'description', 'active', 'public', 'radius']

    def __init__(self, *args, **kwargs):
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
