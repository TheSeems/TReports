from django.db import models
from django.utils import timezone

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


class Report(models.Model):
    name = models.CharField(max_length=40)
    steps = models.CharField(max_length=1000)
    fact = models.CharField(max_length=100)
    expect = models.CharField(max_length=100)
    tags = models.ManyToManyField(Tag)
    id = models.BigAutoField(primary_key=True, auto_created=True, verbose_name='id')
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    open = models.DateTimeField(default=timezone.now)
    comments = models.ManyToManyField(Comment, blank=True)

    REPORT_STATUSES = (
        ('W', 'Ожидание'),
        ('L', 'Рассматривается'),
        ('D', 'Отклонено'),
        ('A', 'Принято'),
        ('F', 'Исправлено')
    )
    status = models.CharField(max_length=20, choices=REPORT_STATUSES)

    def __str__(self):
        return self.name + "@" + self.author.nick
