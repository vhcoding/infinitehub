from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.home.models import Profile


class Command(BaseCommand):
    help = 'Create Profile objects for existing users'

    def handle(self, *args, **options):
        # Get all existing users
        users = User.objects.all()

        # Loop through the users and create a Profile for each
        for user in users:
            profile, created = Profile.objects.get_or_create(user=user)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Profile created for user: {user.username}'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Profile already exists for user: {user.username}'))
