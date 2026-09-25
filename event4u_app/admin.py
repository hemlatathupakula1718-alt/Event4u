from django.contrib import admin
from .models import (
    UserProfile, Coordinator, SubCoordinator, Proposal, Event, SubEvent,
    Volunteer, Participant, Audience, Payment, Notification, Memories,
    Pass, AttendanceLog
)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'fullName', 'branch', 'semester', 'erp', 'phone')
    list_filter = ('role', 'branch', 'semester')
    search_fields = ('user__username', 'fullName', 'erp', 'phone')

@admin.register(Coordinator)
class CoordinatorAdmin(admin.ModelAdmin):
    list_display = ('name', 'branch', 'semester', 'erp', 'user')
    list_filter = ('branch', 'semester')
    search_fields = ('name', 'erp', 'user__username')

@admin.register(SubCoordinator)
class SubCoordinatorAdmin(admin.ModelAdmin):
    list_display = ('name', 'event', 'branch', 'semester', 'erp', 'coordinator', 'user')
    list_filter = ('branch', 'semester', 'event')
    search_fields = ('name', 'erp', 'event__name')

@admin.register(Proposal)
class ProposalAdmin(admin.ModelAdmin):
    list_display = ('title', 'coordinator', 'status', 'HoD_Approval', 'Principal_Approval', 'fundRecieveFromCollege', 'createdAt')
    list_filter = ('status', 'HoD_Approval', 'Principal_Approval', 'createdAt')
    search_fields = ('title', 'coordinator__name', 'description')

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'coordinator', 'status', 'totalMoney', 'eventDate', 'registrationOpen')
    list_filter = ('status', 'category', 'registrationOpen', 'eventDate')
    search_fields = ('name', 'coordinator__name', 'description', 'venue')

@admin.register(SubEvent)
class SubEventAdmin(admin.ModelAdmin):
    list_display = ('name', 'event', 'subcoordinator', 'totalBudget', 'utiliseBudget', 'balanceBudget')
    list_filter = ('event', 'subcoordinator')
    search_fields = ('name', 'event__name')

@admin.register(Volunteer)
class VolunteerAdmin(admin.ModelAdmin):
    list_display = ('name', 'event', 'subevent', 'branch', 'semester', 'erp', 'status')
    list_filter = ('status', 'branch', 'event')
    search_fields = ('name', 'erp', 'work')

@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('name', 'event', 'subevent', 'branch', 'semester', 'erp', 'interest')
    list_filter = ('branch', 'event', 'subevent')
    search_fields = ('name', 'erp', 'interest')

@admin.register(Audience)
class AudienceAdmin(admin.ModelAdmin):
    list_display = ('name', 'event', 'branch', 'semester', 'erp')
    list_filter = ('branch', 'event')
    search_fields = ('name', 'erp')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('name', 'event', 'amount', 'modeOfPayment', 'transactionId', 'coordinatorCheck', 'status', 'createdAt')
    list_filter = ('coordinatorCheck', 'status', 'modeOfPayment', 'event')
    search_fields = ('name', 'transactionId', 'erp')

@admin.register(Pass)
class PassAdmin(admin.ModelAdmin):
    list_display = ('name', 'event', 'registrationType', 'date', 'uuid', 'isCheckedIn', 'checkedInAt')
    list_filter = ('isCheckedIn', 'registrationType', 'event')
    search_fields = ('name', 'uuid', 'event__name')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'event', 'targetRole', 'createdBy', 'createdAt')
    list_filter = ('targetRole', 'createdAt')
    search_fields = ('title', 'description')

@admin.register(Memories)
class MemoriesAdmin(admin.ModelAdmin):
    list_display = ('title', 'event', 'subevent', 'uploadedBy', 'createdAt')
    list_filter = ('event', 'createdAt')
    search_fields = ('title', 'event__name')

@admin.register(AttendanceLog)
class AttendanceLogAdmin(admin.ModelAdmin):
    list_display = ('pass_obj', 'scanned_by', 'status', 'scanned_at')
    list_filter = ('status', 'scanned_at')
    search_fields = ('pass_obj__name', 'pass_obj__uuid')
