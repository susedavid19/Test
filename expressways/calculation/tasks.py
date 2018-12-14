import json
import os
import pandas as pd

from expressways.calculation.celery import app
from expressways.calculation.models import CalculationResult
from expressways.calculation.importmodel import *
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

    for item in items:

        if item['lane_closures'] == 'II':
            for i in range(item['frequency']):
                df = load_csv_model(df, os.path.join(r'expressways/calculation/models',
                                                 query_data(header, [str(item['flow']), item['lane_closures']])),
                                str(item['flow']))

        else:
            for i in range(item['frequency']):
                df = load_csv_model(df, os.path.join(r'expressways/calculation/models',
                                                 query_data(header, [str(item['flow']), item['lane_closures'], str(item['duration'])])),
                                str(item['flow']))
        print(item)

    objective_1 = pti(df)

    result = CalculationResult()
    result.task_id = self.request.id
    result.items = json.dumps(items)
    result.objective_1 = objective_1
    result.objective_2 = objective_2
    result.save()
