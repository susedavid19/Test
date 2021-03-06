from django.contrib import admin
from django.utils.safestring import mark_safe

from expressways.core.models import Occurrence, SubOccurrence, OccurrenceConfiguration, DesignComponent, EffectIntervention, Road
from expressways.core.admin_list_filter import RoadListFilter

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
    fields = ('road', 'sub_occurrence', 'flow', 'lane_closures', 'speed_limit', 'duration', 'frequency', 'incidents_cleared', 'references')
    list_display = ('road', 'sub_occurrence', 'flow', 'lane_closures', 'speed_limit', 'duration', 'frequency', 'incidents_cleared', 'possible_interventions')
    list_filter = (RoadListFilter, 'sub_occurrence__occurrence', 'flow', 'lane_closures', 'speed_limit', 'duration', 'incidents_cleared')
    list_editable = ('frequency',)
    inlines = (InterventionInline,)
    exclude = ('effect',)

    class Media:
        css = {
            'all': ('admin/configuration-style.css',)
        }

    def possible_interventions(self, obj):
        return mark_safe("<br><br>".join([inter.__str__() for inter in obj.effect.all()]))
    
    def get_readonly_fields(self, request, obj=None):
        if obj: # editing an existing object
            return self.readonly_fields + ('road',)
        return self.readonly_fields

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
    readonly_fields = ('design_component', 'configuration_effect', 'frequency_change', 'duration_change', 'justification')

    def has_add_permission(self, request):
        return False

admin.site.register(EffectIntervention, EffectInterventionAdmin)

class RoadAdmin(admin.ModelAdmin):
    exclude = ['archived']
    actions = [archive]

admin.site.register(Road, RoadAdmin)
