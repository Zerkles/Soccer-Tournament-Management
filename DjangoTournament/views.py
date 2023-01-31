from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader


def index(request):
    return HttpResponseRedirect('/tournament')
