from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.views import View


class SimpleView(View):
    @staticmethod
    def get(_: HttpRequest) -> HttpResponse:
        return HttpResponseRedirect('/admin')
