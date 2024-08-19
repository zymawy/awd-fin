from django.test import TestCase
from ..forms import *
from django.core.files.uploadedfile import SimpleUploadedFile

from .model_factories import *

class TestCourseModel(TestCase):

    def test_instructor_assigned_to_course(self):
        instructor = UserProfileFactory(user_type='instructor')
        course_instance = CourseFactory(instructor=instructor)
        self.assertEqual(course_instance.instructor.user.username, instructor.user.username)

    def test_course_has_students(self):
        student = UserProfileFactory(user_type='student')
        course_instance = CourseFactory()
        course_instance.students.add(student)
        self.assertIn(student, course_instance.students.all())

    def test_course_contains_materials(self):
        course_instance = CourseFactory()
        material_instance = MaterialFactory(course=course_instance)
        self.assertEqual(material_instance.course, course_instance)

class TestUserProfileModel(TestCase):

    def test_user_profile_linked_to_user(self):
        user_instance = UserFactory()
        profile_instance = UserProfileFactory(user=user_instance)
        self.assertEqual(profile_instance.user.username, user_instance.username)

    def test_user_profile_types_student_and_instructor(self):
        student_profile = UserProfileFactory(user_type='student')
        instructor_profile = UserProfileFactory(user_type='instructor')
        self.assertTrue(student_profile.user_type == 'student')
        self.assertTrue(instructor_profile.user_type == 'instructor')

class TestMaterialModel(TestCase):

    def test_material_associated_with_course(self):
        course_instance = CourseFactory()
        material_instance = MaterialFactory(course=course_instance)
        self.assertEqual(material_instance.course, course_instance)

    def test_file_uploads_correctly(self):
        course_instance = CourseFactory()
        test_file = SimpleUploadedFile("test.txt", b"test_content")
        material_instance = MaterialFactory(course=course_instance, file=test_file)
        self.assertEqual(material_instance.file.read(), b"test_content")

class TestAssignmentModel(TestCase):

    def test_assignment_belongs_to_course(self):
        course_instance = CourseFactory()
        assignment_instance = AssignmentFactory(course=course_instance)
        self.assertEqual(assignment_instance.course, course_instance)

    def test_assignment_dates_valid(self):
        assignment_instance = AssignmentFactory()
        self.assertTrue(assignment_instance.deadline > assignment_instance.startdate)

class TestFeedbackModel(TestCase):

    def test_feedback_assigned_to_course(self):
        course_instance = CourseFactory()
        student_profile = UserProfileFactory(user_type='student')
        feedback_instance = FeedbackFactory(course=course_instance, student=student_profile)
        self.assertEqual(feedback_instance.course, course_instance)

    def test_feedback_associated_with_student(self):
        course_instance = CourseFactory()
        student_profile = UserProfileFactory(user_type='student')
        feedback_instance = FeedbackFactory(course=course_instance, student=student_profile)
        self.assertEqual(feedback_instance.student, student_profile)

class TestNotificationModel(TestCase):

    def test_notification_received_by_user(self):
        receiver = UserProfileFactory()
        notification_instance = NotificationFactory(to_user=receiver)
        self.assertEqual(notification_instance.to_user, receiver)

    def test_notification_sent_by_user(self):
        sender = UserProfileFactory()
        notification_instance = NotificationFactory(from_user=sender)
        self.assertEqual(notification_instance.from_user, sender)

    def test_notification_linked_to_course(self):
        course_instance = CourseFactory()
        notification_instance = NotificationFactory(course=course_instance)
        self.assertEqual(notification_instance.course, course_instance)
