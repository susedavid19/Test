from django.forms import Form, ModelChoiceField
from django.forms.widgets import CheckboxSelectMultiple

from expressways.core.models import Road, DesignComponent


class RoadSelectionForm(Form):
    road = ModelChoiceField(
        queryset=Road.objects.all(), 
        label='', 
        empty_label=None
    )

class LeverSwitches(CheckboxSelectMultiple):
    template_name = 'common/lever_switches.html'

class InterventionForm(Form):   
    design_components = ModelChoiceField(
        queryset=DesignComponent.objects.all(),
        widget=LeverSwitches(attrs={'class' : 'row'}), 
        label='',
        empty_label=None,
        required=False,
    )
