from django import forms
from .models import Watchlists
from crispy_forms.helper import FormHelper


class CatalogueWatchlistForm(forms.ModelForm):

    cones_textarea = forms.Textarea()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()

    class Meta:
        model = Watchlists
        # name = forms.CharField()
        # description = forms.Textarea()

        # name.widget.attrs.update({'placeholder': 'Succinct description'})

        # fields = ['name', 'description', 'active', 'public', 'radius', 'cones_textarea']
        # widgets = {
        #     'name': forms.TextInput(attrs={'size': 80, 'placeholder': 'Make it memorable'}),
        #     'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'A more detailed description of your watchlist, preferably with a citation to the original catalogue source.'}),
        #     'cones_textarea': forms.Textarea(attrs={'rows': 3, 'placeholder': 'A more detailed description of your watchlist, preferably with a citation to the original catalogue source.'})
        # }
        fields = ['name', 'description', 'active', 'public', 'radius']

    def save(self, commit=True):
        # do something with self.cleaned_data['temp_id']
        return super(Watchlists, self).save(commit=commit)
