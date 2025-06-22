from django.contrib import admin
from .models import Location, Booking, Feedback

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'start_time', 'end_time', 'creation_time')
    list_filter = ('location', 'start_time')
    search_fields = ('user__username', 'location__number')
    ordering = ('-start_time',)

    # These fields will be shown in the form when editing
    fields = ('user', 'location', 'start_time', 'end_time')

    # Use dropdowns for foreign keys
    raw_id_fields = ('user', 'location')

    # Allow deletion directly from list view or detail view
    actions = ['delete_selected']

    # Optional: prevent changing user/location after creation
    # def get_readonly_fields(self, request, obj=None):
    #     if obj:  # editing an existing object
    #         return ('user', 'location')
    #     return ()
