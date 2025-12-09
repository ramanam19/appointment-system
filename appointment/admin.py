from django.contrib import admin
from .models import Appointment

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    """
    Customize how appointments appear in admin panel
    """
    list_display = ['id', 'user', 'name', 'date', 'time', 'status', 'created_at']
    list_filter = ['status', 'date', 'created_at']
    search_fields = ['name', 'user__username', 'description']
    list_editable = ['status']
    date_hierarchy = 'date'
    
    # Fields to show when viewing/editing an appointment
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'name', 'age')
        }),
        ('Appointment Details', {
            'fields': ('date', 'time', 'description', 'status')
        }),
    )