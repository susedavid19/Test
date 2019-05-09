from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from expressways.core.models import Road

class RoadListFilter(admin.SimpleListFilter):
    title = _('road')
    parameter_name = 'road'
    default_value = None

    def lookups(self, request, model_admin):
        road_list = []
        for road in Road.objects.all():
            road_list.append((
                str(road.id), road.name
            ))
        return sorted(road_list, key=lambda x: x[1])

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(road_id=self.value())
        
    def value(self):
        value = super(RoadListFilter, self).value()
        if value is None:
            if self.default_value is None:
                first_road = Road.objects.order_by('name').first()
                value = None if first_road is None else first_road.id
                self.default_value = value 
            else:
                value = self.default_value
        return str(value)

    def choices(self, changelist):
        for lookup, title in self.lookup_choices:
            yield {
                'selected': self.value() == str(lookup),
                'query_string': changelist.get_query_string({self.parameter_name: lookup}),
                'display': title,
            }