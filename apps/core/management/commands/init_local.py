from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.core.management.utils import get_random_secret_key


class Command(BaseCommand):
    """
    Generates a secret key, creates a .env.dev file at the root of
    the project, and writes local environment variables to it.
    """

    help = "Initializes environment variables required to run the project"

    def add_arguments(self, parser):
        parser.add_argument("db_name", type=str)

    def handle(self, *args, **options):
        secret_key = get_random_secret_key()
        db_name = options["db_name"]
        file_path = f"{settings.BASE_DIR}/.env.dev"

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(self._get_file_contents(secret_key, db_name))
            self.stdout.write(self.style.SUCCESS("Successfully initialized project"))
        except FileNotFoundError:
            raise CommandError("Unable to locate base directory")

    def _get_file_contents(self, secret_key, db_name):
        return (
            "DJANGO_DEBUG=1\n"
            f"DJANGO_SECRET_KEY={secret_key}\n"
            "DJANGO_ALLOWED_HOSTS=localhost 127.0.0.1 [::1]\n"
            "DJANGO_SQL_ENGINE=django.db.backends.postgresql\n"
            f"DJANGO_SQL_DATABASE={db_name}_dev\n"
            f"DJANGO_SQL_USER={db_name}\n"
            f"DJANGO_SQL_PASSWORD={db_name}\n"
            "DJANGO_SQL_HOST=db\n"
            "DJANGO_SQL_PORT=5432\n"
        )
