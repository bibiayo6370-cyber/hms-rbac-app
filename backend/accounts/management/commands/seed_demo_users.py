from django.core.management.base import BaseCommand
from accounts.models import User, Role

DEMO_PASSWORD = "HimsDemo123!"

DEMO_USERS = [
    ("superadmin", Role.SUPER_ADMIN, "Super", "Admin"),
    ("admin", Role.ADMIN, "Ada", "Minlai"),
    ("doctor", Role.DOCTOR, "David", "Ogunleye"),
    ("nurse", Role.NURSE, "Nkechi", "Eze"),
    ("labtech", Role.LAB_TECH, "Larry", "Bello"),
    ("pharmacist", Role.PHARMACIST, "Peju", "Adewale"),
    ("billing", Role.BILLING_OFFICER, "Biodun", "Ojo"),
]


class Command(BaseCommand):
    help = "Creates one demo user per role for local development/testing."

    def handle(self, *args, **options):
        for username, role, first, last in DEMO_USERS:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "role": role,
                    "first_name": first,
                    "last_name": last,
                    "email": f"{username}@hims.test",
                    "is_staff": role in (Role.SUPER_ADMIN, Role.ADMIN),
                    "is_superuser": role == Role.SUPER_ADMIN,
                },
            )
            user.set_password(DEMO_PASSWORD)
            user.role = role
            user.save()
            status = "created" if created else "updated"
            self.stdout.write(self.style.SUCCESS(f"{status}: {username} ({role})"))

        self.stdout.write(self.style.WARNING(
            f"\nAll demo users share the password: {DEMO_PASSWORD}"
        ))
