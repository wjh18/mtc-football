import os
from pathlib import Path

from django.contrib.messages import constants as messages
from dotenv import load_dotenv

from apps.core.utils import env_to_bool

load_dotenv() # Load env variables (local)


### Security

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = int(os.environ.get("DJANGO_DEBUG", default=0))

ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost 127.0.0.1 [::1]").split(" ")

# Production security settings
SECURE_SSL_REDIRECT = env_to_bool(os.environ.get("DJANGO_SECURE_SSL_REDIRECT", default=True))
SECURE_HSTS_SECONDS = int(os.environ.get("DJANGO_SECURE_HSTS_SECONDS", default=2592000))
SECURE_HSTS_INCLUDE_SUBDOMAINS = env_to_bool(os.environ.get("DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS",
    default=True))
SECURE_HSTS_PRELOAD = env_to_bool(os.environ.get("DJANGO_SECURE_HSTS_PRELOAD", default=True))
SESSION_COOKIE_SECURE = env_to_bool(os.environ.get("DJANGO_SESSION_COOKIE_SECURE", default=True))
CSRF_COOKIE_SECURE = env_to_bool(os.environ.get("DJANGO_CSRF_COOKIE_SECURE", default=True))


### Applications

INSTALLED_APPS = [
    # Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.sitemaps',

    # 3rd-party
    'crispy_forms',
    'crispy_bootstrap5',
    'allauth',
    'allauth.account',
    'django_extensions',
    'debug_toolbar',

    # Custom
    'apps.accounts.apps.AccountsConfig',
    'apps.web.apps.WebConfig',
    'apps.core.apps.CoreConfig',
    'apps.leagues.apps.LeaguesConfig',
    'apps.teams.apps.TeamsConfig',
    'apps.personnel.apps.PersonnelConfig',
    'apps.matchups.apps.MatchupsConfig',
    'apps.seasons.apps.SeasonsConfig',
]


### Middleware, routing, URLs and WSGI

WSGI_APPLICATION = 'config.wsgi.application'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]
ROOT_URLCONF = 'config.urls'

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


### Templates and forms

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [str(BASE_DIR.joinpath('templates'))],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # Custom context processors
                'apps.core.context_processors.site',
                'apps.web.context_processors.google_tag_manager_id',
                'apps.web.context_processors.font_awesome_kit_id',
                # For advance season form used in base template               
                'apps.seasons.context_processors.advance_season_form',
                'apps.teams.context_processors.user_team',  # Active user team
            ],
        },
    },
]

### Database

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DJANGO_POSTGRES_NAME'),
        'USER': os.environ.get('DJANGO_POSTGRES_USER'),
        'PASSWORD': os.environ.get('DJANGO_POSTGRES_PASS'),
        'HOST': os.environ.get('DJANGO_POSTGRES_HOST'),
        'PORT': os.environ.get('DJANGO_POSTGRES_PORT'),
    }
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'  # Primary key type


### Internationalization

USE_I18N = True
LANGUAGE_CODE = 'en-us'

USE_TZ = True
TIME_ZONE = 'America/New_York'


### Static & Media files

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = (str(BASE_DIR.joinpath('static')),)
STATIC_ROOT = str(BASE_DIR.joinpath('staticfiles'))
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = str(BASE_DIR.joinpath('media'))


### Sites framework

SITE_ID = 1


### Authentication

AUTH_USER_MODEL = 'accounts.CustomUser'  # Custom User

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',  # default
    'allauth.account.auth_backends.AuthenticationBackend',
]

LOGIN_URL = 'account_login'
LOGIN_REDIRECT_URL = 'web:home'
LOGOUT_REDIRECT_URL = 'web:home'

# django-allauth config
ACCOUNT_LOGOUT_REDIRECT = 'web:home'
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = False
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_EMAIL_VERIFICATION = 'optional'

PASSWORD_RESET_TIMEOUT = 259200  # Default
PASSWORD_HASHERS = [
    # Defaults
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
]
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


### Email

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

ADMINS = [('Admin', 'admin@example.com')] # Needed for mailing admins

SERVER_EMAIL = 'contact@example.com' # Needed for mailing admins
DEFAULT_FROM_EMAIL = 'admin@example.com'


### Messages

MESSAGE_TAGS = {
    messages.DEBUG: 'alert-info',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}


### Django Crispy Forms

CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'


### Django Debug Toolbar

SHOW_TOOLBAR = True # False to disable toolbar globally

if DEBUG and DATABASES['default']['HOST'] == 'db':
    # Docker IPs
    import socket  # only if you haven't already imported this
    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS = [ip[: ip.rfind(".")] + ".1" for ip in ips] + ["127.0.0.1", "10.0.2.2"]
elif DEBUG:
    # Non-Docker IPs
    INTERNAL_IPS = ["127.0.0.1"]

DEBUG_TOOLBAR_CONFIG = {
    'DISABLE_PANELS': {
        'debug_toolbar.panels.history.HistoryPanel',
        'debug_toolbar.panels.versions.VersionsPanel',
        'debug_toolbar.panels.timer.TimerPanel',
        'debug_toolbar.panels.settings.SettingsPanel',
        'debug_toolbar.panels.headers.HeadersPanel',
        'debug_toolbar.panels.request.RequestPanel',
        'debug_toolbar.panels.sql.SQLPanel',
        'debug_toolbar.panels.staticfiles.StaticFilesPanel',
        'debug_toolbar.panels.templates.TemplatesPanel',
        'debug_toolbar.panels.cache.CachePanel',
        'debug_toolbar.panels.signals.SignalsPanel',
        'debug_toolbar.panels.logging.LoggingPanel',
        'debug_toolbar.panels.redirects.RedirectsPanel',
        'debug_toolbar.panels.profiling.ProfilingPanel',
    },
    'SHOW_COLLAPSED': True,  # Collapse toolbar by default
    'SHOW_TOOLBAR_CALLBACK': 'apps.core.services.config.show_toolbar'
}


### 3rd-party env vars

GTM_ID = os.environ.get('GTM_ID', '') # Google Tag Manager ID
FONT_AWESOME_KIT_ID = os.environ.get('FA_KIT_ID', '') # Font Awesome icons
