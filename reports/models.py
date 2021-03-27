from django.db import models
from django.utils import timezone
from polymorphic.models import PolymorphicModel

from users.models import CustomUser


class Tag(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Comment(models.Model):
    content = models.CharField(max_length=100)
    id = models.BigAutoField(primary_key=True)
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.id) + "@" + str(self.author.nick)


REPORT_STATUSES = (('W', 'Ожидание'),
                   ('L', 'Рассматривается'),
                   ('D', 'Отклонено'),
                   ('A', 'Принято'),
                   ('F', 'Исправлено'))


class ReportAction(PolymorphicModel):
    id = models.BigAutoField(primary_key=True, auto_created=True, verbose_name='id')
    date = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-date']


class ReportChangeStatusAction(ReportAction):
    previous_status = models.CharField(max_length=20, blank=False, null=False, default='W', choices=REPORT_STATUSES)
    status = models.CharField(max_length=20, blank=False, null=False, default='W', choices=REPORT_STATUSES)

    def __str__(self):
        return F"Change status from {self.previous_status} to {self.status}"


class Report(models.Model):
    id = models.BigAutoField(primary_key=True, auto_created=True, verbose_name='id')

    name = models.CharField(max_length=40)
    steps = models.CharField(max_length=1000)
    fact = models.CharField(max_length=100)
    expect = models.CharField(max_length=100)

    status = models.CharField(max_length=20, choices=REPORT_STATUSES)
    tags = models.ManyToManyField(Tag, blank=True)

    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    open = models.DateTimeField(default=timezone.now)

    comments = models.ManyToManyField(Comment, blank=True)
    events = models.ManyToManyField(ReportAction, blank=True, default=None)

    def __str__(self):
        return self.name + "@" + self.author.nick
