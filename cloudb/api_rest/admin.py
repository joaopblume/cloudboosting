from django.contrib import admin
from .models import InstanceSchedule

# Register your models here.
@admin.register(InstanceSchedule)
class InstanceScheduleAdmin(admin.ModelAdmin):
    list_display = ('instance_id', 'user', 'frequency', 'status')
    list_filter = ('frequency', 'status')
    search_fields = ('instance_id', 'user__username')