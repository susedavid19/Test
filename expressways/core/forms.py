from django.forms import Form, ModelForm, ModelChoiceField

from expressways.core.models import OccurrenceConfiguration, Occurrence, SubOccurrence, Road


class OccurrenceConfigurationForm(ModelForm):
    occurrence = ModelChoiceField(queryset=Occurrence.objects.all())

    class Meta:
        model = OccurrenceConfiguration
        exclude = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['sub_occurrence'].queryset = SubOccurrence.objects.none()

class RoadSelectionForm(Form):
    road = ModelChoiceField(queryset=Road.objects.all(), label='', empty_label=None)
