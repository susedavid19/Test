from django.db import models


class Occurrence(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class SubOccurrence(models.Model):
    name = models.CharField(max_length=200)
    occurrence = models.ForeignKey(Occurrence,
                                   on_delete=models.CASCADE,
                                   related_name='sub_occurrences')

    def __str__(self):
        return self.name
