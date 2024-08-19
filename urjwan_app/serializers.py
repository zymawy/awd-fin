from rest_framework import serializers
from .models import *
from .models import UserProfile, Course, Material, Assignment, Feedback, \
	Notification, ChatMessage


class UserProfileSerializer(serializers.ModelSerializer):
	class Meta:
		model = UserProfile
		fields = '__all__'


class CourseSerializer(serializers.ModelSerializer):
	class Meta:
		model = Course
		fields = '__all__'


class NotificationSerializer(serializers.ModelSerializer):
	class Meta:
		model = Notification
		fields = '__all__'


class ChatMessageSerializer(serializers.ModelSerializer):
	class Meta:
		model = ChatMessage
		fields = '__all__'


class CourseListSerializer(serializers.ModelSerializer):
	# get the instructor's name and email based on their id (only 1 instructor per course)
	instructor_name = serializers.CharField(
		source='instructor.user.get_full_name', read_only=True)
	instructor_email = serializers.CharField(source='instructor.user.email',
											 read_only=True)

	class Meta:
		model = Course
		fields = ['module_code', 'title', 'instructor_name', 'instructor_email']


class AssignmentSerializer(serializers.ModelSerializer):
	class Meta:
		model = Assignment
		fields = ['title', 'startdate', 'deadline']


class MaterialSerializer(serializers.ModelSerializer):
	class Meta:
		model = Material
		fields = ['title', 'file']


class FeedbackSerializer(serializers.ModelSerializer):
	# get student's name
	student = serializers.CharField(source='student.user.get_full_name',
									read_only=True)

	class Meta:
		model = Feedback
		fields = ['student', 'timestamp', 'feedback_text']


class StudentCourseSerializer(serializers.ModelSerializer):
	materials = MaterialSerializer(many=True, read_only=True)
	assignments = AssignmentSerializer(many=True, read_only=True)

	instructor_name = serializers.CharField(
		source='instructor.user.get_full_name', read_only=True)
	instructor_email = serializers.CharField(source='instructor.user.email',
											 read_only=True)

	number_students_enrolled = serializers.SerializerMethodField(
		'get_number_enrolled')

	def get_number_enrolled(self, obj):
		return obj.students.count()

	class Meta:
		model = Course
		fields = ['module_code', 'title', 'instructor_name', 'instructor_email',
				  'number_students_enrolled', 'materials', 'assignments']


class TeacherCourseSerializer(serializers.ModelSerializer):
	materials = MaterialSerializer(many=True, read_only=True)
	assignments = AssignmentSerializer(many=True, read_only=True)
	feedbacks = FeedbackSerializer(many=True, read_only=True,
								   source='feedbacks_received')

	number_students_enrolled = serializers.SerializerMethodField(
		'get_number_enrolled')

	def get_number_enrolled(self, obj):
		return obj.students.count()

	class Meta:
		model = Course
		fields = ['module_code', 'title', 'number_students_enrolled',
				  'materials', 'assignments', 'feedbacks']
