from django.forms import ModelForm

from expressways.core.models import OccurrenceConfiguration, SubOccurrence


class OccurrenceConfigurationForm(ModelForm):
    class Meta:
        model = OccurrenceConfiguration
        exclude = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['sub_occurrence'].queryset = SubOccurrence.objects.none()

        if 'occurrence' in self.data:
            try:
                occurrence_id = int(self.data.get('occurrence')) 
                self.field['sub_occurrence'].queryset = SubOccurrence.objects.filter(occurrence_id=occurrence_id).order_by('name') 
            except (ValueError, TypeError):
                pass # invalid input; fallback to empty suboccurrence queryset
        elif self.instance.pk:
            self.fields['sub_occurrence'].queryset = self.instance.occurrence.sub_occurrences.order_by('name')  
