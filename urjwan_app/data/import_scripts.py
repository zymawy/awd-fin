import os
import sys
import django
import csv
from datetime import datetime
import pytz

sys.path.append('')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'urjwan.settings')
django.setup()

from urjwan_app.models import UserProfile, Course, Assignment, Material, Feedback, Notification
from django.contrib.auth.models import Group, User, Permission
from django.db import connection

def truncate_table(table_name):
    with connection.cursor() as cursor:
        cursor.execute(f"UPDATE sqlite_sequence SET seq = 0 WHERE name = '{table_name}';")

def create_groups():
    group_permissions = {
        "instructor": ["add_course", "change_course", "delete_course", "view_course", "add_assignment", "change_assignment", "delete_assignment", "view_assignment", "add_material", "change_material", "delete_material", "view_material", "change_feedback", "delete_feedback", "view_feedback", "add_notification", "view_notification", "change_notification"],
        "student": ["view_course", "view_assignment", "view_material", "add_feedback", "change_feedback", "delete_feedback", "view_feedback", "add_notification", "view_notification", "change_notification"]
    }
    for group_name, permissions in group_permissions.items():
        group, created = Group.objects.get_or_create(name=group_name)
        if created:
            group.permissions.set(Permission.objects.filter(codename__in=permissions))
            group.save()

def import_user(csv_file_path):
    with open(csv_file_path, 'r', encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        next(csv_reader)
        for row in csv_reader:
            username, first_name, last_name, email, is_active, password = row
            if not User.objects.filter(username=username).exists():
                user = User.objects.create(username=username, first_name=first_name, last_name=last_name, email=email, is_active=is_active == 'TRUE')
                user.set_password(password)
                user.save()

def import_userProfile(csv_file_path):
    with open(csv_file_path, 'r', encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        next(csv_reader)
        for row in csv_reader:
            username, user_type, photo_path, status = row
            user = User.objects.get(username=username)
            if not UserProfile.objects.filter(user=user).exists():
                userprofile = UserProfile.objects.create(user=user, user_type=user_type, photo=photo_path, status=status)
                group = Group.objects.get(name=user_type)
                user.groups.add(group)
                user.save()

def import_course(csv_file_path):
    with open(csv_file_path, 'r', encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        next(csv_reader)
        for row in csv_reader:
            module_code, title, instructor_id, description = row
            instructor = UserProfile.objects.get(id=instructor_id)
            if not Course.objects.filter(module_code=module_code).exists():
                Course.objects.create(module_code=module_code, title=title, instructor=instructor, description=description)

def import_studentenrollment(csv_file_path):
    with open(csv_file_path, 'r', encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        next(csv_reader)
        for row in csv_reader:
            student_id, module_code = row
            student = UserProfile.objects.get(id=student_id)
            course = Course.objects.get(module_code=module_code)
            if not course.students.filter(user=student.user).exists():
                course.students.add(student)
                course.save()

def import_assignment(csv_file_path):
    with open(csv_file_path, 'r', encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        next(csv_reader)
        for row in csv_reader:
            title, module_code, startdate, deadline = row
            course = Course.objects.get(module_code=module_code)
            startdate = pytz.utc.localize(datetime.strptime(startdate, "%Y-%m-%dT%H:%M:%S"))
            deadline = pytz.utc.localize(datetime.strptime(deadline, "%Y-%m-%dT%H:%M:%S"))
            Assignment.objects.create(title=title, course=course, startdate=startdate, deadline=deadline)

def import_material(csv_file_path):
    with open(csv_file_path, 'r', encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        next(csv_reader)
        for row in csv_reader:
            title, module_code, file = row
            course = Course.objects.get(module_code=module_code)
            Material.objects.create(title=title, course=course, file=file)

def import_feedback(csv_file_path):
    with open(csv_file_path, 'r', encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        next(csv_reader)
        for row in csv_reader:
            module_code, student_id, feedback_text, timestamp = row
            student = UserProfile.objects.get(id=student_id)
            course = Course.objects.get(module_code=module_code)
            Feedback.objects.create(course=course, student=student, feedback_text=feedback_text, timestamp=timestamp)

def import_notification(csv_file_path):
    with open(csv_file_path, 'r', encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        next(csv_reader)
        for row in csv_reader:
            to_user_id, from_user_id, module_code, type, read_status, timestamp = row
            to_user = UserProfile.objects.get(id=to_user_id)
            from_user = UserProfile.objects.get(id=from_user_id)
            course = Course.objects.get(module_code=module_code)
            timestamp = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S")
            Notification.objects.create(to_user=to_user, from_user=from_user, course=course, type=type, read_status=read_status == 'TRUE', timestamp=timestamp)
