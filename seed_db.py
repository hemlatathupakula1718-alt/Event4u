import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event4u.settings')
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from event4u_app.models import (
    UserProfile, Coordinator, SubCoordinator, Event, SubEvent,
    Proposal, Payment, Participant, Audience, Volunteer, Pass,
    Notification, Memories
)

def seed_database():
    print("Seeding users, profiles, and initial relationships...")

    # 1. Principal / Admin
    p_user, _ = User.objects.get_or_create(username='admin', defaults={'email': 'admin@ycc.edu'})
    p_user.set_password('admin123')
    p_user.is_superuser = True
    p_user.is_staff = True
    p_user.first_name = 'Principal'
    p_user.last_name = 'Director'
    p_user.save()
    UserProfile.objects.update_or_create(
        user=p_user,
        defaults={
            'role': 'PRINCIPAL',
            'fullName': 'Principal & Director (Admin)',
            'branch': 'Administration',
            'semester': '8',
            'erp': 10000001,
            'phone': '9876543210',
        }
    )

    # 2. HoD
    hod_user, _ = User.objects.get_or_create(username='rajendra', defaults={'email': 'rajendra@gmail.com'})
    hod_user.set_password('ltcoe@123')
    hod_user.is_staff = True
    hod_user.first_name = 'Dr. Rajendra'
    hod_user.last_name = 'Pawar'
    hod_user.save()
    UserProfile.objects.update_or_create(
        user=hod_user,
        defaults={
            'role': 'HOD',
            'fullName': 'Dr. Rajendra Pawar (HoD - Computer Dept)',
            'branch': 'Computer',
            'semester': '8',
            'erp': 10000002,
            'phone': '9876543211',
        }
    )

    # 3. Coordinator
    coord_user, _ = User.objects.get_or_create(username='advait', defaults={'email': 'advait@gmail.com'})
    coord_user.set_password('ltcoe@123')
    coord_user.is_staff = True
    coord_user.first_name = 'Prof. Advait'
    coord_user.last_name = 'Kulkarni'
    coord_user.save()
    UserProfile.objects.update_or_create(
        user=coord_user,
        defaults={
            'role': 'COORDINATOR',
            'fullName': 'Prof. Advait Kulkarni (Faculty Coordinator)',
            'branch': 'Computer',
            'semester': '6',
            'erp': 10000003,
            'phone': '9876543212',
        }
    )
    coord_obj, _ = Coordinator.objects.update_or_create(
        user=coord_user,
        defaults={
            'name': 'Prof. Advait Kulkarni',
            'branch': 'Computer',
            'semester': '6',
            'rollNumber': 1,
            'erp': 10000003,
        }
    )

    # 4. Create Main Events
    event1, _ = Event.objects.update_or_create(
        id=1,
        defaults={
            'name': 'Zeal Fest 2026 (Annual Cultural & Tech Fest)',
            'coordinator': coord_obj,
            'category': 'Cultural',
            'description': 'The biggest annual flagship technical, cultural and sports extravaganza of Yashwantrao Chavan College Of Arts , Commerce & Science.',
            'venue': 'YCC Main Auditorium & Campus Grounds',
            'eventDate': timezone.now() + timezone.timedelta(days=14),
            'totalMoney': 120000,
            'upi': '9321887200@pytm',
            'status': 'Active',
            'registrationOpen': True,
        }
    )

    event2, _ = Event.objects.update_or_create(
        id=2,
        defaults={
            'name': 'Hack-YCC 2026 (National Hackathon)',
            'coordinator': coord_obj,
            'category': 'Technical',
            'description': '36-hour non-stop coding hackathon with tracks in AI/ML, Web3, IoT, and Cloud Computing at Yashwantrao Chavan College.',
            'venue': 'Computer Engineering Advanced Computing Lab',
            'eventDate': timezone.now() + timezone.timedelta(days=21),
            'totalMoney': 75000,
            'upi': '9321887200@pytm',
            'status': 'Active',
            'registrationOpen': True,
        }
    )

    # 5. Sub-Coordinators
    sub1_user, _ = User.objects.get_or_create(username='anjali', defaults={'email': 'anjali@gmail.com'})
    sub1_user.set_password('ltcoe@123')
    sub1_user.first_name = 'Anjali'
    sub1_user.last_name = 'Gupta'
    sub1_user.save()
    UserProfile.objects.update_or_create(
        user=sub1_user,
        defaults={
            'role': 'SUB_COORDINATOR',
            'fullName': 'Anjali Gupta (Student Head)',
            'branch': 'Computer',
            'semester': '6',
            'erp': 200600101,
            'phone': '9876543213',
        }
    )
    sub1_obj, _ = SubCoordinator.objects.update_or_create(
        user=sub1_user,
        defaults={
            'name': 'Anjali Gupta',
            'event': event1,
            'branch': 'Computer',
            'semester': '6',
            'rollNumber': 12,
            'erp': 200600101,
            'coordinator': coord_obj,
        }
    )

    sub2_user, _ = User.objects.get_or_create(username='shraddha', defaults={'email': 'shraddha@gmail.com'})
    sub2_user.set_password('ltcoe@123')
    sub2_user.first_name = 'Shraddha'
    sub2_user.last_name = 'Rane'
    sub2_user.save()
    UserProfile.objects.update_or_create(
        user=sub2_user,
        defaults={
            'role': 'SUB_COORDINATOR',
            'fullName': 'Shraddha Rane (Technical Lead)',
            'branch': 'Computer',
            'semester': '6',
            'erp': 200600102,
            'phone': '9876543214',
        }
    )
    sub2_obj, _ = SubCoordinator.objects.update_or_create(
        user=sub2_user,
        defaults={
            'name': 'Shraddha Rane',
            'event': event2,
            'branch': 'Computer',
            'semester': '6',
            'rollNumber': 15,
            'erp': 200600102,
            'coordinator': coord_obj,
        }
    )

    # 6. Sub-Events
    SubEvent.objects.update_or_create(
        name='Code Clash (Algorithm Battle)',
        defaults={
            'coordinator': coord_obj,
            'subcoordinator': sub2_obj,
            'event': event2,
            'description': 'Speed programming contest on DSA problems.',
            'venue': 'Lab 402',
            'totalBudget': 15000,
            'utiliseBudget': 8000,
            'balanceBudget': 7000,
            'eventDate': timezone.now() + timezone.timedelta(days=21, hours=2),
        }
    )

    SubEvent.objects.update_or_create(
        name='Battle of Bands (Live Concert)',
        defaults={
            'coordinator': coord_obj,
            'subcoordinator': sub1_obj,
            'event': event1,
            'description': 'Inter-college rock and fusion music showdown.',
            'venue': 'Open Air Amphitheatre',
            'totalBudget': 35000,
            'utiliseBudget': 20000,
            'balanceBudget': 15000,
            'eventDate': timezone.now() + timezone.timedelta(days=14, hours=6),
        }
    )

    # 7. Seed 25 Students from PDF roster
    students_data = [
        ("aanchal", "Aanchal Sharma", "Computer", 6, 101, 200600001),
        ("aditi", "Aditi Deshmukh", "Computer", 6, 102, 200600002),
        ("aditya", "Aditya Vernekar", "Computer", 6, 103, 200600003),
        ("akash", "Akash Mishra", "IT", 6, 104, 200600004),
        ("aman", "Aman Gupta", "EXTC", 6, 105, 200600005),
        ("aniket", "Aniket Shinde", "Mechanical", 6, 106, 200600006),
        ("ankita", "Ankita Patil", "Computer", 6, 107, 200600007),
        ("deepak", "Deepak Verma", "Computer", 6, 108, 200600008),
        ("harsh", "Harsh Mehta", "IT", 6, 109, 200600009),
        ("karan", "Karan Johar", "Computer", 6, 110, 200600010),
        ("neha", "Neha Kulkarni", "Computer", 6, 111, 200600011),
        ("nikhil", "Nikhil Sawant", "IT", 6, 112, 200600012),
        ("pooja", "Pooja Hegde", "EXTC", 6, 113, 200600013),
        ("pranav", "Pranav Joshi", "Computer", 6, 114, 200600014),
        ("rahul", "Rahul Roy", "Mechanical", 6, 115, 200600015),
        ("rohit", "Rohit Sharma", "Computer", 6, 116, 200600016),
        ("sakshi", "Sakshi Tanwar", "Computer", 6, 117, 200600017),
        ("saurabh", "Saurabh Jain", "IT", 6, 118, 200600018),
        ("shreya", "Shreya Ghoshal", "Computer", 6, 119, 200600019),
        ("sneha", "Sneha Ullal", "EXTC", 6, 120, 200600020),
        ("tanmay", "Tanmay Bhat", "Computer", 6, 121, 200600021),
        ("varun", "Varun Dhawan", "IT", 6, 122, 200600022),
        ("vikas", "Vikas Dubey", "Civil", 6, 123, 200600023),
        ("vivek", "Vivek Oberoi", "Computer", 6, 124, 200600024),
        ("yash", "Yash Gowda", "Computer", 6, 125, 200600025),
    ]

    for uname, fname, branch, sem, roll, erp in students_data:
        st_user, _ = User.objects.get_or_create(username=uname, defaults={'email': f'{uname}@gmail.com'})
        st_user.set_password('ltcoe@123')
        st_user.first_name = fname.split()[0]
        st_user.last_name = fname.split()[-1]
        st_user.save()
        UserProfile.objects.update_or_create(
            user=st_user,
            defaults={
                'role': 'STUDENT',
                'fullName': fname,
                'branch': branch,
                'semester': str(sem),
                'rollNumber': roll,
                'erp': erp,
                'phone': '9876543299',
            }
        )

        Pass.objects.get_or_create(
            name=fname,
            event=event1,
            defaults={
                'user': st_user,
                'registrationType': 'PARTICIPANT',
                'date': timezone.now().date() + timezone.timedelta(days=14),
            }
        )

        Payment.objects.get_or_create(
            name=fname,
            event=event1,
            defaults={
                'user': st_user,
                'branch': branch,
                'semester': str(sem),
                'rollNumber': roll,
                'erp': erp,
                'whatsAppNumber': '9876543299',
                'mobileNumber': '9876543299',
                'modeOfPayment': 'GPay / PhonePe / Paytm',
                'amount': 200,
                'transactionId': f'UPI{erp}789',
                'coordinatorCheck': True,
                'status': 'Verified',
            }
        )

    # 8. Proposals
    Proposal.objects.update_or_create(
        title='Annual Technical Symposium 2026',
        defaults={
            'coordinator': coord_obj,
            'description': 'A 3-day multi-track technical conference and competition with industry speakers and project exhibits.',
            'feeApplicableForPerStudent': 150,
            'fundRecieveFromCollege': 50000,
            'estimatedAudience': 400,
            'HoD_Approval': True,
            'Principal_Approval': True,
            'status': 'Active',
        }
    )

    Proposal.objects.update_or_create(
        title='Inter-College Esports Championship',
        defaults={
            'coordinator': coord_obj,
            'description': 'Valorant, BGMI and FIFA 24 gaming tournament for colleges across Mumbai University.',
            'feeApplicableForPerStudent': 100,
            'fundRecieveFromCollege': 25000,
            'estimatedAudience': 250,
            'HoD_Approval': True,
            'Principal_Approval': False,
            'status': 'Submitted',
        }
    )

    # 9. Announcements
    Notification.objects.get_or_create(
        title='Zeal Fest 2026 Passes Now Live!',
        defaults={
            'description': 'Official registrations and digital hologram gate passes for Zeal Fest 2026 are now open. Claim your passes early.',
            'targetRole': 'ALL',
            'createdBy': p_user,
            'event': event1,
        }
    )

    print("DATABASE SEEDING COMPLETED SUCCESSFULLY!")

if __name__ == '__main__':
    seed_database()
