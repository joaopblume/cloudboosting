from django.contrib import admin
from .models import CombinedScheduleView

@admin.register(CombinedScheduleView)
class CombinedScheduleViewAdmin(admin.ModelAdmin):
    list_display = (
        'schedule_id',
        'user_name',
        'instance_name',
        'weekly_day',
        'weekly_start',
        'weekly_end',
        'monthly_day',
        'monthly_start',
        'monthly_end',
    )
    search_fields = ('user_name', 'instance_name', 'weekly_day', 'monthly_day')
    list_filter = ('weekly_day', 'monthly_day')