from django.contrib import admin

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


class OccurrenceConfigurationAdmin(admin.ModelAdmin):
    list_display = ('sub_occurrence', 'flow', 'lane_closures', 'speed_limit', 'duration', 'frequency')
    list_filter = ('sub_occurrence__occurrence', 'flow', 'lane_closures', 'speed_limit', 'duration')
    list_editable = ('frequency',)

admin.site.register(OccurrenceConfiguration, OccurrenceConfigurationAdmin)

class DesignComponentAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    exclude = ['archived']
    actions = [archive]

admin.site.register(DesignComponent, DesignComponentAdmin)

class EffectInterventionAdmin(admin.ModelAdmin):
    list_display = ('design_component', 'frequency_change', 'duration_change', 'justification')
    list_editable = ('frequency_change', 'duration_change',)

admin.site.register(EffectIntervention, EffectInterventionAdmin)