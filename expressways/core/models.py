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
