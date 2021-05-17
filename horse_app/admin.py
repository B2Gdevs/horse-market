from django.contrib import admin

# Register your models here.
from horse_app.models import Horse, SliderImage, Message

admin.site.register(Horse)
admin.site.register(SliderImage)
admin.site.register(Message)
