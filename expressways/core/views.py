from django.views import View
from django.shortcuts import render
from braces.views import LoginRequiredMixin
import time

from expressways.calculation.tasks import add

class HomeView(LoginRequiredMixin, View):
    def get(self, request):
        left = int(request.GET.get('left', 1))
        right = int(request.GET.get('right', 1))

        res = add.delay(left, right)
        while not res.ready():
            time.sleep(1)

        context = {
            'left': left,
            'right': right,
            'result': res.get(),
        }
        return render(request, 'core/home.html', context)
