from django.forms import ModelForm, Textarea, CharField, IntegerField
from martor.fields import MartorFormField

from reports.models import Report, Comment


class ReportForm(ModelForm):
    steps = MartorFormField()

    class Meta:
        model = Report
        fields = ('name', 'steps', 'fact', 'expect', 'tags', 'author', 'status', 'open', 'comments')
        widgets = {'steps': Textarea}


class UserReportForm(ModelForm):
    steps = MartorFormField()

    class Meta:
        model = Report
        fields = ('name', 'steps', 'fact', 'expect', 'tags')


class ReportChangeForm(UserReportForm):
    report_id = IntegerField()


class CommentForm(ModelForm):
    content = MartorFormField()
    report_id = IntegerField()

    class Meta:
        model = Comment
        fields = ('content',)
