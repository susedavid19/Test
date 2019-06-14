from django.db import models
from django.contrib.postgres.fields import JSONField, ArrayField

class CalculationResult(models.Model):
    task_id = models.CharField(max_length=100)
    config_ids = ArrayField(models.IntegerField(), default=list)
    component_ids = ArrayField(models.IntegerField(), default=list)
    freq_list = ArrayField(models.IntegerField(), default=list)
    items = JSONField()
    objective_1 = models.DecimalField(max_digits=7, decimal_places=3)
    objective_2 = models.DecimalField(max_digits=7, decimal_places=3)
