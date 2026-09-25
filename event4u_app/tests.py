from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Event, Coordinator, Proposal, Pass, Payment, UserProfile

class Event4uComprehensiveTests(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create Principal User
        self.principal_user = User.objects.create_superuser(
            username='test_principal',
            email='principal@college.edu',
            password='testpassword123'
        )
        UserProfile.objects.create(
            user=self.principal_user,
            role='PRINCIPAL',
            fullName='Dr. Test Principal'
        )

        # Create Coordinator
        self.coord_user = User.objects.create_user(
            username='test_coordinator',
            email='coord@college.edu',
            password='testpassword123'
        )
        UserProfile.objects.create(
            user=self.coord_user,
            role='COORDINATOR',
            fullName='Prof. Test Coordinator',
            branch='Computer'
        )
        self.coordinator = Coordinator.objects.create(
            user=self.coord_user,
            name='Prof. Test Coordinator',
            branch='Computer',
            semester='6',
            rollNumber=1,
            erp=200600001
        )

        # Create Event
        self.event = Event.objects.create(
            coordinator=self.coordinator,
            name='National Hackathon 2026',
            category='Technical',
            description='24-hour campus hackathon',
            totalMoney=50000,
            status='Active'
        )

    def test_home_page(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_login_flow(self):
        response = self.client.post(reverse('login'), {
            'username': 'test_principal',
            'password': 'testpassword123'
        })
        self.assertEqual(response.status_code, 302)

    def test_principal_dashboard_access(self):
        self.client.login(username='test_principal', password='testpassword123')
        response = self.client.get(reverse('principal-dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_pdf_report_generation(self):
        self.client.login(username='test_principal', password='testpassword123')
        response = self.client.get(reverse('generatereport', args=[self.event.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')

    def test_qr_generation(self):
        self.client.login(username='test_principal', password='testpassword123')
        response = self.client.get(reverse('generate-qr'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'image/png')
