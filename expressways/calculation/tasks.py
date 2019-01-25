import json
import os
import pandas as pd

from expressways.calculation.celery import app
from expressways.calculation.models import CalculationResult
from expressways.calculation.import_model import *
from expressways.calculation.metrics import *


@app.task
def add(x, y):
    return x + y


@app.task(bind=True)
def calculate(self, items):
    objective_2 = 0
    df = pd.DataFrame()

    header = load_header_data(r'expressways/calculation/models', 'csv')
    print(header.head())

    freqs_list = []
    for item in items:
        freqs_list.append(item['frequency'])

    freqs_list = norm_freqs(freqs_list)
    i = 0
    for item in items:
        if item['lane_closures'] == 'II':
            df = load_csv_model_freq_light(df, os.path.join(r'expressways/calculation/models',
                                                            query_data(header,
                                                                       [str(item['flow']), item['lane_closures']])),
                                           str(item['flow']), freqs_list[i])

        else:
            df = load_csv_model_freq_light(df, os.path.join(r'expressways/calculation/models',
                                                            query_data(header,
                                                                       [str(item['flow']), item['lane_closures'],
                                                                        str(item['duration'])])), str(item['flow']),
                                           freqs_list[i])
        i += 1
        print(item)

    objective_1 = pti(df)

    result = CalculationResult()
    result.task_id = self.request.id
    result.items = json.dumps(items)
    result.objective_1 = objective_1
    result.objective_2 = objective_2
    result.save()
