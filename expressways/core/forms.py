from django.forms import Form, ModelChoiceField, ModelMultipleChoiceField, ValidationError
from django.forms.widgets import CheckboxSelectMultiple
from django.utils.translation import ugettext_lazy as _

from expressways.core.models import Road, DesignComponent


class RoadSelectionForm(Form):
    road = ModelChoiceField(
        queryset=Road.objects.all(), 
        label='', 
        empty_label=None
    )

class InterventionForm(Form):   
    design_components = ModelMultipleChoiceField(
        queryset=DesignComponent.objects.all(),
        widget=CheckboxSelectMultiple(attrs={'class': 'custom-control-input'}),
        required=False
    )

    def clean_design_components(self):
        data = self.cleaned_data['design_components']
        vms = DesignComponent.objects.get(pk=4) # for VMS design component
        tos = DesignComponent.objects.get(pk=3) # for Traffic Officer design component
        if vms in data and tos not in data:
            raise ValidationError(
                _(f'{vms.name} has to be selected together with {tos.name}'),
                code='invalid'
            )
        return data
                