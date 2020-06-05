import json
import os
import pandas as pd
import logging
from expressways.calculation.celery import app
from expressways.calculation.models import CalculationResult
from expressways.calculation.import_model import *
from expressways.calculation.metrics import *


@app.task
def add(x, y):
    return x + y


@app.task(bind=True)
def calculate(self, config_ids, items, component_ids= None):
    df = pd.DataFrame()
    header = load_header_data(r'expressways/calculation/models', 'csv')
    logging.warning(f'HEADER: {header.head()}')
    freqs_list = []
    if component_ids:
        freq_change = []
        dur_change = []
        durations = []

        for item in items:
            freqs_list.append(item['frequency'])
            durations.append(item['duration'])
            dur_change.append(item['duration_change'])
            freq_change.append(item['frequency_change'])

        freqs_list = frequency_change(freqs_list, freq_change)
        freqs_list = duration_bin(freqs_list, dur_change, durations)
    else:
        for item in items:
            freqs_list.append(item['frequency'])


    freqs_list = norm_freqs(freqs_list)
    for i, item in enumerate(items):
        logging.warning(f'Lane Type: {item["lane_closures"]}')
        if item['lane_closures'] == 'II':
            df = load_csv_model_freq(
                    df, 
                    os.path.join(r'expressways/calculation/models',
                        query_data(
                            header,
                            [str(item['flow']).upper(), item['lane_closures']]
                        )),
                    str(item['flow']), freqs_list[i]
                )

        else:
            df = load_csv_model_freq(
                    df, 
                    os.path.join(r'expressways/calculation/models',
                        query_data(
                            header,
                            [str(item['flow']).upper(), item['lane_closures'], str(item['duration']).replace('.', '_')]
                        )),
                    str(item['flow']), freqs_list[i]
                )

    objective_1 = pti(df)
    objective_2 = acceptable_journeys(df)
    result = CalculationResult()
    result.task_id = self.request.id
    result.items = json.dumps(items)
    result.config_ids = config_ids
    if component_ids:
        result.component_ids = component_ids
    result.freq_list = freqs_list
    result.objective_1 = objective_1
    result.objective_2 = objective_2
    result.save()
