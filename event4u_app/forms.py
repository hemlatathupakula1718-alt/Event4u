from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import (
    UserProfile, Coordinator, SubCoordinator, Proposal, Event, SubEvent,
    Volunteer, Participant, Audience, Payment, Notification, Memories,
    BRANCH, SEMESTER, MODE_OF_PAYMENT, CATEGORY_CHOICES, REGISTRATION_TYPES
)

class ModernLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control form-control-lg',
        'placeholder': 'Enter Username or ERP Number',
        'autocomplete': 'username'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control form-control-lg',
        'placeholder': 'Enter Password',
        'autocomplete': 'current-password'
    }))


class StudentRegistrationForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Unique Username (e.g. john_doe)'
    }))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control', 'placeholder': 'name@example.com'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'placeholder': 'Create Strong Password'
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'placeholder': 'Confirm Password'
    }))
    fullName = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Full Name'
    }))
    branch = forms.ChoiceField(choices=BRANCH, widget=forms.Select(attrs={'class': 'form-select'}))
    semester = forms.ChoiceField(choices=SEMESTER, widget=forms.Select(attrs={'class': 'form-select'}))
    rollNumber = forms.IntegerField(required=True, widget=forms.NumberInput(attrs={
        'class': 'form-control', 'placeholder': 'Roll Number (e.g. 101)'
    }))
    erp = forms.IntegerField(required=True, widget=forms.NumberInput(attrs={
        'class': 'form-control', 'placeholder': 'College ERP Number (e.g. 200600101)'
    }))
    phone = forms.CharField(max_length=15, required=True, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'WhatsApp / Mobile Number'
    }))

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match. Please re-enter.")
        return cleaned_data


class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['fullName', 'branch', 'semester', 'rollNumber', 'erp', 'phone', 'avatar']
        widgets = {
            'fullName': forms.TextInput(attrs={'class': 'form-control'}),
            'branch': forms.Select(attrs={'class': 'form-select'}),
            'semester': forms.Select(attrs={'class': 'form-select'}),
            'rollNumber': forms.NumberInput(attrs={'class': 'form-control'}),
            'erp': forms.NumberInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
        }


class ProposalForm(forms.ModelForm):
    class Meta:
        model = Proposal
        fields = ['title', 'description', 'feeApplicableForPerStudent', 'fundRecieveFromCollege', 'estimatedAudience']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Event Proposal Title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Detailed Event Objective & Proposal Details'}),
            'feeApplicableForPerStudent': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Fee Per Student (₹)'}),
            'fundRecieveFromCollege': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'College Fund Requested (₹)'}),
            'estimatedAudience': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Estimated Attendees'}),
        }


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name', 'category', 'description', 'venue', 'eventDate', 'upi', 'totalMoney', 'image', 'registrationOpen']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Event Name'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'venue': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Auditorium / Ground / Lab'}),
            'eventDate': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'upi': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'college.fest@upi'}),
            'totalMoney': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Total Allocated Budget'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'registrationOpen': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class SubEventForm(forms.ModelForm):
    class Meta:
        model = SubEvent
        fields = ['event', 'name', 'subcoordinator', 'description', 'venue', 'eventDate', 'totalBudget', 'image']
        widgets = {
            'event': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Code Clash, Battle of Bands, Robo Race'}),
            'subcoordinator': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Sub-event rules, rounds, judging criteria & timeline'}),
            'venue': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Lab 402, Stage 1, Seminar Hall'}),
            'eventDate': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'totalBudget': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Allocated Track Budget (₹)'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }


class SubCoordinatorAppointmentForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Assign User Account (Username)'}))
    password = forms.CharField(required=False, widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Default password if creating new user'}))

    class Meta:
        model = SubCoordinator
        fields = ['name', 'branch', 'semester', 'rollNumber', 'erp', 'event']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'branch': forms.Select(attrs={'class': 'form-select'}),
            'semester': forms.Select(attrs={'class': 'form-select'}),
            'rollNumber': forms.NumberInput(attrs={'class': 'form-control'}),
            'erp': forms.NumberInput(attrs={'class': 'form-control'}),
            'event': forms.Select(attrs={'class': 'form-select'}),
        }


class VolunteerForm(forms.ModelForm):
    class Meta:
        model = Volunteer
        fields = ['event', 'subevent', 'name', 'branch', 'semester', 'rollNumber', 'erp', 'work']
        widgets = {
            'event': forms.Select(attrs={'class': 'form-select'}),
            'subevent': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'branch': forms.Select(attrs={'class': 'form-select'}),
            'semester': forms.Select(attrs={'class': 'form-select'}),
            'rollNumber': forms.NumberInput(attrs={'class': 'form-control'}),
            'erp': forms.NumberInput(attrs={'class': 'form-control'}),
            'work': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Describe your skills, available timings or preferred duties'}),
        }


class ParticipantForm(forms.ModelForm):
    class Meta:
        model = Participant
        fields = ['event', 'subevent', 'name', 'branch', 'semester', 'rollNumber', 'erp', 'interest']
        widgets = {
            'event': forms.Select(attrs={'class': 'form-select'}),
            'subevent': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'branch': forms.Select(attrs={'class': 'form-select'}),
            'semester': forms.Select(attrs={'class': 'form-select'}),
            'rollNumber': forms.NumberInput(attrs={'class': 'form-control'}),
            'erp': forms.NumberInput(attrs={'class': 'form-control'}),
            'interest': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'e.g. Solo Dance, Band Vocalist, Coding Competition'}),
        }


class AudienceForm(forms.ModelForm):
    class Meta:
        model = Audience
        fields = ['event', 'name', 'branch', 'semester', 'rollNumber', 'erp']
        widgets = {
            'event': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'branch': forms.Select(attrs={'class': 'form-select'}),
            'semester': forms.Select(attrs={'class': 'form-select'}),
            'rollNumber': forms.NumberInput(attrs={'class': 'form-control'}),
            'erp': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['event', 'name', 'branch', 'semester', 'rollNumber', 'erp', 'whatsAppNumber', 'mobileNumber', 'modeOfPayment', 'amount', 'transactionId', 'paymentRecieptImage']
        widgets = {
            'event': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'branch': forms.Select(attrs={'class': 'form-select'}),
            'semester': forms.Select(attrs={'class': 'form-select'}),
            'rollNumber': forms.NumberInput(attrs={'class': 'form-control'}),
            'erp': forms.NumberInput(attrs={'class': 'form-control'}),
            'whatsAppNumber': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'WhatsApp Contact'}),
            'mobileNumber': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mobile Number'}),
            'modeOfPayment': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'transactionId': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'UPI UTR / Reference ID'}),
            'paymentRecieptImage': forms.FileInput(attrs={'class': 'form-control'}),
        }


class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = ['event', 'title', 'description', 'targetRole']
        widgets = {
            'event': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Announcement Headline'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Notification message body'}),
            'targetRole': forms.Select(attrs={'class': 'form-select'}),
        }


class MemoryUploadForm(forms.ModelForm):
    class Meta:
        model = Memories
        fields = ['event', 'subevent', 'title', 'image']
        widgets = {
            'event': forms.Select(attrs={'class': 'form-select'}),
            'subevent': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Memory Title / Caption'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }