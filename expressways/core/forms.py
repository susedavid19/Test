from django.forms import ModelForm

from expressways.core.models import OccurrenceConfiguration


class OccurrenceConfigurationForm(ModelForm):
    class Meta:
        model = OccurrenceConfiguration
        exclude = []
