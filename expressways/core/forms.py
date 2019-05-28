from django.forms import Form, ModelChoiceField, ModelMultipleChoiceField
from django.forms.widgets import CheckboxSelectMultiple

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
