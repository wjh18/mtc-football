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
        parser.add_argument(
            "-l", "--local", action="store_true", help="Using a local env, not Docker"
        )

    def handle(self, *args, **options):
        db_name = options["db_name"]
        local = options["local"]

        secret_key = get_random_secret_key()
        file_path = f"{settings.BASE_DIR}/.env"

        if local:
            # Local db host
            db_host = "127.0.0.1"
        else:
            # Docker db host
            db_host = "db"

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(self._get_file_contents(secret_key, db_name, db_host))
            self.stdout.write(self.style.SUCCESS("Successfully initialized project"))
        except FileNotFoundError:
            raise CommandError("Unable to locate base directory")

    def _get_file_contents(self, secret_key, db_name, db_host):
        return (
            "DJANGO_DEBUG=1\n"
            f"DJANGO_SECRET_KEY={secret_key}\n"
            "DJANGO_ALLOWED_HOSTS=localhost 127.0.0.1 [::1]\n"
            "DJANGO_SQL_ENGINE=django.db.backends.postgresql\n"
            f"DJANGO_SQL_DATABASE={db_name}_dev\n"
            f"DJANGO_SQL_USER={db_name}\n"
            f"DJANGO_SQL_PASSWORD={db_name}\n"
            f"DJANGO_SQL_HOST={db_host}\n"
            "DJANGO_SQL_PORT=5432\n"
        )
