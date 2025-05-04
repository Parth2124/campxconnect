from django.contrib.auth.management.commands import createsuperuser
from django.core.management import CommandError
from django.contrib.auth import get_user_model
from django.core.validators import validate_email

class Command(createsuperuser.Command):
    help = 'Create a superuser with email, phone, and optional institution/department'

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('--phone', dest='phone', default=None, help='Specifies the phone number for the superuser.')

    def handle(self, *args, **options):
        User = get_user_model()
        email = options.get('email')
        phone = options.get('phone')
        password = options.get('password')

        # Prompt for email if not provided
        if not email:
            email = self.get_input_data('email', 'Email: ', validate_email)

        # Validate email domain
        if not email.endswith('@manavrachna.net'):
            raise CommandError("Email must be a valid Manav Rachna email (e.g., name@manavrachna.net)")

        # Prompt for phone if not provided
        if not phone:
            phone = self.get_input_data('phone', 'Phone: ', lambda x: x if len(x) >= 10 else None)
            if not phone:
                raise CommandError("Phone number must be at least 10 digits")

        # Prompt for password
        if not password:
            password = self.get_input_data('password', 'Password: ', lambda x: x, hidden=True)
            password2 = self.get_input_data('password2', 'Password (again): ', lambda x: x, hidden=True)
            if password != password2:
                raise CommandError("Error: Your passwords didn't match.")

        # Create superuser
        try:
            User.objects.create_superuser(
                email=email,
                phone=phone,
                password=password,
                first_name='Admin',  # Optional, can prompt if needed
                institution=None,    # Superusers don't need institution/department
                department=None
            )
            self.stdout.write(self.style.SUCCESS(f"Superuser created successfully: {email}"))
        except Exception as e:
            raise CommandError(f"Error creating superuser: {str(e)}")

    def get_input_data(self, field_name, message, validator=None, hidden=False):
        """
        Prompt for input and validate if a validator is provided.
        """
        while True:
            if hidden:
                from getpass import getpass
                value = getpass(message)
            else:
                value = input(message).strip()

            if not value:
                self.stderr.write(f"Error: This field cannot be blank.")
                continue

            if validator:
                try:
                    validated_value = validator(value)
                    if validated_value is None:
                        self.stderr.write(f"Error: Invalid {field_name}.")
                        continue
                    return validated_value
                except Exception as e:
                    self.stderr.write(f"Error: {str(e)}")
                    continue
            return value