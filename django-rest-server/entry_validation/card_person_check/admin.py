from django.contrib import admin
from .models import Employee, Card, GateEvent, SecurityZone, Gate

# Register your models here.

class SercurityZoneAdmin(admin.ModelAdmin):
    pass

class GateAdmin(admin.ModelAdmin):
    pass
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('firstname', 'lastname', 'hr_id', 'department')
    search_fields = ('firstname', 'lastname', 'hr_id', 'department')

class CardAdmin(admin.ModelAdmin):
    list_display = ('card_number', 'employee', 'is_active', 'valid_from', 'valid_to')
    search_fields = ('card_number', 'employee__firstname', 'employee__lastname', 'employee__hr_id')
    list_filter = ('is_active', 'valid_from', 'valid_to')

class GateEventAdmin(admin.ModelAdmin):
    list_display = ('gate', 'card', 'timestamp', 'control', 'allowed', 'warning')
    search_fields = ('gate', 'card__card_number', 'card__employee__firstname', 'card__employee__lastname', 'card__employee__hr_id', 'timestamp', 'control', 'allowed', 'warning')
    list_filter = ('gate', 'timestamp', 'control', 'allowed', 'warning')

admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Card, CardAdmin)
admin.site.register(GateEvent, GateEventAdmin)
admin.site.register(SecurityZone, SercurityZoneAdmin)
admin.site.register(Gate, GateAdmin)