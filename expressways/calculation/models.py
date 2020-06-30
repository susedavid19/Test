from django.db import models
from django.contrib.postgres.fields import JSONField, ArrayField
from django.utils.translation import ugettext_lazy as _

class CalculationResult(models.Model):
    task_id = models.CharField(max_length=100)
    config_ids = ArrayField(models.IntegerField(), default=list)
    component_ids = ArrayField(models.IntegerField(), default=list)
    freq_list = ArrayField(models.IntegerField(), default=list)
    items = JSONField()
    objective_incident = models.DecimalField(max_digits=7, decimal_places=3, default=0.0, help_text=_('Objective for incidents cleared'))
    objective_pti = models.DecimalField(max_digits=7, decimal_places=3, default=0.0, help_text=_('Objective for planning time index'))
    objective_journey = models.DecimalField(max_digits=7, decimal_places=3, default=0.0, help_text=_('Objective for acceptable journeys'))
    objective_speed = models.DecimalField(max_digits=7, decimal_places=3, default=0.0, help_text=_('Objective for average speed'))

    def __str__(self):
        return self.task_id
