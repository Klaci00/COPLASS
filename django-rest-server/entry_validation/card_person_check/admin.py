from django.contrib import admin
from .models import Employee, Card, GateEvent, SecurityZone, Gate, AccessRight, AccessRightRequest, Message, Department


# Register your models here.

class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('employee', 'content', 'is_read', 'created_at')
    search_fields = ('employee__firstname', 'employee__lastname', 'employee__hr_id', 'content')
    list_filter = ('is_read', 'created_at')
class AccessRightRequestAdmin(admin.ModelAdmin):
    list_display = ('security_zone', 'employee', 'start_date', 'end_date', 'approved')
    search_fields = ('security_zone__name', 'employee__firstname', 'employee__lastname', 'employee__hr_id')
    list_filter = ('security_zone', 'start_date', 'end_date', 'approved')
class AccessRightAdmin(admin.ModelAdmin):
    list_display = ('security_zone', 'start_date', 'end_date')
    search_fields = ('security_zone__name', 'start_date', 'end_date')
    list_filter = ('security_zone', 'start_date', 'end_date')
class SecurityZoneAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

class GateAdmin(admin.ModelAdmin):
    list_display = ('id', 'current_zone', 'opposite_zone')
    search_fields = ('id', 'current_zone__name', 'opposite_zone__name')
    list_filter = ('id', 'current_zone', 'opposite_zone')

class CardInline(admin.TabularInline):
    model = Card
    extra = 0

class AccessRightInline(admin.TabularInline):
    model = AccessRight
    extra = 0

class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('firstname', 'lastname', 'hr_id', 'department', 'supervisor')
    search_fields = ('firstname', 'lastname', 'hr_id', 'department', 'supervisor__firstname', 'supervisor__lastname', 'supervisor__hr_id')
    inlines = [CardInline, AccessRightInline]
    filter_horizontal = ('deputy',)  # For ManyToManyField deputy

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
admin.site.register(SecurityZone, SecurityZoneAdmin)
admin.site.register(Gate, GateAdmin)
admin.site.register(AccessRight, AccessRightAdmin)
admin.site.register(AccessRightRequest, AccessRightRequestAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(Department, DepartmentAdmin)