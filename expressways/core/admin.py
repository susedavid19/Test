from django.contrib import admin

from expressways.core.models import Occurrence, SubOccurrence


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
