from django.shortcuts import render
from django.core.paginator import Paginator


class Core:
    def index(request):
        return render(request, 'index.html')
