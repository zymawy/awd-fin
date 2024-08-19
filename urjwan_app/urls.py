from django.urls import path
from . import views
from . import api
from django.contrib.auth.decorators import login_required
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import UserProfileViewSet, CourseViewSet, MaterialViewSet, \
	AssignmentViewSet, FeedbackViewSet, NotificationViewSet, ChatMessageViewSet
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

router = DefaultRouter()
router.register(r'userprofiles', UserProfileViewSet)
router.register(r'courses', CourseViewSet)
router.register(r'materials', MaterialViewSet)
router.register(r'assignments', AssignmentViewSet)
router.register(r'feedbacks', FeedbackViewSet)
router.register(r'notifications', NotificationViewSet)
router.register(r'chatmessages', ChatMessageViewSet)
schema_view = get_schema_view(
	openapi.Info(
		title="Urjwan API",
		default_version='v1',
		description="API documentation for Urjwan",
	),
	public=True,
	permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
	path('docs/', schema_view.with_ui('swagger', cache_timeout=0),
		 name='api_docs'),
	path('redoc/', schema_view.with_ui('redoc', cache_timeout=0),
		 name='schema-redoc'),
	# path("__reload__/", include("django_browser_reload.urls")),
	path('api/', include(router.urls)),
	path("", views.index, name="home"),
	# URLs for user management
	path("login/", views.login_user, name="login"),
	path("logout/", views.logout_user, name="logout"),
	path("signup/", views.register, name="signup"),

	# path("profile", login_required(views.ProfileDetail.as_view()), name="profile"),
	path("profile/<int:pk>", login_required(views.ProfileDetail.as_view()),
		 name="profile"),
	path("change-photo/", login_required(views.PictureUpdate.as_view()),
		 name="change_photo"),
	path("update-status/", login_required(views.StatusUpdate.as_view()),
		 name="update_status"),
	path("users/", login_required(views.UserList.as_view()), name="users"),

	# URLs for course management
	path("courses/", login_required(views.CourseList.as_view()),
		 name="courses"),
	path("courses/create", login_required(views.CourseCreate.as_view()),
		 name="courses.create"),
	path("courses/<int:pk>", views.CourseDetail.as_view(), name="courses.show"),
	path("courses/<int:pk>/destroy",
		 login_required(views.CourseDelete.as_view()), name="courses.destroy"),
	path("courses/<int:course_pk>/materials/",
		 login_required(views.MaterialCreate.as_view()),
		 name="material.create"),
	path("courses/<int:course_pk>/materials/<int:pk>",
		 login_required(views.MaterialDelete.as_view()),
		 name="material.destroy"),
	path("courses/<int:course_pk>/assignments",
		 login_required(views.AssignmentCreate.as_view()),
		 name="assignments.create"),
	path("courses/<int:course_pk>/assignments/<int:pk>",
		 login_required(views.AssignmentDelete.as_view()),
		 name="assignments.destroy"),
	path("courses/<int:course_pk>/enrollments", views.enrollments,
		 name="enrollments.create"),
	path("courses/<int:course_pk>/enrollments/<int:student_id>/",
		 views.enrollmentsDestory, name="enrollments.destroy"),
	path("courses/<int:course_pk>/enrollments_bulk",
		 login_required(views.EnrollStudents.as_view()),
		 name="enrollments.index"),
	path("courses/<int:course_pk>/feedback",
		 login_required(views.FeedbackCreate.as_view()), name="feedback.store"),
	path("mark-as-read/<int:pk>/", views.mark_as_read, name="mark_as_read"),
]
