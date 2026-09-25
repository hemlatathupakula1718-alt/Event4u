from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    # Landing & Authentication
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Smart Dashboards
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/principal/', views.principal_dashboard, name='principal-dashboard'),
    path('dashboard/hod/', views.hod_dashboard, name='hod-dashboard'),
    path('dashboard/coordinator/', views.coordinator_dashboard, name='coordinator-dashboard'),
    path('dashboard/subcoordinator/', views.subcoordinator_dashboard, name='subcoordinator-dashboard'),
    path('dashboard/student/', views.student_dashboard, name='student-dashboard'),

    # Events & Details
    path('events/', views.events, name='events'),
    path('event_data/<int:pid>/', views.event_data, name='event_data'),
    path('subevent/create/', views.create_subevent, name='create-subevent'),
    path('subevent/delete/<int:pid>/', views.delete_subevent, name='delete-subevent'),
    path('subcoordinator/appoint/', views.appoint_subcoordinator, name='appoint-subcoordinator'),

    # Registration & Roles
    path('volunteer/', views.volunteer, name='volunteer'),
    path('participant/', views.participant, name='participant'),
    path('audience/', views.audience, name='audience'),

    # Payments
    path('payment/', views.payment, name='payment'),
    path('payment/toggle/<int:pid>/', views.toggle_payment_verification, name='toggle-payment'),

    # 3-Tier Proposal Approval Pipeline
    path('proposals/', views.proposals_view, name='proposals'),
    path('proposals/approve-hod/<int:pid>/', views.approve_proposal_hod, name='approve-proposal-hod'),
    path('proposals/approve-principal/<int:pid>/', views.approve_proposal_principal, name='approve-proposal-principal'),
    path('proposals/reject/<int:pid>/', views.reject_proposal, name='reject-proposal'),

    # Passes & QR Engine
    path('qr/', views.generate_qr, name='generate-qr'),
    path('event/<int:event_id>/generate-pass/', views.generate_pass, name='generate-pass'),
    
    # Sub-coordinator Live QR Scanner & API
    path('scanner/', views.scanner_page, name='scanner'),
    path('api/verify-pass/', views.verify_pass_api, name='verify-pass-api'),

    # Audit & PDF Reports
    path('report/', views.report, name='report'),
    path('generatereport/<int:pid>/', views.generatereport, name='generatereport'),

    # Memories Gallery & Notifications
    path('memories/', views.memories_view, name='memories'),
    path('notification/', views.notification, name='notification'),
    path('profile/', views.profile, name='profile'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
