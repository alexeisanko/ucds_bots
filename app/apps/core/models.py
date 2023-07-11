from django.db import models


class TGUser(models.Model):
    id = models.BigIntegerField(primary_key=True, verbose_name="ID пользователя")
    chat_id = models.BigIntegerField(verbose_name="ID чата")
    username = models.CharField(
        max_length=64, null=True, verbose_name="Никнейм"
    )
    balance = models.IntegerField(verbose_name='Баланс', default=0)
    is_active = models.BooleanField(verbose_name="Активность", default=False)
    data_created = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    objects: models.manager.BaseManager["TGUser"]

    class Meta:
        db_table = "TGUser"


class Activity(models.Model):
    name = models.CharField(max_length=64, unique=True, verbose_name='Наименование активности')
    is_active = models.BooleanField(default=True, verbose_name='Актуальная активность?')
    objects: models.manager.BaseManager["Activity"]

    class Meta:
        db_table = "Activity"


class TrackingTime(models.Model):
    user = models.ForeignKey(TGUser, verbose_name='Пользователь', on_delete=models.CASCADE)
    period = models.DateField(verbose_name='До какого числа отслеживается')
    mode = models.CharField(verbose_name='Режим')
    objects: models.manager.BaseManager["TrackingTime"]

    class Meta:
        db_table = "TrackingTime"


class TrackedActivity(models.Model):
    user = models.ForeignKey(TGUser, verbose_name='Пользователь', on_delete=models.CASCADE)
    activity = models.ForeignKey(Activity, verbose_name='Активность', on_delete=models.PROTECT)
    tracking_time = models.TimeField(verbose_name='Время отслеживания')
    objects: models.manager.BaseManager["TrackedActivity"]

    class Meta:
        db_table = "TrackedActivity"
