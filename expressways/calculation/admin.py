from django.contrib import admin
from expressways.calculation.models import CalculationResult

class CalculationAdmin(admin.ModelAdmin):
    readonly_fields = ('task_id', 'config_ids', 'component_ids', 'freq_list', 'items', 'objective_incident', 'objective_pti', 'objective_journey', 'objective_speed')

admin.site.register(CalculationResult, CalculationAdmin)