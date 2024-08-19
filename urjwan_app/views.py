from django.shortcuts import render
from django.contrib.auth import login, logout
from django.contrib.auth.models import Group
import platform
import django
from django.http import HttpResponseRedirect
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django.http import JsonResponse

from .forms import *
from django.views.generic import DetailView, UpdateView, DeleteView, \
	ListView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy
from django.views.generic import CreateView
from urjwan_app.models import Course
from urjwan_app.forms import CourseForm
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from channels.layers import get_channel_layer
from django.urls import reverse
from asgiref.sync import async_to_sync
import json
from rest_framework import viewsets
from .models import UserProfile, Course, Material, Assignment, Feedback, \
	Notification, ChatMessage
from .serializers import UserProfileSerializer, CourseSerializer, \
	MaterialSerializer, AssignmentSerializer, FeedbackSerializer, \
	NotificationSerializer, ChatMessageSerializer


def register(request):
	registered = False

	if request.method == "POST":
		user_form = UserForm(data=request.POST)
		profile_form = UserProfileForm(data=request.POST)

		if user_form.is_valid() and profile_form.is_valid():
			try:
				user = user_form.save(commit=False)
				user.username = user.email
				user.set_password(user.password)
				user.save()
				profile = profile_form.save(commit=False)
				profile.user = user

				if "photo" in request.FILES:
					profile.photo = request.FILES["photo"]
				else:
					profile.photo = "urjwan_app/user_photos/default_user.png"

				student_group = Group.objects.get(name='student')
				student_group.user_set.add(user)
				profile.is_student = True
				profile.is_instructor = False

				profile.save()
				registered = True

				# Redirect to the profile page after successful registration
				login(request, user)
				return HttpResponseRedirect(reverse('profile', args=[user.id]))

			except IntegrityError:
				return render(request, "urjwan/signup.html",
							  {"user_form": user_form,
							   "profile_form": profile_form,
							   "registered": registered,
							   "error": "You already have an account. Please login instead."})

		else:
			return render(request, "urjwan/signup.html",
						  {"user_form": user_form, "profile_form": profile_form,
						   "registered": registered,
						   "error": "Please fill in all entries in the form to register."})
			print(user_form.errors, profile_form.errors)
	else:
		user_form = UserForm()
		profile_form = UserProfileForm()

	return render(request, "urjwan/signup.html",
				  {"user_form": user_form, "profile_form": profile_form,
				   "registered": registered})


def login_user(request):
	if request.method == "POST":
		# handling form submission
		email = request.POST["email"]
		password = request.POST["password"]
		try:
			user = User.objects.get(username=email)
			if user.check_password(password):
				if user.is_active:
					login(request, user)
					return HttpResponseRedirect("/")  # Redirect to index page
				else:
					return render(request, "urjwan/login.html", {
						"error": "Your account is disabled, please reach out to your administrator to enable it."})
			else:
				return render(request, "urjwan/login.html",
							  {"error": "Invalid email or password"})
		except User.DoesNotExist:
			return render(request, "urjwan/login.html",
						  {"error": "Invalid email or password"})
	else:
		# leading the login page
		return render(request, "urjwan/login.html")


def logout_user(request):
	logout(request)
	return HttpResponseRedirect("/login")


def index(request):
	user_profile = None
	notifications = []
	courses_enrolled = []
	courses_taught = []

	if request.user.is_authenticated:
		user_profile = UserProfile.objects.get(user=request.user)
		courses_taught = Course.objects.filter(instructor=user_profile)

	available_courses = Course.objects.all()[:6]
	python_version = platform.python_version()
	django_version = django.get_version()
	server_time = timezone.now()

	context = {
		'user_profile': user_profile,
		'notifications': notifications,
		'courses_taught': courses_taught,
		'available_courses': available_courses,
		'python_version': python_version,
		'django_version': django_version,
		'server_time': server_time,
	}
	return render(request, "urjwan/index.html", context)


class ProfileDetail(DetailView):
	model = User
	template_name = "urjwan/profile.html"
	context_object_name = "user"

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)

		# Get the user being viewed (the one whose profile is visited)
		viewed_user = self.get_object()
		context["other_user_profile"] = get_object_or_404(UserProfile,
														  user=viewed_user)

		# Get the details of the logged-in user (authenticated user)
		logged_in_user = self.request.user
		context["user_profile"] = UserProfile.objects.get(user=logged_in_user)

		# Check if the logged-in user is viewing their own profile
		context["is_own_profile"] = logged_in_user == viewed_user

		# Get courses enrolled/taught by the viewed user
		context["other_courses_taught"] = context[
			"other_user_profile"].courses_taught.all()
		context["other_courses_enrolled"] = context[
			"other_user_profile"].courses_enrolled.all()

		# Fetch notifications only if the logged-in user is viewing their own profile
		if context["is_own_profile"]:
			context["notifications"] = Notification.objects.filter(
				to_user=context["user_profile"]).order_by('-timestamp')

		return context


class PictureUpdate(UpdateView):
	model = UserProfile
	template_name = "urjwan/change_photo.html"
	form_class = UserProfileForm
	success_url = "/"

	def get_object(self, queryset=None):
		return self.request.user.userprofile

	def form_valid(self, form):
		# Get the user profile object
		user_profile = form.save(commit=False)
		# add the uploaded photo to the user profile
		user_profile.photo = form.cleaned_data['photo']
		user_profile.save()
		return super().form_valid(form)


class StatusUpdate(UpdateView):
	model = UserProfile
	template_name = "urjwan/change_status.html"
	form_class = UpdateStatusForm
	success_url = "/"

	def get_object(self, queryset=None):
		return self.request.user.userprofile

	def form_valid(self, form):
		# Get the user profile object
		user_profile = form.save(commit=False)
		# add the uploaded photo to the user profile
		user_profile.status = form.cleaned_data['status']
		user_profile.save()
		return super().form_valid(form)


class UserList(ListView):
	model = User
	template_name = "urjwan/users.html"
	context_object_name = "users"
	paginate_by = 10  # Display 10 users per page

	def get_queryset(self):
		user_profile = UserProfile.objects.get(user=self.request.user)
		search_query = self.request.GET.get('search')

		if user_profile.user_type == 'instructor':
			# Instructors can view both students and instructors / exclude current user
			queryset = User.objects.exclude(id=self.request.user.id)
		else:
			# Students can only view other students / exclude current user
			queryset = User.objects.filter(
				userprofile__user_type='student').exclude(
				id=self.request.user.id)

		if search_query:
			queryset = queryset.filter(
				first_name__startswith=search_query) | queryset.filter(
				last_name__startswith=search_query) | queryset.filter(
				email__startswith=search_query)

		return queryset.order_by('first_name')

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		user_profile = UserProfile.objects.get(user=self.request.user)
		context["user_profile"] = user_profile
		return context



class CourseDetail(DetailView):
	model = Course
	template_name = "urjwan/course.html"
	context_object_name = "course"

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		course = self.object
		user_profile = None
		if self.request.user.is_authenticated:
			user_profile = UserProfile.objects.get(user=self.request.user)

		context["students"] = course.students.all()
		context["instructor"] = course.instructor
		context["user_profile"] = user_profile
		context["user"] = self.request.user
		context[
			"user_id"] = self.request.user.id if self.request.user.is_authenticated else None
		context["materials"] = course.materials.all()
		context["assignments"] = course.assignments.all()
		context["feedbacks"] = course.feedbacks_received.all()
		context[
			"feedbacks_shared"] = user_profile.feedbacks_given.all() if user_profile else None

		# For chat
		context[
			"username"] = self.request.user.get_full_name() if self.request.user.is_authenticated else "Guest"
		context[
			"auth_group"] = "student" if user_profile and user_profile.is_student else "instructor" if user_profile and user_profile.is_instructor else "guest"
		context["room_name"] = course.module_code
		context['form'] = MaterialForm()
		context['assignment_form'] = AssignmentForm()
		return context


class CourseCreate(PermissionRequiredMixin, CreateView):
	permission_required = 'urjwan_app.add_course'
	model = Course
	template_name = "urjwan/course_form.html"
	form_class = CourseForm
	success_url = reverse_lazy(
		'courses')

	def dispatch(self, request, *args, **kwargs):
		# Check if the user has the required permission
		if not request.user.has_perm(self.permission_required):
			return HttpResponse(
				status=404)  # Or return a 403 Forbidden error if you prefer
		return super().dispatch(request, *args, **kwargs)

	def form_valid(self, form):
		# Associate the logged-in user (as instructor) with the course
		user_profile = self.request.user.userprofile
		form.instance.instructor = user_profile
		return super().form_valid(form)

	def form_invalid(self, form):
		# Handle form errors and return a JSON response if it's an AJAX request
		if self.request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
			return JsonResponse(form.errors, status=400)
		return super().form_invalid(form)


class CourseDelete(PermissionRequiredMixin, DeleteView):
	permission_required = 'urjwan_app.delete_course'
	model = Course
	success_url = '/'

	def dispatch(self, request, *args, **kwargs):
		try:
			if not request.user.has_perm('urjwan_app.delete_course'):
				return HttpResponse(status=404)
		except PermissionDenied:
			pass
		return super().dispatch(request, *args, **kwargs)

	def delete(self, request, *args, **kwargs):
		self.object = self.get_object()
		self.object.delete()

		if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
			return JsonResponse({"message": "Course deleted successfully!",
								 "redirect_url": self.success_url})

		return HttpResponseRedirect(self.success_url)


class CourseList(ListView):
	permission_required = 'urjwan_app.view_course'

	def dispatch(self, request, *args, **kwargs):
		try:
			if not request.user.has_perm('urjwan_app.view_course'):
				return HttpResponse(status=404)
		except PermissionDenied:
			pass
		return super().dispatch(request, *args, **kwargs)

	model = Course
	template_name = "urjwan/courses.html"
	context_object_name = "courses"

	# sort data by module_code
	def get_queryset(self):
		search_query = self.request.GET.get('search')
		# Filter users by first name, last name, and email starting with the value entered in the search query
		if search_query:
			queryset = Course.objects.filter(
				module_code__startswith=search_query) | Course.objects.filter(
				title__contains=search_query)
		else:
			queryset = Course.objects.all()
		return queryset.order_by('module_code')

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		user_profile = UserProfile.objects.get(user=self.request.user)
		context["courses_taught"] = user_profile.courses_taught.all()
		context["courses_enrolled"] = user_profile.courses_enrolled.all()
		context["user_profile"] = user_profile
		context['search_query'] = self.request.GET.get('search', '')

		return context


class MaterialCreate(CreateView):
	model = Material
	form_class = MaterialForm
	permission_required = 'urjwan_app.add_material'

	def dispatch(self, request, *args, **kwargs):
		try:
			if not request.user.has_perm('urjwan_app.add_material'):
				return JsonResponse({'error': 'Permission denied'}, status=403)
		except PermissionDenied:
			pass
		return super().dispatch(request, *args, **kwargs)

	def get_success_url(self):
		return reverse('courses.show', kwargs={'pk': self.kwargs['course_pk']})

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		course = get_object_or_404(Course, pk=self.kwargs['course_pk'])
		context["course"] = course
		return context

	def form_valid(self, form):
		course = get_object_or_404(Course, pk=self.kwargs['course_pk'])
		material = form.save(commit=False)
		material.course = course
		material.save()

		# Create a notification for each student in the course
		for student in course.students.all():
			notification = Notification(to_user=student,
										from_user=course.instructor,
										course=course,
										message=course.instructor.user.get_full_name() + " has added new material to the course.")
			notification.save()
			notify(notification, student)

		if self.request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
			return JsonResponse({'success': True})

		return super().form_valid(form)

	def form_invalid(self, form):
		if self.request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
			return JsonResponse(form.errors, status=400)
		return super().form_invalid(form)


class MaterialDelete(PermissionRequiredMixin, DeleteView):
	permission_required = 'urjwan_app.delete_material'
	model = Material
	context_object_name = 'material'

	def dispatch(self, request, *args, **kwargs):
		try:
			if not request.user.has_perm('urjwan_app.delete_material'):
				return HttpResponse(status=404)
		except PermissionDenied:
			pass
		return super().dispatch(request, *args, **kwargs)

	def delete(self, request, *args, **kwargs):
		material = self.get_object()
		course_pk = material.course.pk  # Get the course primary key for redirect
		material.delete()

		if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
			return JsonResponse({"message": "Material deleted successfully!"})

		return HttpResponseRedirect(self.get_success_url())

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		course = get_object_or_404(Course, pk=self.kwargs['course_pk'])
		context["course"] = course
		return context

	def get_success_url(self):
		return reverse('courses.show', kwargs={'pk': self.kwargs['course_pk']})


class AssignmentCreate(CreateView):
	permission_required = 'urjwan_app.add_assignment'

	def dispatch(self, request, *args, **kwargs):
		try:
			if not request.user.has_perm('urjwan_app.add_assignment'):
				# Return 404 error if user does not have permission to add a course
				return HttpResponse(status=404)
		except PermissionDenied:
			# Handle PermissionDenied exception without raising it further
			pass
		return super().dispatch(request, *args, **kwargs)

	model = Assignment
	form_class = AssignmentForm

	def get_success_url(self):
		return reverse('courses.show', kwargs={'pk': self.kwargs['course_pk']})

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		course = Course.objects.get(pk=self.kwargs['course_pk'])
		context["course"] = course
		return context

	def form_valid(self, form):
		# Get the course object
		course = Course.objects.get(pk=self.kwargs['course_pk'])
		# add assignment to the course
		assignment = form.save(commit=False)
		assignment.course = course
		assignment.save()

		# Create a notification for each student in the course
		for student in course.students.exclude(user_type='instructor'):
			print(student.user_id)
			notification = Notification(to_user=student,
										from_user=course.instructor,
										course=course,
										message=course.instructor.user.get_full_name() + " has added new assignment to the course.")
			notification.save()
			notify(notification, student)

		if self.request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
			return JsonResponse({"message": "Assignment created successfully!",
								 "assignment_id": assignment.id})

		return super().form_valid(form)


class AssignmentDelete(DeleteView):
	permission_required = 'urjwan_app.delete_assignment'

	def dispatch(self, request, *args, **kwargs):
		try:
			if not request.user.has_perm('urjwan_app.delete_assignment'):
				# Return 404 error if user does not have permission to add a course
				return HttpResponse(status=404)
		except PermissionDenied:
			# Handle PermissionDenied exception without raising it further
			pass
		return super().dispatch(request, *args, **kwargs)

	model = Assignment

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		course = Course.objects.get(pk=self.kwargs['course_pk'])
		context["course"] = course
		return context

	def get_success_url(self):
		return reverse('courses.show', kwargs={'pk': self.kwargs['course_pk']})


# Enrollment views
# class EnrollStudents(UpdateView):
# 	model = Course
# 	template_name = "urjwan/enrollments_bulk.html"
# 	fields = ['students']
#
# 	# redirect back to course page after updating the students
# 	def get_success_url(self):
# 		return reverse('course', kwargs={'pk': self.kwargs['course_pk']})
#
# 	def get_context_data(self, **kwargs):
# 		context = super().get_context_data(**kwargs)
# 		course = Course.objects.get(pk=self.kwargs['course_pk'])
# 		# get all users with is_student set in their profile
# 		context["all_students"] = UserProfile.objects.filter(is_student=True)
# 		# get all the students enrolled in the course so that we can exclude them from the list of students to be enrolled
# 		context["enrolled_students"] = Course.objects.get(
# 			pk=course.id).students.all()
# 		context["course"] = course
# 		return context
#
# 	# add students to db if form is valid
# 	def form_valid(self, form):
# 		# Get list of selected students from the form submission
# 		selected_student_ids = self.request.POST.getlist('students')
# 		# Add each of the selected students to the course
# 		course = form.instance
# 		for student_id in selected_student_ids:
# 			student = UserProfile.objects.get(pk=student_id)
# 			course.students.add(student)  # Add selected students to the course
#
# 		return super().form_valid(form)

@method_decorator(login_required, name='dispatch')
class EnrollStudents(ListView):
	def get(self, request, course_pk):
		course = get_object_or_404(Course, pk=course_pk)
		# Get all students and the ones already enrolled in the course
		all_students = UserProfile.objects.filter(is_student=True)
		enrolled_students = course.students.all()

		context = {
			'course': course,
			'all_students': all_students,
			'enrolled_students': enrolled_students
		}
		return render(request, 'urjwan/enrollments_bulk.html', context)

	def post(self, request, course_pk):
		course = get_object_or_404(Course, pk=course_pk)
		# Retrieve selected student IDs from the form
		student_ids = request.POST.getlist('students')
		students = UserProfile.objects.filter(id__in=student_ids)
		# Clear current enrollments and reassign the selected students
		course.students.clear()
		course.students.add(*students)

		return HttpResponseRedirect(
			reverse('courses.show', kwargs={'pk': course_pk}))


@login_required
def enrollments(request, course_pk):
	course = Course.objects.get(pk=course_pk)
	user_profile = UserProfile.objects.get(user=request.user)
	course.students.add(user_profile)

	# Create a notification to instructor when student enrolls in the course
	message = user_profile.user.get_full_name() + " has enrolled in the course."
	notification = Notification(to_user=course.instructor,
								from_user=user_profile, course=course,
								type=message)
	notification.save()
	# let's notify the instructor
	notify(notification, course.instructor)

	if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
		return JsonResponse(
			{"message": "Enrolled successfully!", "course_id": course_pk})

	return HttpResponseRedirect(
		reverse('courses.show', kwargs={'pk': course_pk}))


@login_required
def enrollmentsDestory(request, course_pk, student_id):
	course = Course.objects.get(pk=course_pk)
	user_profile = UserProfile.objects.get(user=student_id)
	course.students.remove(user_profile)

	if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
		return JsonResponse(
			{"message": "Enrolled successfully!", "course_id": course_pk,
			 "redirect_url": "/"})

	return HttpResponseRedirect("/")


# Feedback views
class FeedbackCreate(CreateView):
	model = Feedback
	form_class = FeedbackForm

	def get_success_url(self):
		return reverse('courses.show', kwargs={'pk': self.kwargs['course_pk']})

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		course = Course.objects.get(pk=self.kwargs['course_pk'])
		student = UserProfile.objects.get(user=self.request.user)
		context["course"] = course
		context["student"] = student
		return context

	def form_valid(self, form):
		course = Course.objects.get(pk=self.kwargs['course_pk'])
		student = UserProfile.objects.get(user=self.request.user)
		feedback = form.save(commit=False)
		feedback.course = course
		feedback.student = student
		feedback.save()

		for instructor in course.students.filter(user_type='instructor'):
			message = student.user.get_full_name() + " added new feedback 💬."
			notification = Notification(to_user=instructor,
										from_user=student, course=course,
										message=message)
			notification.save()
			# let's notify the instructor
			notify(notification, instructor)

		if self.request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
			return JsonResponse({"message": "Feedback submitted successfully!"})

		return super().form_valid(form)

	def form_invalid(self, form):
		if self.request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
			return JsonResponse(form.errors, status=400)
		return super().form_invalid(form)


@login_required
def mark_as_read(request, pk):
	print(pk)
	# Get the notification object
	notification = get_object_or_404(Notification, pk=pk)
	# Ensure the notification belongs to the user
	if notification.to_user != request.user.userprofile:
		return JsonResponse({'error': 'Permission denied'}, status=403)

	# Mark as read
	notification.read_status = True
	notification.save()

	return JsonResponse({'message': 'Notification marked as read'})

	return HttpResponseRedirect("/")


def custom_page_not_found_view(request, exception):
	return render(request, "urjwan/404.html", {})


class UserProfileViewSet(viewsets.ModelViewSet):
	queryset = UserProfile.objects.all()
	serializer_class = UserProfileSerializer


class CourseViewSet(viewsets.ModelViewSet):
	queryset = Course.objects.all()
	serializer_class = CourseSerializer


class MaterialViewSet(viewsets.ModelViewSet):
	queryset = Material.objects.all()
	serializer_class = MaterialSerializer


class AssignmentViewSet(viewsets.ModelViewSet):
	queryset = Assignment.objects.all()
	serializer_class = AssignmentSerializer


class FeedbackViewSet(viewsets.ModelViewSet):
	queryset = Feedback.objects.all()
	serializer_class = FeedbackSerializer


class NotificationViewSet(viewsets.ModelViewSet):
	queryset = Notification.objects.all()
	serializer_class = NotificationSerializer


class ChatMessageViewSet(viewsets.ModelViewSet):
	queryset = ChatMessage.objects.all()
	serializer_class = ChatMessageSerializer


def notify(notification, profile):
	channel_layer = get_channel_layer()
	async_to_sync(channel_layer.group_send)(
		f'notifications_{profile.user.id}',
		{
			'type': 'send_notification',
			'notification': json.dumps({
				'message': notification.message,
				'timestamp': str(notification.timestamp),
				'course_name': notification.course.title if notification.course else '',
			}),
		}
	)
