from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import ugettext_lazy as _


class FilterArchivedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().exclude(archived=True).order_by('id')


class CommonInfo(models.Model):
    name = models.CharField(max_length=200, help_text=_('Provide a short, descriptive name'))
    archived = models.BooleanField(default=False)

    objects = FilterArchivedManager()

    class Meta:
        abstract = True


class Occurrence(CommonInfo):
    def __str__(self):
        return self.name


class SubOccurrence(CommonInfo):
    occurrence = models.ForeignKey(
        Occurrence,
        on_delete=models.CASCADE,
        help_text=_('Select ‘parent’ occurrence for the new sub-occurrence e.g. spillage (sub-occurrence) > Debris in road (parent occurrence). Add new occurrence if required.'),
        related_name='sub_occurrences'
    )

    def __str__(self):
        return self.name


class DesignComponent(CommonInfo):
    description = models.TextField(
        help_text=_('Provide a description of the design component, including any relevant references or supporting information')
    )

    def __str__(self):
        return self.name


class Road(CommonInfo):
    def __str__(self):
        return self.name
    

LANE_CHOICES = (
    ('II', 'II'),
    ('XI', 'XI'),
    ('XX', 'XX'),
    ('S', 'S'),
)

DURATION_CHOICES = (
    (2.5, '2.5'),
    (10, '10'),
    (25, '25'),
    (45, '45'),
    (90, '90'),
)

FLOW_CHOICES = (
    ('High', 'High'),
    ('Medium', 'Medium'),
    ('Low', 'Low'),
)

SPEED_CHOICES = (
    (70, '70'),
    (60, '60'),
    (50, '50'),
    (40, '40'),
)

class OccurrenceConfiguration(models.Model):
    road = models.ForeignKey(
        Road,
        help_text=_('Select road/project name​'),
        on_delete=models.CASCADE,
        null=True,
    )
    sub_occurrence = models.ForeignKey(
        SubOccurrence, 
        help_text=_('Select sub-occurrence to edit, re-name the sub-occurrence or create a new entry​'),
        on_delete=models.CASCADE
    )
    lane_closures = models.CharField(
        help_text=_('Select lane impact parameters i.e. II = all lanes open, XI = one lane closed (lane one or two), XX = both lanes closed, S = slow moving vehicle or WCH in lane​'),
        verbose_name='impact',
        max_length=2,
        choices=LANE_CHOICES,
        default='II',
    )
    duration = models.FloatField(
        help_text=_('Select how long the incident occurs for. i.e. 2.5 = 0 to 5 minutes; 10 = 5 to 15 minutes; 25 = 15 to 30 minutes; 45 = 30 to 60 minutes; 90 = 60 to 120 minutes. Not required for "slow moving vehicle" or "all lanes open" incident.'),
        choices=DURATION_CHOICES,
        default=2.5,
    )
    flow = models.CharField(
        help_text=_('Select traffic flow condition: High = >1000 Medium = >400 <1000 Low = <400 (vph)​'),
        verbose_name='flow rate',
        max_length=20,
        choices=FLOW_CHOICES,
        default='Low',
    )
    speed_limit = models.PositiveIntegerField(
        help_text=_('Select prevailing traffic speed (mph) for given occurrence (set default to 70mph)​​'),
        choices=SPEED_CHOICES,
        default=70,
    )
    frequency = models.PositiveIntegerField(
        help_text=_('Define the frequency of the occurrence (per mile per year)​')
    )
    incidents_cleared = models.BooleanField(
        help_text=_('If ticked, incidents occurring as a result of this Operational Occurrence will be included in the ‘Incidents Cleared’ calculation'),
        default=False
    )
    references = models.TextField(
        help_text=_('Provide references to data sources or a detailed explanation of any assumptions used e.g. calculations to determine frequencies or durations.'),
        default=''
    )
    effect = models.ManyToManyField(
        DesignComponent,
        verbose_name='Possible intervention',
        through='EffectIntervention'
    )

    def __str__(self):
        return f'{self.sub_occurrence.name}, {self.lane_closures}, {self.duration}, {self.flow}, {self.frequency}' 


class EffectIntervention(models.Model):
    design_component = models.ForeignKey(
        DesignComponent, 
        help_text=_('Select design component to create an impact score​'),
        on_delete=models.CASCADE, 
        verbose_name='Design component',
        null=True,
    )
    configuration_effect = models.ForeignKey(
        OccurrenceConfiguration,
        on_delete=models.CASCADE,
        verbose_name='Effect on configuration',
        null=True,
    )
    frequency_change = models.IntegerField(
        help_text=_(f'% change in frequency'),
        validators=[MinValueValidator(-100)]
    )
    duration_change = models.IntegerField(
        help_text=_(f'% change in duration'),
        validators=[MinValueValidator(-100)]
    )
    justification = models.TextField(
        help_text=_('Provide a detailed explanation and references for the sources of the impact sources. Must be based on real data, published research or an assumption agreed with relevant subject matter experts')
    )

    def __str__(self):
        return f'{self.design_component.name} with {self.frequency_change}% frequency and {self.duration_change}% duration change'


class OperationalObjective(CommonInfo):
    description = models.TextField()
    identifier = models.CharField(
        help_text=_('Operational objective identifier​'),
        max_length=10,
        default='',
    )

    def __str__(self):
        return self.name
