from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from decouple import config

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        if not User.objects.filter(username=config('DJANGO_SUPERUSER_USERNAME')).exists():
            User.objects.create_superuser(
                username=config('DJANGO_SUPERUSER_USERNAME'),
                email=config('DJANGO_SUPERUSER_EMAIL'),
                password=config('DJANGO_SUPERUSER_PASSWORD')
            )
            self.stdout.write(self.style.SUCCESS('created!'))
        else:
            self.stdout.write(self.style.SUCCESS('already exists'))
