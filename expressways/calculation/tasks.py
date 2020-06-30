import json
import os
import pandas as pd
from expressways.calculation.celery import app, ExpresswaysException
from expressways.calculation.models import CalculationResult
from expressways.calculation.import_model import *
from expressways.calculation.metrics import *


BOTH_LANES_OPEN = 'II'

@app.task(bind=True)
def calculate(self, config_ids, items, component_ids= None):
    df = pd.DataFrame()
    experr = ExpresswaysException(self)
    header = load_header_data(r'expressways/calculation/models', 'csv')
    freqs_list = []
    lte_an_hour_list = []
    zero_freq_list = []

    # raise exception if the road has no configuration item
    if len(items) == 0:
        experr.log('No occurrence configuration found for this road.')

    if component_ids:
        freq_change = []
        dur_change = []
        durations = []

        for item in items:
            freqs_list.append(item['frequency'])
            durations.append(item['duration'])
            dur_change.append(item['duration_change'])
            freq_change.append(item['frequency_change'])

            if item['duration'] <= 60 and item['incidents_cleared']:
                lte_an_hour_list.append(item)
            
            if item['frequency'] == 0:
                zero_freq_list.append(item)

        freqs_list = frequency_change(freqs_list, freq_change)
        freqs_list = duration_bin(freqs_list, dur_change, durations)
    else:
        for item in items:
            freqs_list.append(item['frequency'])

            if item['duration'] <= 60 and item['incidents_cleared']:
                lte_an_hour_list.append(item)
            
            if item['frequency'] == 0:
                zero_freq_list.append(item)

    # raise exception if all configuration items have zero frequency
    if len(items) == len(zero_freq_list):
        experr.log('Invalid ie all zero frequency configurations found on this road.')

    freqs_list = norm_freqs(freqs_list)
    for i, item in enumerate(items):
        params_list = [str(item['flow']).upper(), item['lane_closures']]
        if item['lane_closures'] != BOTH_LANES_OPEN:
            # Add duration to factor in if any lane is impacted with closure
            params_list.append(str(item['duration']).replace('.', '_'))

        df = load_csv_model_freq(
                df, 
                os.path.join(r'expressways/calculation/models',
                    query_data(
                        header,
                        params_list
                    )),
                str(item['flow']), freqs_list[i]
            )

    # raise exception if configuration outside specified analysis time range
    if get_data_on_time_range(df).empty:
        experr.log('No valid analysis found within time range for configuration on this road.')

    objective_incident = incidents_cleared(lte_an_hour_list, items)
    objective_pti = pti(df)
    objective_journey = acceptable_journeys(df)
    objective_speed = average_speed(df)
    result = CalculationResult()
    result.task_id = self.request.id
    result.items = json.dumps(items)
    result.config_ids = config_ids
    if component_ids:
        result.component_ids = component_ids
    result.freq_list = freqs_list
    result.objective_incident = objective_incident
    result.objective_pti = objective_pti
    result.objective_journey = objective_journey
    result.objective_speed = objective_speed
    result.save()
