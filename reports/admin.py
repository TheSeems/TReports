from django.contrib import admin

# Register your models here.
from reports.forms import ReportForm, CommentForm
from reports.models import Report, Tag, Comment


class ReportAdmin(admin.ModelAdmin):
    form = ReportForm


class CommentAdmin(admin.ModelAdmin):
    form = CommentForm
    fields = ('id',)


admin.site.register(Report, ReportAdmin)
admin.site.register(Tag)
admin.site.register(Comment)
