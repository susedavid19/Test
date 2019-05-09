from django.contrib import admin
from django.utils.safestring import mark_safe

from expressways.core.models import Occurrence, SubOccurrence, OccurrenceConfiguration, DesignComponent, EffectIntervention


def archive(modeladmin, request, queryset):
    for item in queryset:
        if hasattr(item, 'sub_occurrences'):
            item.sub_occurrences.update(archived=True)
    queryset.update(archived=True)

archive.short_description = 'Archive'


class OccurrenceAdmin(admin.ModelAdmin):
    exclude = ['archived']
    actions = [archive]

admin.site.register(Occurrence, OccurrenceAdmin)


class SubOccurrenceAdmin(admin.ModelAdmin):
    exclude = ['archived']
    actions = [archive]
    list_filter = ['occurrence']

admin.site.register(SubOccurrence, SubOccurrenceAdmin)


class InterventionInline(admin.TabularInline):
    model = EffectIntervention
    extra = 0

class OccurrenceConfigurationAdmin(admin.ModelAdmin):
    list_display = ('sub_occurrence', 'flow', 'lane_closures', 'speed_limit', 'duration', 'frequency', 'possible_interventions')
    list_filter = ('sub_occurrence__occurrence', 'flow', 'lane_closures', 'speed_limit', 'duration')
    list_editable = ('frequency',)
    inlines = (InterventionInline,)
    exclude = ('effect',)

    def possible_interventions(self, obj):
        return mark_safe("<br><br>".join([inter.__str__() for inter in obj.effect.all()]))

admin.site.register(OccurrenceConfiguration, OccurrenceConfigurationAdmin)

class DesignComponentAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    exclude = ['archived']
    actions = [archive]

admin.site.register(DesignComponent, DesignComponentAdmin)

class EffectInterventionAdmin(admin.ModelAdmin):
    list_display = ('design_component', 'configuration_effect')
    list_filter = ('design_component', 'configuration_effect')
    verbose_name = 'Effect Intervention'
    verbose_name_plural = 'Effect Interventions'
    readonly_fields = ('design_component', 'configuration_effect', 'frequency_change', 'duration_change')

    def has_add_permission(self, request):
        return False

admin.site.register(EffectIntervention, EffectInterventionAdmin)