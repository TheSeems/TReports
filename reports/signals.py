from django.db.models.signals import pre_save

from reports.models import Report, ReportChangeStatusAction


def on_status_change(sender, instance, **kwargs):
    if instance.id is None:
        return
    previous = Report.objects.get(id=instance.id)
    if previous.status != instance.status:
        action = ReportChangeStatusAction()
        action.previous_status = previous.status
        action.status = instance.status
        action.save()
        instance.events.add(action)


pre_save.connect(on_status_change, sender=Report,
                 dispatch_uid="on_status_change")
