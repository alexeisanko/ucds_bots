from django.contrib import admin
from django.contrib.admin import ModelAdmin

from app.apps.core import models


@admin.register(models.TGUser)
class CoreAdmin(ModelAdmin[models.TGUser]):
    pass


@admin.register(models.Activity)
class CoreAdmin(ModelAdmin[models.Activity]):
    pass


@admin.register(models.TrackedActivity)
class CoreAdmin(ModelAdmin[models.TrackedActivity]):
    pass


@admin.register(models.TrackingTime)
class CoreAdmin(ModelAdmin[models.TrackingTime]):
    pass
