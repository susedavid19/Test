import json
import os

from expressways.calculation.celery import app
from expressways.calculation.models import CalculationResult

@app.task
def add(x, y):
    return x + y

@app.task(bind=True)
def calculate(self, items):
    objective_1 = 0  # Sum of the frequencies
    objective_2 = 0  # Sum of the durations

    for item in items:
        objective_1 += item['frequency']
        objective_2 += item['duration']

    result = CalculationResult()
    result.task_id = self.request.id
    result.items = json.dumps(items)
    result.objective_1 = objective_1
    result.objective_2 = objective_2
    result.save()
