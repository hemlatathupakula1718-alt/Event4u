from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid

# --- Choices ---
BRANCH = [
    ('Computer', 'Computer Engineering'),
    ('AIML', 'Artificial Intelligence & Machine Learning'),
    ('Data Science', 'Data Science'),
    ('IOT', 'Internet of Things'),
    ('IT', 'Information Technology'),
    ('EXTC', 'Electronics & Telecommunication'),
    ('Mechanical', 'Mechanical Engineering'),
    ('Civil', 'Civil Engineering'),
]

SEMESTER = [
    ('1', 'Semester 1'),
    ('2', 'Semester 2'),
    ('3', 'Semester 3'),
    ('4', 'Semester 4'),
    ('5', 'Semester 5'),
    ('6', 'Semester 6'),
    ('7', 'Semester 7'),
    ('8', 'Semester 8'),
]

ROLES = [
    ('PRINCIPAL', 'Principal / Admin'),
    ('HOD', 'Head of Department (HoD)'),
    ('COORDINATOR', 'Faculty Coordinator'),
    ('SUB_COORDINATOR', 'Student Sub-Coordinator'),
    ('STUDENT', 'Student'),
]

STATUS = [
    ('Pending', 'Pending Approval'),
    ('Active', 'Active / In Progress'),
    ('Completed', 'Completed'),
    ('Rejected', 'Rejected'),
]

MODE_OF_PAYMENT = [
    ('CASH', 'Cash Payment'),
    ('ONLINE', 'Online (UPI / QR / NetBanking)'),
]

PAYMENT_STATUS = [
    ('Pending', 'Verification Pending'),
    ('Verified', 'Verified & Approved'),
    ('Rejected', 'Rejected / Invalid Proof'),
]

CATEGORY_CHOICES = [
    ('Technical', 'Technical Events'),
    ('Gaming', 'Gaming & Esports'),
    ('Cultural', 'On Stage / Cultural'),
    ('Sports', 'Sports & Fitness'),
    ('Workshop', 'Workshops & Seminars'),
    ('OffStage', 'Off Stage & Competitions'),
]

REGISTRATION_TYPES = [
    ('PARTICIPANT', 'Participant'),
    ('VOLUNTEER', 'Volunteer'),
    ('AUDIENCE', 'Audience / Attendee'),
]


# --- User Profile Extension ---
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=30, choices=ROLES, default='STUDENT')
    fullName = models.CharField(max_length=100, blank=True, null=True)
    branch = models.CharField(max_length=50, choices=BRANCH, default='Computer')
    semester = models.CharField(max_length=10, choices=SEMESTER, default='1')
    rollNumber = models.PositiveIntegerField(null=True, blank=True)
    erp = models.PositiveBigIntegerField(null=True, blank=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars', null=True, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

    @property
    def display_name(self):
        if self.fullName:
            return self.fullName
        return self.user.get_full_name() or self.user.username


# --- Coordinator Profile ---
class Coordinator(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='coordinator_profile')
    name = models.CharField(max_length=100, null=False, blank=False)
    branch = models.CharField(max_length=50, choices=BRANCH)
    semester = models.CharField(max_length=50, choices=SEMESTER)
    rollNumber = models.PositiveIntegerField(null=False, blank=False)
    erp = models.PositiveBigIntegerField(null=False, blank=False)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


# --- Proposal Model ---
class Proposal(models.Model):
    coordinator = models.ForeignKey(Coordinator, on_delete=models.CASCADE, null=False, blank=False, related_name='proposals')
    title = models.CharField(max_length=200, default='Event Proposal')
    description = models.TextField(null=False, blank=False)
    feeApplicableForPerStudent = models.PositiveIntegerField(null=False, blank=False, default=0)
    fundRecieveFromCollege = models.PositiveIntegerField(null=False, blank=False, default=0)
    estimatedAudience = models.PositiveIntegerField(default=100)
    
    # 3-Tier Approval Workflow
    HoD_Approval = models.BooleanField(default=False)
    Vice_Principal_Approval = models.BooleanField(default=False)
    Principal_Approval = models.BooleanField(default=False)
    
    status = models.CharField(max_length=50, choices=STATUS, default='Pending')
    rejectionRemarks = models.TextField(blank=True, null=True)
    
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.status}"

    @property
    def is_fully_approved(self):
        return self.HoD_Approval and self.Principal_Approval


# --- Main Event Model ---
class Event(models.Model):
    coordinator = models.ForeignKey(Coordinator, on_delete=models.CASCADE, null=False, blank=False, related_name='events')
    name = models.CharField(max_length=150, null=False, blank=False)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Technical')
    description = models.TextField(null=False, blank=False)
    image = models.ImageField(upload_to='events')
    status = models.CharField(max_length=50, choices=STATUS, default='Active')
    upi = models.CharField(max_length=100, blank=True, null=True, help_text="UPI ID for student fee collection")
    totalMoney = models.PositiveIntegerField(null=True, blank=True, default=0, help_text="Total allocated budget")
    venue = models.CharField(max_length=150, default='College Auditorium')
    eventDate = models.DateTimeField(null=True, blank=True)
    registrationOpen = models.BooleanField(default=True)
    createdAt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def total_participants_count(self):
        return Participant.objects.filter(event=self).count()

    @property
    def total_volunteers_count(self):
        return Volunteer.objects.filter(event=self).count()

    @property
    def total_audience_count(self):
        return Audience.objects.filter(event=self).count()

    @property
    def total_attendees_count(self):
        return self.total_participants_count + self.total_volunteers_count + self.total_audience_count

    @property
    def total_verified_payments_amount(self):
        verified_payments = Payment.objects.filter(event=self, coordinatorCheck=True)
        # Assuming fee per event or proposal
        proposal = Proposal.objects.filter(coordinator=self.coordinator).first()
        fee = proposal.feeApplicableForPerStudent if proposal else 150
        return verified_payments.count() * fee


# --- Sub-Coordinator Profile ---
class SubCoordinator(models.Model):
    coordinator = models.ForeignKey(Coordinator, on_delete=models.CASCADE, null=False, blank=False, related_name='subcoordinators')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=False, blank=False, related_name='subcoordinators')
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='subcoordinator_profile')
    name = models.CharField(max_length=100, null=False, blank=False)
    branch = models.CharField(max_length=50, choices=BRANCH)
    semester = models.CharField(max_length=50, choices=SEMESTER)
    rollNumber = models.PositiveIntegerField(null=False, blank=False)
    erp = models.PositiveBigIntegerField(null=False, blank=False)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.event.name})"


# --- Sub-Event Model ---
class SubEvent(models.Model):
    coordinator = models.ForeignKey(Coordinator, on_delete=models.CASCADE, null=False, blank=False)
    subcoordinator = models.ForeignKey(SubCoordinator, on_delete=models.CASCADE, null=False, blank=False, related_name='subevents')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=False, blank=False, related_name='subevents')
    name = models.CharField(max_length=150, null=False, blank=False)
    description = models.TextField(null=False, blank=False)
    image = models.ImageField(upload_to='subevents', blank=True, null=True)
    venue = models.CharField(max_length=150, default='Main Campus')
    totalBudget = models.PositiveIntegerField(null=True, blank=True, default=0)
    utiliseBudget = models.PositiveIntegerField(null=True, blank=True, default=0)
    balanceBudget = models.PositiveIntegerField(null=True, blank=True, default=0)
    eventDate = models.DateTimeField(null=True, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.event.name}"

    def save(self, *args, **kwargs):
        if self.totalBudget is not None and self.utiliseBudget is not None:
            self.balanceBudget = max(0, int(self.totalBudget) - int(self.utiliseBudget))
        super().save(*args, **kwargs)


# --- Volunteer Registration ---
class Volunteer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='volunteer_registrations')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=False, blank=False, related_name='volunteers')
    subevent = models.ForeignKey(SubEvent, on_delete=models.CASCADE, null=False, blank=False, related_name='volunteers')
    name = models.CharField(max_length=100, null=False, blank=False)
    branch = models.CharField(max_length=50, choices=BRANCH)
    semester = models.CharField(max_length=50, choices=SEMESTER)
    rollNumber = models.PositiveIntegerField(null=False, blank=False)
    erp = models.PositiveBigIntegerField(null=False, blank=False)
    isVolunteer = models.BooleanField(default=True)
    work = models.TextField(null=False, blank=False, help_text="Preferred tasks / skills")
    status = models.CharField(max_length=30, default='Assigned', choices=[('Pending', 'Pending'), ('Assigned', 'Assigned'), ('Completed', 'Completed')])
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - Volunteer ({self.subevent.name})"


# --- Participant Registration ---
class Participant(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='participant_registrations')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=False, blank=False, related_name='participants')
    subevent = models.ForeignKey(SubEvent, on_delete=models.CASCADE, null=False, blank=False, related_name='participants')
    name = models.CharField(max_length=100, null=False, blank=False)
    branch = models.CharField(max_length=50, choices=BRANCH)
    semester = models.CharField(max_length=50, choices=SEMESTER)
    rollNumber = models.PositiveIntegerField(null=False, blank=False)
    erp = models.PositiveBigIntegerField(null=False, blank=False)
    isParticipant = models.BooleanField(default=True)
    interest = models.TextField(null=False, blank=False)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - Participant ({self.subevent.name})"


# --- Audience Registration ---
class Audience(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='audience_registrations')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=False, blank=False, related_name='audience_members')
    name = models.CharField(max_length=100, null=False, blank=False)
    branch = models.CharField(max_length=50, choices=BRANCH)
    semester = models.CharField(max_length=50, choices=SEMESTER)
    rollNumber = models.PositiveIntegerField(null=False, blank=False)
    erp = models.PositiveBigIntegerField(null=False, blank=False)
    isAudience = models.BooleanField(default=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - Audience ({self.event.name})"


# --- Payment Model ---
class Payment(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=False, blank=False, related_name='payments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='payments')
    name = models.CharField(max_length=100, null=False, blank=False)
    branch = models.CharField(max_length=50, choices=BRANCH)
    semester = models.CharField(max_length=50, choices=SEMESTER)
    rollNumber = models.PositiveIntegerField(null=False, blank=False)
    erp = models.PositiveBigIntegerField(null=False, blank=False)
    whatsAppNumber = models.CharField(max_length=15, null=False, blank=False)
    mobileNumber = models.CharField(max_length=15, null=False, blank=False)
    modeOfPayment = models.CharField(choices=MODE_OF_PAYMENT, default='ONLINE', max_length=50)
    amount = models.PositiveIntegerField(default=150)
    transactionId = models.CharField(max_length=100, blank=True, null=True)
    paymentRecieptImage = models.ImageField(upload_to='payment', null=True, blank=True)
    recieptNumber = models.CharField(max_length=50, null=True, blank=True)
    coordinatorCheck = models.BooleanField(default=True, help_text="Verified by Coordinator")
    status = models.CharField(max_length=30, choices=PAYMENT_STATUS, default='Verified')
    verifiedAt = models.DateTimeField(null=True, blank=True)
    createdAt = models.DateTimeField(default=timezone.now)


    def __str__(self):
        return f"{self.name} - ₹{self.amount} ({self.modeOfPayment})"


# --- Digital Pass with Verifiable QR Code ---
class Pass(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='passes')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='passes')
    subevent = models.ForeignKey(SubEvent, on_delete=models.SET_NULL, null=True, blank=True, related_name='passes')
    registrationType = models.CharField(max_length=30, choices=REGISTRATION_TYPES, default='PARTICIPANT')
    date = models.DateField()
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    isCheckedIn = models.BooleanField(default=False)
    checkedInAt = models.DateTimeField(null=True, blank=True)
    checkedInBy = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='scanned_passes')
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Pass #{self.uuid.hex[:8]} - {self.name} ({self.event.name})"



# --- Notifications Model ---
class Notification(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    title = models.CharField(max_length=200, default='Event Announcement')
    description = models.TextField(null=False, blank=False)
    targetRole = models.CharField(max_length=30, default='ALL', choices=[
        ('ALL', 'All College Members'),
        ('STUDENTS', 'Registered Students Only'),
        ('VOLUNTEERS', 'Volunteers Only'),
        ('COORDINATORS', 'Coordinators Only'),
    ])
    createdBy = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    createdAt = models.DateTimeField(default=timezone.now)


    def __str__(self):
        return self.title or self.description[:50]


# --- Event Memories Photo Gallery ---
class Memories(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=False, blank=False, related_name='memories')
    subevent = models.ForeignKey(SubEvent, on_delete=models.SET_NULL, null=True, blank=True, related_name='memories')
    title = models.CharField(max_length=150, default='Event Memory')
    image = models.ImageField(upload_to='memories')
    uploadedBy = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.event.name}"


# --- Pass Scan & Attendance Log ---
class AttendanceLog(models.Model):
    pass_obj = models.ForeignKey(Pass, on_delete=models.CASCADE, related_name='attendance_logs')
    scanned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    scanned_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default='Granted')
    remarks = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"{self.pass_obj.name} - {self.status} at {self.scanned_at}"