from django.contrib.auth.decorators import login_required
from django.db.models import Max
from django.shortcuts import render, redirect

# Create your views here.
from reports.forms import UserReportForm, CommentForm
from reports.models import Report, Comment


def normalize_page(page, default=1):
    if page is None:
        page = default

    try:
        page = int(page)
    except ValueError:
        page = default
        return page, True

    if page < 1 or page > (Report.objects.count() + 5) // 5:
        page = default
        return page, True

    return page, False


@login_required
def render_index(request, **kwargs):
    page, need_redirect = normalize_page(request.GET.get('page'))

    if need_redirect:
        print('page', request.GET.get('page'))
        if request.GET.get('page') != "0":
            return redirect('/?page=' + str((Report.objects.count() + 5) // 5))
        return redirect('/?page=1')

    return render(request, template_name='reports/index.html', context={
        "reports": Report.objects.all().order_by('-open')[(page - 1) * 5: page * 5],
        "total": Report.objects.count(),
        "fixed": Report.objects.filter(status='F').count(),
        "your": Report.objects.filter(author=request.user).count()
    })


@login_required
def render_report(request, rid=0):
    try:
        report = Report.objects.get(id=rid)

        return render(request, template_name='reports/full.html', context={
            "report": report,
            "form": CommentForm
        })
    except Report.DoesNotExist:
        return render_index(request)


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

                return redirect('/r/' + str(report_id))
            except Report.DoesNotExist:
                return redirect('/')
    return redirect('/')


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
            return redirect('/r/' + str(report.id))
        else:
            print('invalid')

    return render(request, template_name='reports/create.html', context={
        "form": UserReportForm
    })
