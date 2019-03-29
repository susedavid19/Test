from django.forms import ModelForm, ModelChoiceField

from expressways.core.models import OccurrenceConfiguration, Occurrence, SubOccurrence


class OccurrenceConfigurationForm(ModelForm):
    occurrence = ModelChoiceField(queryset=Occurrence.objects.all())

    class Meta:
        model = OccurrenceConfiguration
        exclude = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['sub_occurrence'].queryset = SubOccurrence.objects.none()
