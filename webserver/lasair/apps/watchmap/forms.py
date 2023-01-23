from django import forms
from .models import Watchmap
from crispy_forms.helper import FormHelper


# ar_id = models.AutoField(primary_key=True)
#     user = models.ForeignKey(User, models.DO_NOTHING, db_column='user', blank=True, null=True)
#     name = models.CharField(max_length=256, blank=True, null=True)
#     description = models.TextField(max_length=4096, blank=True, null=True)
#     moc = models.TextField(blank=True, null=True)
#     mocimage = models.TextField(blank=True, null=True)
#     active = models.IntegerField(blank=True, null=True)
#     public = models.IntegerField(blank=True, null=True)
#     timestamp = models.DateTimeField(auto_now=True, editable=False, blank=True, null=True)
#     date_created = models.DateTimeField(auto_now=True, editable=False, blank=True, null=True)
#     date_modified = models.DateTimeField(auto_now=True, editable=False, blank=True, null=True)

class WatchmapForm(forms.ModelForm):

    watchmap_file = forms.FileField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.fields['watchmap_file'].required = True

    class Meta:
        model = Watchmap
        widgets = {
            'name': forms.TextInput(attrs={'size': 80, 'placeholder': 'Make it memorable'}),
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'A detailed description of your watchmap.'}),
        }
        fields = ['name', 'description', 'active', 'public', 'watchmap_file']

    def clean(self):
        cleaned_data = super(WatchmapForm, self).clean()

    def save(self, commit=True):
        # do something with self.cleaned_data['temp_id']
        return super(WatchmapForm, self).save(commit=commit)


class UpdateWatchmapForm(forms.ModelForm):

    class Meta:
        model = Watchmap
        widgets = {
            'name': forms.TextInput(attrs={'size': 80, 'placeholder': 'Make it memorable'}),
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'A detailed description of your watchmap.'}),
            'public': forms.CheckboxInput(),
            'active': forms.CheckboxInput()
        }
        fields = ['name', 'description', 'active', 'public']

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
