from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from .model_factories import *
from ..serializers import *
from django.test import override_settings


class AuthenticatedUserAPITest(APITestCase):

	def setUp(self):
		self.user = UserFactory()
		self.client = APIClient()
		self.client.force_authenticate(user=self.user)
		self.user.profile = UserProfileFactory(user=self.user)
		self.course = CourseFactory(instructor=self.user.profile)

	def test_access_user_profiles(self):
		response = self.client.get(
			reverse('userprofile-list'))  # For list endpoint of userprofiles
		self.assertEqual(response.status_code, 200)

	def test_access_courses(self):
		response = self.client.get(
			reverse('course-list'))  # For list endpoint of courses
		self.assertEqual(response.status_code, 200)

	def test_access_materials(self):
		response = self.client.get(
			reverse('material-list'))  # For list endpoint of materials
		self.assertEqual(response.status_code, 200)

	def tearDown(self):
		self.client.force_authenticate(user=None)
		super().tearDown()


class UnauthenticatedUserAPITest(APITestCase):

	def setUp(self):
		self.user = UserFactory()
		self.client = APIClient()
		self.client.force_authenticate(user=None)

	def test_unauthenticated_access_courses(self):
		response = self.client.get(reverse('course-list'))
		self.assertEqual(response.status_code, 403)

	def test_unauthenticated_access_feedbacks(self):
		response = self.client.get(reverse('feedback-list'))
		self.assertEqual(response.status_code, 403)

	def test_unauthenticated_access_assignments(self):
		response = self.client.get(reverse('assignment-list'))
		self.assertEqual(response.status_code, 403)

	def tearDown(self):
		self.client.force_authenticate(user=None)
		super().tearDown()


class CourseListDataTest(APITestCase):

	def setUp(self):
		self.user = UserFactory()
		self.client = APIClient()
		self.client.force_authenticate(user=self.user)
		self.user.profile = UserProfileFactory(user=self.user)
		self.course = CourseFactory(instructor=self.user.profile)

	def test_course_list_contains_all_courses(self):
		response = self.client.get(reverse('course-list'))
		self.assertEqual(response.json(),
						 CourseListSerializer(Course.objects.all(),
											  many=True).data)

	def tearDown(self):
		self.client.force_authenticate(user=None)
		super().tearDown()


class MaterialListDataTest(APITestCase):

	def setUp(self):
		self.user = UserFactory()
		self.client = APIClient()
		self.client.force_authenticate(user=self.user)
		self.user.profile = UserProfileFactory(user=self.user)
		self.material = MaterialFactory(
			course=CourseFactory(instructor=self.user.profile))

	@override_settings(MEDIA_URL='/media/')
	def test_material_list_contains_all_materials(self):
		response = self.client.get(reverse('material-list'))

		# Normalize the serializer data to use absolute URLs
		expected_data = MaterialSerializer(Material.objects.all(),
										   many=True).data
		for item in expected_data:
			item['file'] = f"http://testserver{item['file']}"


		self.assertEqual(response.json(), expected_data)

	def tearDown(self):
		self.client.force_authenticate(user=None)


class AssignmentListDataTest(APITestCase):

	def setUp(self):
		self.user = UserFactory()
		self.client = APIClient()
		self.client.force_authenticate(user=self.user)
		self.user.profile = UserProfileFactory(
			user=self.user)  # Create the user profile first
		self.course = CourseFactory(
			instructor=self.user.profile)  # Use the created profile
		self.assignment = AssignmentFactory(
			course=self.course)  # Create an assignment tied to the course

	def test_assignment_list_contains_all_assignments(self):
		response = self.client.get(reverse('assignment-list'))
		self.assertEqual(response.json(),
						 AssignmentSerializer(Assignment.objects.all(),
											  many=True).data)

	def tearDown(self):
		self.client.force_authenticate(user=None)
		super().tearDown()


class FeedbackListDataTest(APITestCase):

	def setUp(self):
		self.user = UserFactory(user_type='instructor')
		self.client = APIClient()
		self.client.force_authenticate(user=self.user)
		self.feedback = FeedbackFactory(
			course=CourseFactory(instructor=self.user))

	def test_feedback_list_contains_all_feedbacks(self):
		response = self.client.get(reverse('feedback-list'))
		self.assertEqual(response.json(),
						 FeedbackSerializer(Feedback.objects.all(),
											many=True).data)

	def tearDown(self):
		self.client.force_authenticate(user=None)


class NotificationListDataTest(APITestCase):

	def setUp(self):
		self.user = UserFactory()
		self.client = APIClient()
		self.client.force_authenticate(user=self.user)
		self.notification = NotificationFactory(to_user=self.user.profile)

	def test_notification_list_contains_all_notifications(self):
		response = self.client.get(reverse('notification-list'))
		self.assertEqual(response.json(),
						 NotificationSerializer(Notification.objects.all(),
												many=True).data)

	def tearDown(self):
		self.client.force_authenticate(user=None)


class ChatMessageListDataTest(APITestCase):

	def setUp(self):
		self.user = UserFactory(user_type='instructor')
		self.client = APIClient()
		self.client.force_authenticate(user=self.user)
		self.chat_message = ChatMessageFactory(sender=self.user)

	def test_chat_message_list_contains_all_messages(self):
		response = self.client.get(reverse('chatmessage-list'))
		self.assertEqual(response.json(),
						 ChatMessageSerializer(ChatMessage.objects.all(),
											   many=True).data)

	def tearDown(self):
		self.client.force_authenticate(user=None)
