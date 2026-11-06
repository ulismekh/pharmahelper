import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "Create an admin user from environment variables"

    def handle(self, *args, **kwargs):
        User = get_user_model()

        username = os.environ.get("ADMIN_USERNAME")
        password = os.environ.get("ADMIN_PASSWORD")
        email = os.environ.get("ADMIN_EMAIL", "")

        if not username or not password:
            self.stdout.write("Admin credentials are not configured.")
            return

        if User.objects.filter(username=username).exists():
            self.stdout.write("Admin already exists.")
            return

        User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
        )

        self.stdout.write(self.style.SUCCESS("Admin created."))