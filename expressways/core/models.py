from django.db import models


class FilterArchivedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().exclude(archived=True).order_by('id')


class Occurrence(models.Model):
    name = models.CharField(max_length=200)
    archived = models.BooleanField(default=False)

    objects = FilterArchivedManager()

    def __str__(self):
        return self.name


class SubOccurrence(models.Model):
    name = models.CharField(max_length=200)
    archived = models.BooleanField(default=False)
    occurrence = models.ForeignKey(Occurrence,
                                   on_delete=models.CASCADE,
                                   related_name='sub_occurrences')

    objects = FilterArchivedManager()

    def __str__(self):
        return self.name


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


class OccurrenceConfiguration(models.Model):
    sub_occurrence = models.ForeignKey(SubOccurrence,
                                       on_delete=models.CASCADE)
    lane_closures = models.CharField(
        max_length=2,
        choices=LANE_CHOICES,
        default='II',
    )
    duration = models.PositiveIntegerField(
        choices=DURATION_CHOICES,
        default=15,
    )
    flow = models.PositiveIntegerField(
        choices=FLOW_CHOICES,
        default=300,
    )
    frequency = models.PositiveIntegerField()
