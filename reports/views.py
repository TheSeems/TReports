from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, redirect
# Create your views here.
from django.urls import reverse

from reports.forms import UserReportForm, CommentForm
from reports.models import Report


def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def normalize_page(page, count=0, default=1):
    if page is None:
        page = default

    try:
        page = int(page)
    except ValueError:
        page = default
        return page, True

    if page < 1 or page > count // 5 + (0 if count % 5 == 0 else 1):
        page = default
        return page, True

    return page, False


def rel(name, args=None):
    if args is None:
        args = []
    return redirect(reverse(name, args=args))


def filter_reports(request):
    selection = Report.objects.all()
    filters_applied = []
    if request.GET.get('status'):
        filters = Q()
        for name in request.GET.get('status').split(','):
            filters |= Q(status=name)
            filters_applied.append(name)

        selection = selection.filter(filters)

    return selection, filters_applied


@login_required
def render_index(request, **kwargs):
    selection, filters_applied = filter_reports(request)

    page, need_redirect = normalize_page(request.GET.get('page'), selection.count())

    if need_redirect:
        import urllib.parse as urlparse
        from urllib.parse import urlencode

        parts = list(urlparse.urlparse(request.get_raw_uri()))
        query = dict(urlparse.parse_qsl(parts[4]))

        needed_page = 1
        if request.GET.get('page') != "0":
            needed_page = selection.count() // 5 + (0 if selection.count() % 5 == 0 else 1)

        if needed_page == 0:
            return redirect('/')

        params = {'page': needed_page}
        query.update(params)
        parts[4] = urlencode(query)

        return redirect(urlparse.urlunparse(parts))

    return render(request, template_name='reports/index.html', context={
        "reports": selection.order_by('-open')[(page - 1) * 5: page * 5],
        "total": selection.count(),
        "fixed": selection.filter(status='F').count(),
        "your": selection.filter(author=request.user).count(),
        "filters": filters_applied
    })


@login_required
def render_report(request, rid=1):
    try:
        report = Report.objects.get(id=rid)

        return render(request, template_name='reports/full.html', context={
            "report": report,
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

                return rel('report', args=[report.id])
            except Report.DoesNotExist:
                return rel('index')

    return rel('index')


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
            return rel('report', args=[report.id])

    return render(request, template_name='reports/create.html', context={
        "form": UserReportForm
    })
