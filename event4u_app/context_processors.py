from .models import Notification

def app_context(request):
    """
    Provides global application context to all templates,
    including current user profile, role flags, and unread notifications.
    """
    context = {
        'user_profile': None,
        'user_role': 'ANONYMOUS',
        'is_principal': False,
        'is_hod': False,
        'is_coordinator': False,
        'is_subcoordinator': False,
        'is_student': False,
        'recent_notifications': [],
        'unread_notifications_count': 0,
    }
    
    if request.user.is_authenticated:
        # Check UserProfile if attached
        profile = getattr(request.user, 'profile', None)
        if profile:
            context['user_profile'] = profile
            role = profile.role
            context['user_role'] = role
            context['is_principal'] = (role == 'PRINCIPAL' or request.user.is_superuser)
            context['is_hod'] = (role == 'HOD')
            context['is_coordinator'] = (role == 'COORDINATOR')
            context['is_subcoordinator'] = (role == 'SUB_COORDINATOR')
            context['is_student'] = (role == 'STUDENT')
        else:
            if request.user.is_superuser:
                context['user_role'] = 'PRINCIPAL'
                context['is_principal'] = True
            elif request.user.is_staff:
                context['user_role'] = 'COORDINATOR'
                context['is_coordinator'] = True
            else:
                context['user_role'] = 'STUDENT'
                context['is_student'] = True
                
        try:
            notifications = Notification.objects.all().order_by('-id')[:5]
            context['recent_notifications'] = notifications
            context['unread_notifications_count'] = Notification.objects.count()
        except Exception:
            pass

    return context
