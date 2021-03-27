from urllib.parse import urlencode

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
# Create your views here.
from django.urls import reverse

from reports.forms import UserReportForm, CommentForm
from reports.models import Report


def is_int(s):
    if s is None:
        return False

    try:
        int(s)
        return True
    except ValueError:
        return False


def normalize_page(page, count=0, default=1):
    if page is None:
        page = default

    if page < 1 or page > count // 5 + (0 if count % 5 == 0 else 1):
        page = default
        return page

    return page


def custom_redirect(url_name, *args, **kwargs):
    url = reverse(url_name, args=args)
    params = urlencode(kwargs)
    return HttpResponseRedirect(url + "?%s" % params)


def redirect_reverse(name, args=None):
    if args is None:
        args = []
    return redirect(reverse(name, args=args))


def filter_reports_by_status(request, selection=Report.objects.all()):
    filters_applied = []
    if request.GET.get('status'):
        filters = Q()
        for name in request.GET.get('status').split(','):
            filters |= Q(status=name)
            filters_applied.append(name)

        selection = selection.filter(filters).distinct()

    return selection, filters_applied


def filter_reports_by_tag(request, selection=Report.objects.all()):
    filters_applied = []
    if request.GET.get('tags'):
        filters = Q()
        for tag_id in request.GET.get('tags').split(','):
            if is_int(tag_id):
                filters |= Q(tags=tag_id)
                filters_applied.append(int(tag_id))

        selection = selection.filter(filters).distinct()

    return selection, filters_applied


@login_required
def render_index(request, **kwargs):
    selection, filters_applied = filter_reports_by_status(request)
    selection, tag_filters_applied = filter_reports_by_tag(request, selection)

    current_page = request.GET.get('page')
    if not is_int(current_page):
        current_page = None
    else:
        current_page = int(current_page)

    bound_page = normalize_page(current_page, selection.count())
    if current_page is not None and bound_page != current_page:
        if bound_page == 1:
            return redirect_reverse('index')
        return custom_redirect('index', page=bound_page)

    return render(request, template_name='reports/index.html', context={
        "reports": selection.order_by('-open')[(bound_page - 1) * 5: bound_page * 5],
        "total": selection.count(),
        "fixed": selection.filter(status='F').count(),
        "your": selection.filter(author=request.user).count(),
        "filters": filters_applied,
        "tag_filters": tag_filters_applied
    })


@login_required
def render_report(request, rid=1):
    try:
        report = Report.objects.get(id=rid)
        return render(request, template_name='reports/full.html', context={
            "report": report,
            "events": report.events.all()[:3],
            "rest_events_count": report.events.all().count() - 3,
            "form": CommentForm
        })
    except Report.DoesNotExist:
        return reverse('index')


@login_required
def make_comment(request):
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            report_id = form.cleaned_data["report_id"]
            try:
                report = Report.objects.get(id=report_id)
                comment = form.save(commit=False)
                comment.content = form.cleaned_data["content"]
                comment.author = request.user

                comment.save()
                report.comments.add(comment)
                report.save()

                return redirect_reverse('report', args=[report.id])
            except Report.DoesNotExist:
                return redirect_reverse('index')

    return redirect_reverse('index')


@login_required
def create_report(request):
    if request.method == "POST":
        form = UserReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.status = 'W'
            report.author = request.user
            report.save()

            for i in form.cleaned_data["tags"]:
                report.tags.add(i)

            report.save()
            return redirect_reverse('report', args=[report.id])

    return render(request, template_name='reports/create.html', context={
        "form": UserReportForm
    })
