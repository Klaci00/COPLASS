from django.contrib import admin
from .models import Employee, Card, GateEvent, SecurityZone, Gate, AccessRight
from django.db import models
from django import forms

# Register your models here.

class AccessRightAdmin(admin.ModelAdmin):
    list_display = ('security_zone', 'start_date', 'end_date')
    search_fields = ('security_zone__name', 'start_date', 'end_date')
    list_filter = ('security_zone', 'start_date', 'end_date')
class SercurityZoneAdmin(admin.ModelAdmin):
    pass

class GateAdmin(admin.ModelAdmin):
    pass

class CardInline(admin.TabularInline):
    model = Card
    extra = 0

class AccessRightInline(admin.TabularInline):
    model = AccessRight
    extra = 0

class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('firstname', 'lastname', 'hr_id', 'department')
    search_fields = ('firstname', 'lastname', 'hr_id', 'department')
    inlines = [CardInline, AccessRightInline]

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
admin.site.register(AccessRight, AccessRightAdmin)