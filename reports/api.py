import json

from django.core import serializers
from django.http import HttpResponse, JsonResponse

from reports.models import Report


class ApiQueryException(Exception):
    def __init__(self, message):
        self.message = message


def require_param(request, name, method='get'):
    if method == 'post':
        value = request.POST.get(name)
    else:
        value = request.GET.get(name)

    if value is None:
        raise ApiQueryException("Missing required param '" + name + "'")

    return value


def require_int(request, name, method='get'):
    try:
        return int(require_param(request, name, method))
    except ValueError:
        raise ApiQueryException("Expected param '" + name + "' as integer")


def wrap(answer):
    return JsonResponse(answer)


def api_get_report(request):
    answer = dict()
    try:
        report = Report.objects.get(id=require_int(request, 'id'))
        answer['success'] = True

        report_dict = dict()
        report_dict['name'] = report.name
        report_dict['author'] = report.author.nick
        report_dict['steps'] = report.steps
        report_dict['status'] = report.status
        report_dict['tags'] = [tag.name for tag in report.tags.all()]

        answer['report'] = report_dict
    except Report.DoesNotExist:
        answer['success'] = False
        answer['message'] = "No report found by that id"
    except ApiQueryException as err:
        answer['success'] = False
        answer['message'] = err.message

    return wrap(answer)