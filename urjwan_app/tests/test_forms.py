from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from .model_factories import *
from ..forms import *

class TestUserForm(TestCase):

	def test_email_is_valid(self):
		form_data = {
			'email': 'user@example.com',
			'password': 'complexpass456',
			'first_name': 'Sample',
			'last_name': 'User'
		}
		form = UserForm(data=form_data)
		self.assertTrue(form.is_valid())

	def test_email_with_no_at_symbol(self):
		form_data = {
			'email': 'invalidemail',
			'password': 'complexpass456',
			'first_name': 'Sample',
			'last_name': 'User'
		}
		form = UserForm(data=form_data)
		self.assertFalse(form.is_valid())
		self.assertIn('email', form.errors)

	def test_email_missing_domain_extension(self):
		form_data = {
			'email': 'user@domain',
			'password': 'complexpass456',
			'first_name': 'Sample',
			'last_name': 'User'
		}
		form = UserForm(data=form_data)
		self.assertFalse(form.is_valid())
		self.assertIn('email', form.errors)

	def test_email_starts_with_at_symbol(self):
		form_data = {
			'email': '@example.com',
			'password': 'complexpass456',
			'first_name': 'Sample',
			'last_name': 'User'
		}
		form = UserForm(data=form_data)
		self.assertFalse(form.is_valid())
		self.assertIn('email', form.errors)


class TestUpdateStatusForm(TestCase):

	def test_form_without_status_field(self):
		form_data = {}
		form = UpdateStatusForm(data=form_data)
		self.assertTrue(form.is_valid())

	def test_form_with_status_field(self):
		form_data = {'status': 'Unavailable'}
		form = UpdateStatusForm(data=form_data)
		self.assertTrue(form.is_valid())


class TestCourseForm(TestCase):

	def setUp(self):
		Course.objects.create(module_code="CS1010", title="Initial Course")

	def test_unique_course_is_valid(self):
		form_data = {'module_code': 'CS2021', 'title': 'Another Course'}
		form = CourseForm(data=form_data)
		self.assertTrue(form.is_valid())

	def test_invalid_format_in_module_code_letters(self):
		form_data = {'module_code': 'InvalidCode', 'title': 'Test Course'}
		form = CourseForm(data=form_data)
		self.assertFalse(form.is_valid())

	def test_invalid_format_in_module_code_numbers(self):
		form_data = {'module_code': '123456', 'title': 'Test Course'}
		form = CourseForm(data=form_data)
		self.assertFalse(form.is_valid())

	def test_duplicate_module_code_not_allowed(self):
		form_data = {'module_code': 'CS1010', 'title': 'Duplicate Entry'}
		form = CourseForm(data=form_data)
		self.assertFalse(form.is_valid())


class TestMaterialForm(TestCase):

	def test_small_file_size_is_valid(self):
		small_test_file = SimpleUploadedFile("small_file.txt", b"Test Content")
		form = MaterialForm(data={'title': 'Valid File'},
							files={'file': small_test_file})
		self.assertTrue(form.is_valid())

	def test_large_file_size_is_invalid(self):
		large_test_file = SimpleUploadedFile("large_file.txt",
											 b"x" * (10 * 1024 * 1024 + 1))
		form_data = {'title': 'Too Large File', 'file': large_test_file}
		form = MaterialForm(data=form_data)
		self.assertFalse(form.is_valid())


class TestAssignmentForm(TestCase):

	def test_future_deadline_is_valid(self):
		form_data = {
			'title': 'Upcoming Assignment',
			'startdate': timezone.now(),
			'deadline': timezone.now() + timezone.timedelta(days=1)
		}
		form = AssignmentForm(data=form_data)
		self.assertTrue(form.is_valid())

	def test_past_deadline_is_invalid(self):
		form_data = {
			'title': 'Expired Assignment',
			'startdate': timezone.now(),
			'deadline': timezone.now() - timezone.timedelta(days=1)
		}
		form = AssignmentForm(data=form_data)
		self.assertFalse(form.is_valid())
