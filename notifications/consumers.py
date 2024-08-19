from channels.generic.websocket import AsyncWebsocketConsumer
import json
from urjwan_app.models import Notification, User
from channels.db import database_sync_to_async

class NotificationConsumer(AsyncWebsocketConsumer):
	async def connect(self):
		self.user_id = self.scope['url_route']['kwargs']['user_id']
		self.user = await self.get_user()

		if self.user.is_authenticated:
			self.group_name = f'notifications_{self.user.id}'

			# Add the user to a notification group
			await self.channel_layer.group_add(
				self.group_name,
				self.channel_name
			)

			# Accept the WebSocket connection
			await self.accept()

			# Fetch old notifications and send them over WebSocket
			old_notifications = await self.get_old_notifications()
			for notification in old_notifications:
				await self.send(text_data=json.dumps({
					'type': 'old_notification',
					'notification': notification,
				}))
		else:
			await self.close()

	async def disconnect(self, close_code):
		if self.user.is_authenticated:
			await self.channel_layer.group_discard(
				self.group_name,
				self.channel_name
			)

	async def receive(self, text_data):
		pass

	async def send_notification(self, event):
		notification = json.loads(event['notification'])
		message = notification.get('message')
		timestamp = notification.get('timestamp')
		course_name = notification.get('course_name', '')

		await self.send(text_data=json.dumps({
			'type': 'new_notification',
			'notification': {
				'message': message,
				'timestamp': timestamp,
				'course_name': course_name,
			},
		}))

	@database_sync_to_async
	def get_user(self):
		return User.objects.get(id=self.user_id)

	@database_sync_to_async
	def get_old_notifications(self):
		notifications = Notification.objects.filter(
			to_user__user=self.user
		).order_by('-timestamp')

		formatted_notifications = []
		for notification in notifications:
			formatted_notifications.append({
				'message': notification.message,
				'timestamp': notification.timestamp.strftime(
					'%Y-%m-%d %H:%M:%S'),  # Format timestamp
				'course_name': notification.course.title if notification.course else '',
				'read_status': notification.read_status,
				'id': notification.id
			})

		return formatted_notifications
