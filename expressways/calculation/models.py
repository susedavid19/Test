from django.db import models
from django.contrib.postgres.fields import JSONField

class CalculationResult(models.Model):
    task_id = models.CharField(max_length=100)
    items = JSONField()
    objective_1 = models.DecimalField(max_digits=7, decimal_places=3)
    objective_2 = models.DecimalField(max_digits=7, decimal_places=3)
