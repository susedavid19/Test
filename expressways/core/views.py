from django.views import View
from django.views.generic import ListView
from django.views.generic.edit import CreateView, DeleteView, FormView
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse
from braces.views import LoginRequiredMixin
from celery.result import AsyncResult
import time

from expressways.calculation.models import CalculationResult
from expressways.calculation.tasks import calculate
from expressways.core.models import OccurrenceConfiguration, Occurrence, SubOccurrence, Road
from expressways.core.forms import InterventionForm, RoadSelectionForm


class HomeView(LoginRequiredMixin, View):
    def get(self, request, road_id):
        form = InterventionForm()
        configurations = OccurrenceConfiguration.objects.filter(road=road_id)
        road = Road.objects.get(id=road_id)
        context = {
            'road': road,
            'configurations': configurations,
            'form': form,
        }
        return render(request, 'core/home.html', context)


class DeleteOccurrenceConfiguration(LoginRequiredMixin, DeleteView):
    model = OccurrenceConfiguration

    def get_object(self):
        obj = super(DeleteOccurrenceConfiguration, self).get_object()
        CalculationResult.objects.filter(config_ids__contains=[obj.pk]).delete()
        return obj

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        if 'task_id' in self.request.session:
            del self.request.session['task_id']
        return response

    def get_success_url(self):
        return reverse('core:home', kwargs={'road_id': self.request.session['road_id']})


class CalculateView(LoginRequiredMixin, View):    
    def post(self, request):
        items = []
        calc_ids = []
        road_id = request.session['road_id']
        intform = InterventionForm(request.POST)
        design_comp = request.POST.getlist('design_components')
        print('DES: ', design_comp, intform) 

        for item in OccurrenceConfiguration.objects.filter(road=road_id):
            calc_ids.append(item.pk)            
            items.append(self.create_calculation_object(item))

        try:
            calculated = CalculationResult.objects.get(config_ids=calc_ids)
            request.session['task_id'] = calculated.task_id
        except CalculationResult.DoesNotExist:
            res = calculate.delay(calc_ids, items)
            request.session['task_id'] = res.id

        return redirect(reverse('core:home', kwargs={'road_id': road_id}))

    def create_calculation_object(self, occ_config):
        return {
            'lane_closures': occ_config.lane_closures,
            'duration': occ_config.duration,
            'flow': occ_config.flow,
            'frequency': occ_config.frequency,
        }


class ResultView(LoginRequiredMixin, View):
    def get(self, request, task_id):
        res = AsyncResult(task_id)
        if res.failed():
            return JsonResponse({'msg': 'The Task Failed'}, status=500)

        result = get_object_or_404(CalculationResult, task_id=task_id)

        return JsonResponse({'objective_1': result.objective_1, 'objective_2': result.objective_2})


class SubOccurrenceOptionsView(LoginRequiredMixin, ListView):
    model = SubOccurrence
    template_name = 'core/sub_occurrences_list_options.html'
    context_object_name = 'sub_occurrences'

    def get_queryset(self):
        occurrence_id = self.request.GET.get('occurrence')
        query_set = self.model.objects.filter(occurrence_id=occurrence_id).order_by('name')
        return query_set

class RoadSelectionView(LoginRequiredMixin, FormView):
    template_name = 'core/road_selection.html'
    form_class = RoadSelectionForm
    road_id = None

    def get_initial(self):
        initial = super(RoadSelectionView, self).get_initial()
        if 'road_id' in self.request.session:
            initial['road'] = Road.objects.get(id=self.request.session['road_id'])
        return initial

    def form_valid(self, form):
        road = form.cleaned_data.get('road')
        self.road_id = road.id
        return super(RoadSelectionView, self).form_valid(form)

    def get_success_url(self):
        self.request.session['road_id'] = self.road_id
        if 'task_id' in self.request.session: # reset any previous task id when road is changed
            del self.request.session['task_id']
        return reverse('core:home', kwargs={'road_id': self.road_id})
