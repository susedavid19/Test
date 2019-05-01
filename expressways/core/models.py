from django.db import models


class FilterArchivedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().exclude(archived=True).order_by('id')


class CommonInfo(models.Model):
    name = models.CharField(max_length=200)
    archived = models.BooleanField(default=False)

    objects = FilterArchivedManager()

    class Meta:
        abstract = True


class Occurrence(CommonInfo):
    def __str__(self):
        return self.name


class SubOccurrence(CommonInfo):
    occurrence = models.ForeignKey(Occurrence,
                                   on_delete=models.CASCADE,
                                   related_name='sub_occurrences')

    def __str__(self):
        return self.name


class DesignComponent(CommonInfo):
    description = models.TextField()

    def __str__(self):
        return self.name


class EffectIntervention(models.Model):
    design_component = models.ForeignKey(DesignComponent, on_delete=models.CASCADE)
    frequency_change = models.IntegerField()
    duration_change = models.IntegerField()
    justification = models.TextField()

    def __str__(self):
        return f'{self.design_component.name}_{self.frequency_change}_{self.duration_change}'

LANE_CHOICES = (
    ('II', 'II'),
    ('IX', 'IX'),
    ('XI', 'XI'),
    ('XX', 'XX'),
)

DURATION_CHOICES = (
    (15, '15'),
    (30, '30'),
    (45, '45'),
    (60, '60'),
    (120, '120'),
    (300, '300'),
)

FLOW_CHOICES = (
    (1750, 'High'),
    (1250, 'Medium High'),
    (750, 'Medium Low'),
    (300, 'Low'),
)

SPEED_CHOICES = (
    (70, '70'),
    (60, '60'),
    (50, '50'),
    (40, '40'),
)

class OccurrenceConfiguration(models.Model):
    sub_occurrence = models.OneToOneField(SubOccurrence, 
        on_delete=models.CASCADE, default=1)
    lane_closures = models.CharField(
        verbose_name='impact',
        max_length=2,
        choices=LANE_CHOICES,
        default='II',
    )
    duration = models.PositiveIntegerField(
        choices=DURATION_CHOICES,
        default=15,
    )
    flow = models.PositiveIntegerField(
        verbose_name='flow rate',
        choices=FLOW_CHOICES,
        default=300,
    )
    speed_limit = models.PositiveIntegerField(
        choices=SPEED_CHOICES,
        default=70,
    )
    frequency = models.PositiveIntegerField()
    effects = models.ManyToManyField(
        'EffectIntervention',
        verbose_name='Possible intervention'
    )

    def __str__(self):
        return ('{}_{}_{}_{}_{}').format(self.sub_occurrence.name, 
            self.lane_closures, self.duration, self.flow, self.frequency)
    