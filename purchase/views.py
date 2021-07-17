from django.shortcuts import render

from . import models

def index(request):
    return render(request, 'purchase/index.html', {
        'items': models.Item.objects.all()
    })