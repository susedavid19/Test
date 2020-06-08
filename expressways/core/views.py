from django.views import View
from django.views.generic import ListView
from django.views.generic.edit import CreateView, DeleteView, FormView
from django.views.defaults import page_not_found, server_error
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse
from braces.views import LoginRequiredMixin
from celery.result import AsyncResult
import time

from expressways.calculation.models import CalculationResult
from expressways.calculation.tasks import calculate
from expressways.core.models import OccurrenceConfiguration, Occurrence, SubOccurrence, Road, DesignComponent, EffectIntervention, OperationalObjective
from expressways.core.forms import InterventionForm, RoadSelectionForm


class HomeView(LoginRequiredMixin, View):
    def get(self, request, road_id):
        try:
            road = Road.objects.get(id=road_id)        
        except Road.DoesNotExist:
            return render(request, '404.html', { 'message': 'The road does not exist.' })
        
        form = InterventionForm()
        configurations = OccurrenceConfiguration.objects.filter(road=road_id)
        objectives = OperationalObjective.objects.all()
        context = {
            'road': road,
            'objectives': objectives,
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
    road_id = None

    def post(self, request):
        self.road_id = request.session['road_id']
        form = InterventionForm(request.POST)

        if form.is_valid():
            components = form.cleaned_data['design_components'] 
            if components:
                request.session['task_id'] = self.process_expressways_calculation(components)
            else:
                request.session['task_id'] = self.process_baseline_calculation()

        configurations = OccurrenceConfiguration.objects.filter(road=self.road_id)
        road = Road.objects.get(id=self.road_id)
        objectives = OperationalObjective.objects.all()
        context = {
            'road': road,
            'objectives': objectives,
            'configurations': configurations,
            'form': form,
        }
        return render(request, 'core/home.html', context)

    def create_calculation_object(self, occ_config):
        return {
            'lane_closures': occ_config.lane_closures,
            'duration': occ_config.duration,
            'flow': occ_config.flow,
            'frequency': occ_config.frequency,
        }
    
    def process_baseline_calculation(self):
        items = []
        calc_ids = []
        for item in OccurrenceConfiguration.objects.filter(road=self.road_id):
            calc_ids.append(item.pk)            
            items.append(self.create_calculation_object(item))

        try:
            calculated = CalculationResult.objects.get(config_ids=calc_ids, component_ids=[])
            return calculated.task_id
        except CalculationResult.DoesNotExist:
            res = calculate.delay(calc_ids, items)
            return res.id

    def create_expressways_object(self, occ_config, freq_val, dur_val):
    
        return {
            'lane_closures': occ_config.lane_closures,
            'duration': occ_config.duration,
            'flow': occ_config.flow,
            'frequency': occ_config.frequency,
            'duration_change': (dur_val / 100),
            'frequency_change': (freq_val / 100)
        }

    def value_to_use(self, value_list: list):
        if len(value_list) == 0:
            return 0
        max_val = max(value_list)
        min_val = min(value_list)
        if max_val > 0:
            return max_val
        else:
            return min_val

    def process_expressways_calculation(self, components):
        items = []
        calc_ids = []
        comp_ids = []
        freq_list = []
        dur_list = []
        for occ_config in OccurrenceConfiguration.objects.filter(road=self.road_id):
            calc_ids.append(occ_config.pk)            
            for comp in components:
                comp_ids.append(comp.pk)
                for item in EffectIntervention.objects.filter(configuration_effect__pk=occ_config.pk, design_component__pk=comp.pk):
                    freq_list.append(item.frequency_change) 
                    dur_list.append(item.duration_change)

            marked_freq_val = self.value_to_use(freq_list)
            marked_dur_val = self.value_to_use(dur_list)  
            items.append(self.create_expressways_object(occ_config, marked_freq_val, marked_dur_val))      

        try:
            calculated = CalculationResult.objects.get(config_ids=calc_ids, component_ids=comp_ids)
            return calculated.task_id
        except CalculationResult.DoesNotExist:
            res = calculate.delay(calc_ids, items, comp_ids)
            return res.id


class ResultView(LoginRequiredMixin, View):
    def get(self, request, task_id):
        res = AsyncResult(task_id)
        if res.failed():
            return JsonResponse({'msg': 'The Task Failed'}, status=500)

        result = get_object_or_404(CalculationResult, task_id=task_id)

        obj = {
            'objective_pti': '-',
            'objective_journey': '-',
            'objective_speed': '-',
            'objective_exp_pti': '-',
            'objective_exp_journey': '-',
            'objective_exp_speed': '-'
        }
        if 'result' in request.session:
            obj = request.session['result']

        if len(result.component_ids) > 0:
            obj['objective_exp_pti'] = str(result.objective_pti)
            obj['objective_exp_journey'] = str(result.objective_journey)
            obj['objective_exp_speed'] = str(result.objective_speed)
        else:
            obj['objective_pti'] = str(result.objective_pti)
            obj['objective_journey'] = str(result.objective_journey)
            obj['objective_speed'] = str(result.objective_speed)

        request.session['result'] = obj 

        return JsonResponse({
            'objective_pti': obj['objective_pti'], 
            'objective_journey': obj['objective_journey'],
            'objective_speed': obj['objective_speed'],
            'objective_exp_pti': obj['objective_exp_pti'], 
            'objective_exp_journey': obj['objective_exp_journey'],
            'objective_exp_speed': obj['objective_exp_speed']
        })


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
        if 'result' in self.request.session: # reset any previous calculation result
            del self.request.session['result']
        return reverse('core:home', kwargs={'road_id': self.road_id})


def custom404(request, exception=None):
    return page_not_found(request, None, '404.html')

def custom500(request):
    return server_error(request, '500.html')