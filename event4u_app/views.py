import io
import uuid
import qrcode
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.db.models import Sum, Count, Q
from django.core.files.base import ContentFile

from .models import (
    UserProfile, Coordinator, SubCoordinator, Proposal, Event, SubEvent,
    Volunteer, Participant, Audience, Payment, Notification, Memories, Pass, AttendanceLog
)
from .forms import (
    ModernLoginForm, StudentRegistrationForm, UserProfileUpdateForm,
    ProposalForm, EventForm, SubEventForm, SubCoordinatorAppointmentForm,
    VolunteerForm, ParticipantForm, AudienceForm, PaymentForm,
    NotificationForm, MemoryUploadForm
)


# ==========================================
# Role Helper & Dispatcher
# ==========================================

def get_user_role(user):
    if not user.is_authenticated:
        return 'ANONYMOUS'
    profile = getattr(user, 'profile', None)
    if profile:
        return profile.role
    if user.is_superuser:
        return 'PRINCIPAL'
    if user.is_staff:
        return 'COORDINATOR'
    return 'STUDENT'


# ==========================================
# Authentication & Landing Views
# ==========================================

def home(request):
    """
    Modern Public Landing Page for Event4u
    """
    featured_events = Event.objects.filter(status='Active').order_by('-createdAt')[:6]
    all_events = Event.objects.all().order_by('-createdAt')[:9]
    notifications = Notification.objects.all().order_by('-createdAt')[:5]
    memories = Memories.objects.all().order_by('-createdAt')[:8]
    
    total_events_count = Event.objects.count()
    total_students_count = UserProfile.objects.filter(role='STUDENT').count()
    total_passes_count = Pass.objects.count()

    context = {
        'featured_events': featured_events,
        'all_events': all_events,
        'notifications': notifications,
        'memories': memories,
        'total_events_count': total_events_count,
        'total_students_count': total_students_count,
        'total_passes_count': total_passes_count,
    }
    return render(request, 'home/home.html', context)


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = ModernLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password. Please try again.")
    else:
        form = ModernLoginForm()

    return render(request, 'event4u/login.html', {'form': form})


@login_required(login_url='login')
def logout_view(request):
    logout(request)
    messages.info(request, "You have been successfully logged out.")
    return redirect('home')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already exists. Please choose a different one.")
                return render(request, 'register/register.html', {'form': form})
                
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=form.cleaned_data['fullName'].split()[0],
                last_name=' '.join(form.cleaned_data['fullName'].split()[1:]) if len(form.cleaned_data['fullName'].split()) > 1 else ''
            )
            
            UserProfile.objects.create(
                user=user,
                role='STUDENT',
                fullName=form.cleaned_data['fullName'],
                branch=form.cleaned_data['branch'],
                semester=form.cleaned_data['semester'],
                rollNumber=form.cleaned_data['rollNumber'],
                erp=form.cleaned_data['erp'],
                phone=form.cleaned_data['phone'],
            )

            login(request, user)
            messages.success(request, f"Welcome to Event4u, {user.first_name}! Your student profile has been created.")
            return redirect('dashboard')
        else:
            messages.error(request, "Please correct the errors in the form.")
    else:
        form = StudentRegistrationForm()

    return render(request, 'register/register.html', {'form': form})


# ==========================================
# Unified Smart Dashboard Dispatcher
# ==========================================

@login_required(login_url='login')
def dashboard(request):
    role = get_user_role(request.user)

    if role == 'PRINCIPAL' or request.user.is_superuser:
        return principal_dashboard(request)
    elif role == 'HOD':
        return hod_dashboard(request)
    elif role == 'COORDINATOR':
        return coordinator_dashboard(request)
    elif role == 'SUB_COORDINATOR':
        return subcoordinator_dashboard(request)
    else:
        return student_dashboard(request)


# ==========================================
# Role-Specific Dashboards
# ==========================================

@login_required(login_url='login')
def principal_dashboard(request):
    events = Event.objects.all().order_by('-createdAt')
    pending_proposals = Proposal.objects.filter(HoD_Approval=True, Principal_Approval=False).order_by('-createdAt')
    all_proposals = Proposal.objects.all().order_by('-createdAt')
    coordinators = Coordinator.objects.all()
    
    total_budget_allocated = Event.objects.aggregate(Sum('totalMoney'))['totalMoney__sum'] or 0
    total_verified_payments = Payment.objects.filter(coordinatorCheck=True).aggregate(Sum('amount'))['amount__sum'] or 0
    total_attendees = Pass.objects.count()
    active_events_count = Event.objects.filter(status='Active').count()

    context = {
        'events': events,
        'pending_proposals': pending_proposals,
        'all_proposals': all_proposals,
        'coordinators': coordinators,
        'total_budget_allocated': total_budget_allocated,
        'total_verified_payments': total_verified_payments,
        'total_attendees': total_attendees,
        'active_events_count': active_events_count,
        'role_title': 'Principal Executive Control Center'
    }
    return render(request, 'dashboards/principal_dashboard.html', context)


@login_required(login_url='login')
def hod_dashboard(request):
    user_branch = getattr(getattr(request.user, 'profile', None), 'branch', 'Computer')
    
    # Proposals under this department or general
    pending_proposals = Proposal.objects.filter(HoD_Approval=False, coordinator__branch=user_branch).order_by('-createdAt')
    approved_proposals = Proposal.objects.filter(HoD_Approval=True, coordinator__branch=user_branch).order_by('-createdAt')
    department_events = Event.objects.filter(coordinator__branch=user_branch).order_by('-createdAt')
    
    dept_participants = Participant.objects.filter(branch=user_branch).count()
    dept_volunteers = Volunteer.objects.filter(branch=user_branch).count()

    context = {
        'pending_proposals': pending_proposals,
        'approved_proposals': approved_proposals,
        'department_events': department_events,
        'dept_participants': dept_participants,
        'dept_volunteers': dept_volunteers,
        'user_branch': user_branch,
        'role_title': f'HoD Dashboard ({user_branch} Department)'
    }
    return render(request, 'dashboards/hod_dashboard.html', context)


@login_required(login_url='login')
def coordinator_dashboard(request):
    # Find coordinator profile
    coordinator = Coordinator.objects.filter(user=request.user).first()
    if not coordinator:
        coordinator = Coordinator.objects.filter(name__icontains=request.user.first_name).first()
    
    events = Event.objects.filter(coordinator=coordinator) if coordinator else Event.objects.all()
    proposals = Proposal.objects.filter(coordinator=coordinator) if coordinator else Proposal.objects.all()
    subevents = SubEvent.objects.filter(coordinator=coordinator) if coordinator else SubEvent.objects.all()
    
    # Payments for coordinator's events
    payments = Payment.objects.filter(event__in=events).order_by('-createdAt') if events.exists() else Payment.objects.all().order_by('-createdAt')
    
    # Subcoordinators under this coordinator
    subcoordinators = SubCoordinator.objects.filter(coordinator=coordinator) if coordinator else SubCoordinator.objects.all()

    subevent_form = SubEventForm()
    proposal_form = ProposalForm()
    subcoord_form = SubCoordinatorAppointmentForm()

    context = {
        'coordinator': coordinator,
        'events': events,
        'proposals': proposals,
        'subevents': subevents,
        'payments': payments,
        'subcoordinators': subcoordinators,
        'subevent_form': subevent_form,
        'proposal_form': proposal_form,
        'subcoord_form': subcoord_form,
        'role_title': 'Faculty Coordinator Management Hub'
    }
    return render(request, 'dashboards/coordinator_dashboard.html', context)


@login_required(login_url='login')
def create_subevent(request):
    """
    Allows Faculty Coordinator or Admin to create a new Sub-Event & Competition Track.
    """
    coordinator = Coordinator.objects.filter(user=request.user).first()
    if not coordinator and not request.user.is_superuser:
        coordinator = Coordinator.objects.first()

    if request.method == 'POST':
        form = SubEventForm(request.POST, request.FILES)
        if form.is_valid():
            subevent = form.save(commit=False)
            if coordinator:
                subevent.coordinator = coordinator
            else:
                subevent.coordinator = subevent.event.coordinator
            subevent.save()
            messages.success(request, f"Sub-Event '{subevent.name}' created successfully under {subevent.event.name} with budget of ₹{subevent.totalBudget}!")
            return redirect('coordinator-dashboard')
        else:
            messages.error(request, "Please correct the errors in the sub-event form.")
    return redirect('coordinator-dashboard')


@login_required(login_url='login')
def delete_subevent(request, pid):
    """
    Allows Coordinator to delete a sub-event.
    """
    subevent = get_object_or_404(SubEvent, pk=pid)
    name = subevent.name
    subevent.delete()
    messages.success(request, f"Sub-Event '{name}' has been deleted.")
    return redirect('coordinator-dashboard')


@login_required(login_url='login')
def appoint_subcoordinator(request):
    """
    Allows Faculty Coordinator to appoint a student as Sub-Coordinator.
    """
    coordinator = Coordinator.objects.filter(user=request.user).first()
    if not coordinator and not request.user.is_superuser:
        coordinator = Coordinator.objects.first()

    if request.method == 'POST':
        form = SubCoordinatorAppointmentForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password') or 'ycc@123'
            
            sub_user, created = User.objects.get_or_create(username=username, defaults={'email': f'{username}@ycc.edu'})
            if created or password:
                sub_user.set_password(password)
                sub_user.save()
                
            UserProfile.objects.update_or_create(
                user=sub_user,
                defaults={
                    'role': 'SUB_COORDINATOR',
                    'fullName': form.cleaned_data.get('name'),
                    'branch': form.cleaned_data.get('branch'),
                    'semester': form.cleaned_data.get('semester'),
                    'rollNumber': form.cleaned_data.get('rollNumber'),
                    'erp': form.cleaned_data.get('erp'),
                }
            )
            
            subcoord = form.save(commit=False)
            subcoord.user = sub_user
            if coordinator:
                subcoord.coordinator = coordinator
            subcoord.save()
            messages.success(request, f"Student {subcoord.name} successfully appointed as Sub-Coordinator for {subcoord.event.name}!")
            return redirect('coordinator-dashboard')
        else:
            messages.error(request, "Failed to appoint sub-coordinator. Please verify form fields.")
    return redirect('coordinator-dashboard')



@login_required(login_url='login')
def subcoordinator_dashboard(request):
    subcoord = SubCoordinator.objects.filter(user=request.user).first()
    if not subcoord:
        subcoord = SubCoordinator.objects.filter(name__icontains=request.user.first_name).first()
    
    subevents = SubEvent.objects.filter(subcoordinator=subcoord) if subcoord else SubEvent.objects.all()
    volunteers = Volunteer.objects.filter(subevent__in=subevents) if subevents.exists() else Volunteer.objects.all()
    participants = Participant.objects.filter(subevent__in=subevents) if subevents.exists() else Participant.objects.all()
    
    recent_checkins = AttendanceLog.objects.filter(scanned_by=request.user).order_by('-scanned_at')[:10]

    context = {
        'subcoord': subcoord,
        'subevents': subevents,
        'volunteers': volunteers,
        'participants': participants,
        'recent_checkins': recent_checkins,
        'role_title': 'Sub-Coordinator Event Operations'
    }
    return render(request, 'dashboards/subcoordinator_dashboard.html', context)


@login_required(login_url='login')
def student_dashboard(request):
    user_passes = Pass.objects.filter(user=request.user).order_by('-createdAt')
    user_payments = Payment.objects.filter(user=request.user).order_by('-createdAt')
    
    registered_participants = Participant.objects.filter(user=request.user)
    registered_volunteers = Volunteer.objects.filter(user=request.user)
    registered_audience = Audience.objects.filter(user=request.user)
    
    available_events = Event.objects.filter(status='Active', registrationOpen=True).order_by('-createdAt')
    notifications = Notification.objects.all().order_by('-createdAt')[:5]

    context = {
        'user_passes': user_passes,
        'user_payments': user_payments,
        'registered_participants': registered_participants,
        'registered_volunteers': registered_volunteers,
        'registered_audience': registered_audience,
        'available_events': available_events,
        'notifications': notifications,
        'role_title': 'Student Experience & Passes Portal'
    }
    return render(request, 'dashboards/student_dashboard.html', context)


# ==========================================
# Events & Sub-Events Views
# ==========================================

@login_required(login_url='login')
def events(request):
    category = request.GET.get('category', None)
    search_query = request.GET.get('q', None)
    
    events_qs = Event.objects.all().order_by('-createdAt')
    if category:
        events_qs = events_qs.filter(category=category)
    if search_query:
        events_qs = events_qs.filter(Q(name__icontains=search_query) | Q(description__icontains=search_query) | Q(coordinator__name__icontains=search_query))

    context = {
        'events': events_qs,
        'selected_category': category,
        'search_query': search_query,
    }
    return render(request, 'event4u/events.html', context)


@login_required(login_url='login')
def event_data(request, pid):
    event = get_object_or_404(Event, pk=pid)
    subevents = SubEvent.objects.filter(event=event)
    
    # Check if current user is registered in any form
    user_pass = Pass.objects.filter(user=request.user, event=event).first()
    user_payment = Payment.objects.filter(user=request.user, event=event).first()
    
    is_registered_participant = Participant.objects.filter(user=request.user, event=event).exists()
    is_registered_volunteer = Volunteer.objects.filter(user=request.user, event=event).exists()
    is_registered_audience = Audience.objects.filter(user=request.user, event=event).exists()

    context = {
        'event': event,
        'subevents': subevents,
        'user_pass': user_pass,
        'user_payment': user_payment,
        'is_registered': (is_registered_participant or is_registered_volunteer or is_registered_audience),
        'is_registered_participant': is_registered_participant,
        'is_registered_volunteer': is_registered_volunteer,
        'is_registered_audience': is_registered_audience,
    }
    return render(request, 'event4u/event_data.html', context)


# ==========================================
# Proposal Management & Approval Workflow
# ==========================================

@login_required(login_url='login')
def proposals_view(request):
    role = get_user_role(request.user)
    
    if request.method == 'POST':
        form = ProposalForm(request.POST)
        if form.is_valid():
            coordinator = Coordinator.objects.filter(user=request.user).first()
            if not coordinator:
                coordinator = Coordinator.objects.first()
            
            proposal = form.save(commit=False)
            proposal.coordinator = coordinator
            proposal.status = 'Pending'
            proposal.save()
            messages.success(request, "Event proposal submitted successfully! Awaiting HoD and Principal review.")
            return redirect('proposals')
    else:
        form = ProposalForm()

    all_proposals = Proposal.objects.all().order_by('-createdAt')

    context = {
        'proposals': all_proposals,
        'form': form,
        'can_approve_hod': (role in ['HOD', 'PRINCIPAL'] or request.user.is_superuser),
        'can_approve_principal': (role == 'PRINCIPAL' or request.user.is_superuser),
    }
    return render(request, 'event4u/proposals.html', context)


@login_required(login_url='login')
def approve_proposal_hod(request, pid):
    proposal = get_object_or_404(Proposal, pk=pid)
    proposal.HoD_Approval = True
    proposal.save()
    messages.success(request, f"Proposal '{proposal.title}' endorsed by HoD! Forwarded to Principal.")
    return redirect(request.META.get('HTTP_REFERER', 'proposals'))


@login_required(login_url='login')
def approve_proposal_principal(request, pid):
    proposal = get_object_or_404(Proposal, pk=pid)
    proposal.Principal_Approval = True
    proposal.status = 'Active'
    proposal.save()

    # Automatically initialize Event if not present
    event, created = Event.objects.get_or_create(
        name=proposal.title,
        coordinator=proposal.coordinator,
        defaults={
            'description': proposal.description,
            'status': 'Active',
            'totalMoney': proposal.fundRecieveFromCollege,
            'eventDate': timezone.now() + timezone.timedelta(days=14),
            'registrationOpen': True,
        }
    )
    
    Notification.objects.create(
        event=event,
        title=f"🎉 Event Approved: {event.name}",
        description=f"Great news! The event '{event.name}' has been formally sanctioned by the Principal. Registrations are now active!",
        targetRole='ALL',
        createdBy=request.user
    )

    messages.success(request, f"Proposal '{proposal.title}' sanctioned by Principal! Event is now LIVE.")
    return redirect(request.META.get('HTTP_REFERER', 'proposals'))


@login_required(login_url='login')
def reject_proposal(request, pid):
    proposal = get_object_or_404(Proposal, pk=pid)
    remarks = request.POST.get('remarks', 'Budget or safety revision requested.')
    proposal.status = 'Rejected'
    proposal.rejectionRemarks = remarks
    proposal.save()
    messages.warning(request, f"Proposal '{proposal.title}' marked as Rejected.")
    return redirect(request.META.get('HTTP_REFERER', 'proposals'))


# ==========================================
# Registration & Payment Flows
# ==========================================

@login_required(login_url='login')
def volunteer(request):
    profile = getattr(request.user, 'profile', None)
    initial_data = {}
    if profile:
        initial_data = {
            'name': profile.display_name,
            'branch': profile.branch,
            'semester': profile.semester,
            'rollNumber': profile.rollNumber,
            'erp': profile.erp,
        }

    if request.method == 'POST':
        form = VolunteerForm(request.POST)
        if form.is_valid():
            vol = form.save(commit=False)
            vol.user = request.user
            vol.isVolunteer = True
            vol.save()
            
            # Generate Pass
            Pass.objects.get_or_create(
                user=request.user,
                event=vol.event,
                defaults={
                    'name': vol.name,
                    'subevent': vol.subevent,
                    'registrationType': 'VOLUNTEER',
                    'date': vol.event.eventDate.date() if vol.event.eventDate else timezone.now().date(),
                    'uuid': uuid.uuid4()
                }
            )
            
            messages.success(request, f"Volunteer application submitted for {vol.subevent.name}! Your volunteer pass has been generated.")
            return redirect('dashboard')
    else:
        form = VolunteerForm(initial=initial_data)

    return render(request, 'event4u/volunteer.html', {'form': form})


@login_required(login_url='login')
def participant(request):
    profile = getattr(request.user, 'profile', None)
    initial_data = {}
    if profile:
        initial_data = {
            'name': profile.display_name,
            'branch': profile.branch,
            'semester': profile.semester,
            'rollNumber': profile.rollNumber,
            'erp': profile.erp,
        }

    if request.method == 'POST':
        form = ParticipantForm(request.POST)
        if form.is_valid():
            part = form.save(commit=False)
            part.user = request.user
            part.isParticipant = True
            part.save()

            # Generate Pass
            Pass.objects.get_or_create(
                user=request.user,
                event=part.event,
                defaults={
                    'name': part.name,
                    'subevent': part.subevent,
                    'registrationType': 'PARTICIPANT',
                    'date': part.event.eventDate.date() if part.event.eventDate else timezone.now().date(),
                    'uuid': uuid.uuid4()
                }
            )

            messages.success(request, f"Successfully registered as Participant for {part.subevent.name}! Proceed with fee payment to confirm pass.")
            return redirect('payment')
    else:
        form = ParticipantForm(initial=initial_data)

    return render(request, 'event4u/participant.html', {'form': form})


@login_required(login_url='login')
def audience(request):
    profile = getattr(request.user, 'profile', None)
    initial_data = {}
    if profile:
        initial_data = {
            'name': profile.display_name,
            'branch': profile.branch,
            'semester': profile.semester,
            'rollNumber': profile.rollNumber,
            'erp': profile.erp,
        }

    if request.method == 'POST':
        form = AudienceForm(request.POST)
        if form.is_valid():
            aud = form.save(commit=False)
            aud.user = request.user
            aud.isAudience = True
            aud.save()

            # Generate Pass
            Pass.objects.get_or_create(
                user=request.user,
                event=aud.event,
                defaults={
                    'name': aud.name,
                    'registrationType': 'AUDIENCE',
                    'date': aud.event.eventDate.date() if aud.event.eventDate else timezone.now().date(),
                    'uuid': uuid.uuid4()
                }
            )

            messages.success(request, f"Audience seat confirmed for {aud.event.name}! Complete payment to activate entry QR badge.")
            return redirect('payment')
    else:
        form = AudienceForm(initial=initial_data)

    return render(request, 'event4u/audience.html', {'form': form})


@login_required(login_url='login')
def payment(request):
    profile = getattr(request.user, 'profile', None)
    initial_data = {}
    if profile:
        initial_data = {
            'name': profile.display_name,
            'branch': profile.branch,
            'semester': profile.semester,
            'rollNumber': profile.rollNumber,
            'erp': profile.erp,
            'whatsAppNumber': profile.phone or '9876543210',
            'mobileNumber': profile.phone or '9876543210',
            'amount': 150,
        }

    if request.method == 'POST':
        form = PaymentForm(request.POST, request.FILES)
        if form.is_valid():
            pay = form.save(commit=False)
            pay.user = request.user
            pay.coordinatorCheck = True  # Auto-verified for smooth mock workflow
            pay.status = 'Verified'
            pay.verifiedAt = timezone.now()
            pay.save()

            # Ensure Pass exists and is linked
            pass_obj, created = Pass.objects.get_or_create(
                user=request.user,
                event=pay.event,
                defaults={
                    'name': pay.name,
                    'date': pay.event.eventDate.date() if pay.event.eventDate else timezone.now().date(),
                    'uuid': uuid.uuid4()
                }
            )

            messages.success(request, f"Payment of ₹{pay.amount} confirmed for {pay.event.name}! Your Digital Pass is ready to download.")
            return redirect('generate-pass', event_id=pay.event.id)
    else:
        form = PaymentForm(initial=initial_data)

    return render(request, 'event4u/payment.html', {'form': form})


@login_required(login_url='login')
def toggle_payment_verification(request, pid):
    payment_obj = get_object_or_404(Payment, pk=pid)
    payment_obj.coordinatorCheck = not payment_obj.coordinatorCheck
    payment_obj.status = 'Verified' if payment_obj.coordinatorCheck else 'Rejected'
    payment_obj.verifiedAt = timezone.now() if payment_obj.coordinatorCheck else None
    payment_obj.save()
    messages.success(request, f"Payment status for {payment_obj.name} updated to {payment_obj.status}.")
    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))


# ==========================================
# Digital Pass & Verifiable QR Engine
# ==========================================

@login_required(login_url='login')
def generate_pass(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    
    pass_obj = Pass.objects.filter(user=request.user, event=event).first()
    if not pass_obj:
        pass_obj = Pass.objects.create(
            name=request.user.first_name or request.user.username,
            user=request.user,
            event=event,
            date=event.eventDate.date() if event.eventDate else timezone.now().date(),
            uuid=uuid.uuid4()
        )

    payment_record = Payment.objects.filter(user=request.user, event=event).first()
    profile = getattr(request.user, 'profile', None)

    context = {
        'pass': pass_obj,
        'event': event,
        'payment': payment_record,
        'profile': profile,
    }
    return render(request, 'event4u/pass.html', context)


@login_required(login_url='login')
def generate_qr(request):
    """
    Generates a secure QR Code image for the authenticated user's pass
    """
    event_id = request.GET.get('event_id', None)
    if event_id:
        pass_obj = Pass.objects.filter(user=request.user, event_id=event_id).first()
    else:
        pass_obj = Pass.objects.filter(user=request.user).first()
        
    if not pass_obj:
        # Generate on the fly
        event = Event.objects.first()
        pass_obj = Pass.objects.create(
            name=request.user.username,
            user=request.user,
            event=event,
            date=timezone.now().date(),
            uuid=uuid.uuid4()
        )

    # Verifiable QR payload
    qr_data = f"EVENT4U|PASS:{pass_obj.uuid}|USER:{request.user.username}|EVENT:{pass_obj.event.name}|DATE:{pass_obj.date}"
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#0f172a", back_color="#ffffff")

    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)

    response = HttpResponse(buffer.getvalue(), content_type='image/png')
    response['Content-Disposition'] = f'inline; filename="event4u_pass_{pass_obj.uuid.hex[:8]}.png"'
    return response


# ==========================================
# QR Scanner & Live Verification API
# ==========================================

@login_required(login_url='login')
def scanner_page(request):
    """
    Interactive Live Pass Scanner interface for Coordinators & Sub-Coordinators
    """
    recent_logs = AttendanceLog.objects.all().order_by('-scanned_at')[:15]
    context = {
        'recent_logs': recent_logs,
        'role_title': 'Gate Pass Scanner & Attendance Verification'
    }
    return render(request, 'event4u/scanner.html', context)


@login_required(login_url='login')
def verify_pass_api(request):
    """
    REST API endpoint for scanning / looking up pass UUID
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST request required'}, status=400)

    raw_qr = request.POST.get('qr_data', '').strip()
    pass_uuid_str = request.POST.get('pass_uuid', '').strip()

    pass_uuid = None
    if raw_qr:
        # Extract UUID from "EVENT4U|PASS:<uuid>|..."
        if "PASS:" in raw_qr:
            try:
                pass_uuid = raw_qr.split("PASS:")[1].split("|")[0].strip()
            except Exception:
                pass_uuid = raw_qr
        else:
            pass_uuid = raw_qr
    elif pass_uuid_str:
        pass_uuid = pass_uuid_str

    if not pass_uuid:
        return JsonResponse({'status': 'error', 'message': 'No Pass ID or QR code data provided.'})

    try:
        pass_obj = Pass.objects.filter(Q(uuid=pass_uuid) | Q(name__iexact=pass_uuid)).first()
        if not pass_obj:
            return JsonResponse({'status': 'invalid', 'message': '❌ Pass NOT Found! Invalid or Counterfeit Pass.'})

        already_checked_in = pass_obj.isCheckedIn
        
        # Mark Check-In
        pass_obj.isCheckedIn = True
        pass_obj.checkedInAt = timezone.now()
        pass_obj.checkedInBy = request.user
        pass_obj.save()

        # Log Attendance
        AttendanceLog.objects.create(
            pass_obj=pass_obj,
            scanned_by=request.user,
            status='Approved' if not already_checked_in else 'Duplicate_Scan',
            remarks='Verified via Scanner'
        )

        user_profile = getattr(pass_obj.user, 'profile', None) if pass_obj.user else None

        return JsonResponse({
            'status': 'success' if not already_checked_in else 'duplicate',
            'already_checked_in': already_checked_in,
            'message': '✅ Entry Verified & Attendance Marked!' if not already_checked_in else '⚠️ Warning: Pass was already checked in earlier!',
            'attendee_name': pass_obj.name,
            'event_name': pass_obj.event.name,
            'subevent_name': pass_obj.subevent.name if pass_obj.subevent else 'Main Event',
            'registration_type': pass_obj.registrationType,
            'roll_number': user_profile.rollNumber if user_profile else 'N/A',
            'erp_number': user_profile.erp if user_profile else 'N/A',
            'branch': user_profile.branch if user_profile else 'N/A',
            'checked_in_at': timezone.localtime(pass_obj.checkedInAt).strftime('%d %b %Y, %I:%M %p'),
            'pass_uuid': str(pass_obj.uuid),
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Server Verification Error: {str(e)}'})


# ==========================================
# ReportLab Dynamic PDF Audit Report Engine
# ==========================================

@login_required(login_url='login')
def report(request):
    events = Event.objects.all().order_by('-createdAt')
    context = {
        'events': events,
        'role_title': 'Event Financial & Participation Audit Reports'
    }
    return render(request, 'event4u/report.html', context)


@login_required(login_url='login')
def generatereport(request, pid):
    """
    Generates dynamic in-memory ReportLab PDF with college branding and financial stats
    """
    event = get_object_or_404(Event, pk=pid)
    coordinator = event.coordinator
    subevents = SubEvent.objects.filter(event=event)
    
    students_count = Audience.objects.filter(event=event).count()
    participants_count = Participant.objects.filter(event=event).count()
    volunteers_count = Volunteer.objects.filter(event=event).count()

    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
    from reportlab.lib import colors

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#1e293b'),
        alignment=1
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#4338ca'),
        spaceBefore=12,
        spaceAfter=6
    )
    meta_style = ParagraphStyle(
        'DocMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#475569')
    )

    story = []

    # Institution Header
    story.append(Paragraph("EVENT4U • COLLEGE EVENT MANAGEMENT SYSTEM", ParagraphStyle('Inst', fontName='Helvetica-Bold', fontSize=10, alignment=1, textColor=colors.HexColor('#6366f1'))))
    story.append(Paragraph(f"OFFICIAL EVENT AUDIT & COMPLETION REPORT", title_style))
    story.append(Paragraph(f"Event: <b>{event.name}</b> • Category: {event.category}", ParagraphStyle('Sub', fontName='Helvetica', fontSize=12, alignment=1, textColor=colors.HexColor('#64748b'))))
    story.append(Spacer(1, 0.15 * inch))

    # Event Meta Table
    meta_data = [
        ["Event Name", event.name, "Event Date", event.eventDate.strftime('%d %b %Y, %I:%M %p') if event.eventDate else "TBD"],
        ["Coordinator", coordinator.name if coordinator else "N/A", "Department", coordinator.branch if coordinator else "Computer"],
        ["Venue", event.venue, "Status", event.status],
    ]
    meta_table = Table(meta_data, colWidths=[1.3*inch, 2.2*inch, 1.3*inch, 2.2*inch])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1e293b')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 0.2 * inch))

    # Participation Breakdown
    story.append(Paragraph("1. Student Participation Metrics", subtitle_style))
    part_data = [
        ["Audience / Attendees", "Registered Participants", "Student Volunteers", "Total Footfall"],
        [str(students_count), str(participants_count), str(volunteers_count), str(students_count + participants_count + volunteers_count)]
    ]
    part_table = Table(part_data, colWidths=[1.75*inch, 1.75*inch, 1.75*inch, 1.75*inch])
    part_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4338ca')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#f1f5f9')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#94a3b8')),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(part_table)
    story.append(Spacer(1, 0.2 * inch))

    # Sub-Events & Budget Utilization
    story.append(Paragraph("2. Sub-Events Financial & Execution Breakdown", subtitle_style))
    budget_table_data = [["Sub Event Name", "Sub-Coordinator", "Allocated Budget", "Utilized Budget", "Balance (₹)"]]
    
    total_alloc = 0
    total_util = 0
    total_bal = 0
    
    for s in subevents:
        alloc = s.totalBudget or 0
        util = s.utiliseBudget or 0
        bal = max(0, alloc - util)
        total_alloc += alloc
        total_util += util
        total_bal += bal
        budget_table_data.append([
            s.name,
            s.subcoordinator.name if s.subcoordinator else "Unassigned",
            f"₹{alloc:,}",
            f"₹{util:,}",
            f"₹{bal:,}"
        ])
        
    budget_table_data.append([
        "TOTAL",
        "---",
        f"₹{total_alloc:,}",
        f"₹{total_util:,}",
        f"₹{total_bal:,}"
    ])

    sub_table = Table(budget_table_data, colWidths=[1.8*inch, 1.8*inch, 1.1*inch, 1.1*inch, 1.2*inch])
    sub_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e293b')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
        ('BACKGROUND', (0, 1), (-1, -2), colors.white),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e2e8f0')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(sub_table)
    story.append(Spacer(1, 0.2 * inch))

    # Summary & Signatures
    story.append(Paragraph("3. Executive Summary & Outcome", subtitle_style))
    summary_text = (
        f"The event '{event.name}' was executed in accordance with college guidelines. "
        f"A total of {students_count + participants_count + volunteers_count} attendees participated across all technical & cultural sub-events. "
        f"Total budget expenditure stood at ₹{total_util:,} with a remaining balance of ₹{total_bal:,} duly accounted for institutional records."
    )
    story.append(Paragraph(summary_text, meta_style))
    story.append(Spacer(1, 0.4 * inch))

    # Signatures
    sig_data = [
        ["____________________________", "____________________________", "____________________________"],
        ["Faculty Coordinator", "Head of Department (HoD)", "Principal / Director"],
        [coordinator.name if coordinator else "Prof. Advait", "Dr. Rajendra Pawar", "Dr. Suraj Sahani"]
    ]
    sig_table = Table(sig_data, colWidths=[2.3*inch, 2.3*inch, 2.3*inch])
    sig_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#334155')),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(sig_table)

    # Build PDF
    doc.build(story)
    buffer.seek(0)

    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Event4u_Report_{event.name.replace(" ", "_")}.pdf"'
    return response


# ==========================================
# Photo Memories Gallery
# ==========================================

@login_required(login_url='login')
def memories_view(request):
    event_id = request.GET.get('event', None)
    if event_id:
        memories = Memories.objects.filter(event_id=event_id).order_by('-createdAt')
    else:
        memories = Memories.objects.all().order_by('-createdAt')

    events = Event.objects.all()

    if request.method == 'POST':
        form = MemoryUploadForm(request.POST, request.FILES)
        if form.is_valid():
            mem = form.save(commit=False)
            mem.uploadedBy = request.user
            mem.save()
            messages.success(request, "Event memory photo uploaded successfully!")
            return redirect('memories')
    else:
        form = MemoryUploadForm()

    context = {
        'memories': memories,
        'events': events,
        'form': form,
        'selected_event': event_id,
        'role_title': 'Event Memories & Photo Album'
    }
    return render(request, 'event4u/memories.html', context)


# ==========================================
# Notifications Center
# ==========================================

@login_required(login_url='login')
def notification(request):
    notifications = Notification.objects.all().order_by('-createdAt')
    
    if request.method == 'POST':
        form = NotificationForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.createdBy = request.user
            note.save()
            messages.success(request, "Broadcast announcement published to students & staff!")
            return redirect('notification')
    else:
        form = NotificationForm()

    context = {
        'notifications': notifications,
        'form': form,
        'can_broadcast': request.user.is_staff or request.user.is_superuser or (getattr(getattr(request.user, 'profile', None), 'role', '') in ['PRINCIPAL', 'HOD', 'COORDINATOR']),
        'role_title': 'Campus Announcements & Notification Center'
    }
    return render(request, 'event4u/notification.html', context)


# ==========================================
# User Profile
# ==========================================

@login_required(login_url='login')
def profile(request):
    user_profile, created = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={
            'role': 'STUDENT',
            'fullName': request.user.get_full_name() or request.user.username,
            'branch': 'Computer',
            'semester': '6',
        }
    )

    if request.method == 'POST':
        form = UserProfileUpdateForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile details have been updated successfully!")
            return redirect('profile')
    else:
        form = UserProfileUpdateForm(instance=user_profile)

    context = {
        'profile': user_profile,
        'form': form,
        'role_title': 'My Account Profile'
    }
    return render(request, 'event4u/profile.html', context)
