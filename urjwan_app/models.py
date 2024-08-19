from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class UserProfile(models.Model):
    USER_TYPE_CHOICES = [
        ('student', 'Student'),
        ('instructor', 'Instructor'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    photo = models.ImageField(upload_to='urjwan_app/user_photos/', blank=True, null=True)
    status = models.CharField(max_length=256, blank=True, null=True, default="")

    def is_student(self):
        return self.user_type == 'student'

    def is_instructor(self):
        return self.user_type == 'instructor'

    def __str__(self):
        return self.user.username

class Course(models.Model):
    module_code = models.CharField(max_length=256, unique=True)
    title = models.CharField(max_length=256)
    description = models.TextField(blank=True, null=True)
    instructor = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, related_name='courses_taught')
    students = models.ManyToManyField(UserProfile, related_name='courses_enrolled', blank=True)

    def __str__(self):
        return self.module_code

class Material(models.Model):
    title = models.CharField(max_length=256)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='materials')
    file = models.FileField(upload_to='course_materials/')

    def __str__(self):
        return self.title

class Assignment(models.Model):
    title = models.CharField(max_length=256)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments')
    startdate = models.DateTimeField(null=True, blank=True)
    deadline = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title

class Feedback(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='feedbacks_received')
    student = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='feedbacks_given')
    feedback_text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.feedback_text

class Notification(models.Model):
    to_user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='notifications_recieved')
    from_user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='notifications_sent')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=256)
    read_status = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message

class ChatMessage(models.Model):
    room_name = models.CharField(max_length=255)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.sender.username}: {self.message[:50]}'
