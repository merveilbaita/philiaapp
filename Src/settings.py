from pathlib import Path

import dj_database_url
from decouple import config, Csv

# ------------------------------------------------------------------------------
# Base
# ------------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# ------------------------------------------------------------------------------
# Sécurité / Environnement
# ------------------------------------------------------------------------------
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    default='philiaapp.onrender.com,localhost',
    cast=Csv()
)

# ------------------------------------------------------------------------------
# Applications
# ------------------------------------------------------------------------------
INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
    'boutique.apps.BoutiqueConfig',
    'salon.apps.SalonConfig',
    'widget_tweaks',
    'axes',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',      # sert les static en production
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'axes.middleware.AxesMiddleware',                  # lockout en cas de trop d’échecs de login
]

ROOT_URLCONF = 'Src.urls'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [],
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
        ],
    },
}]

WSGI_APPLICATION = 'Src.wsgi.application'

# ------------------------------------------------------------------------------
# Base de données
# ------------------------------------------------------------------------------
DATABASES = {
    'default': dj_database_url.parse(
        config(
            'DATABASE_URL',
            default='postgresql://postgres:password@localhost:5432/philiaapp_db'
        ),
        conn_max_age=600,
        ssl_require=not DEBUG
    )
}

# ------------------------------------------------------------------------------
# Validation de mot de passe
# ------------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 10}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ------------------------------------------------------------------------------
# Internationalisation
# ------------------------------------------------------------------------------
LANGUAGE_CODE = 'fr-FR'
TIME_ZONE = 'Africa/Lubumbashi'
USE_I18N = True
USE_TZ = True

# ------------------------------------------------------------------------------
# Static files
# ------------------------------------------------------------------------------
STATIC_URL = 'static/'

# ------------------------------------------------------------------------------
# Autres paramètres
# ------------------------------------------------------------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LOGIN_URL = '/connexion/'

# ------------------------------------------------------------------------------
# JAZZMIN (Admin personnalisé)
# ------------------------------------------------------------------------------
JAZZMIN_SETTINGS = {
    "site_title": "Philia App Admin",
    "site_header": "Philia App",
    "site_brand": "Philia App Admin",
    "welcome_sign": "Bienvenue sur l'administration de Philia App",
    "search_model": ["annonces.User", "annonces.Annonce"],
    "topmenu_links": [
        {"name": "Accueil du site", "url": "accueil", "permissions": ["auth.view_user"]},
        {"app": "annonces"},
    ],
    "order_with_respect_to": ["annonces", "auth"],
    "icons": {
        "auth": "fas fa-users-cog",
        "annonces.User": "fas fa-user",
        "annonces.Annonce": "fas fa-home",
        "annonces.Agence": "fas fa-building",
        "annonces.PaiementSimple": "fas fa-money-check-alt",
        "annonces.Avis": "fas fa-comments",
        "annonces.ContactAnnonce": "fas fa-envelope",
    },
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-indigo",
    "accent": "accent-primary",
    "navbar": "navbar-white navbar-light",
    "no_navbar_border": False,
    "navbar_fixed": True,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": True,
    "theme": "litera",
    "dark_mode_theme": "darkly",
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    }
}

# ------------------------------------------------------------------------------
# AXES (protection contre bruteforce pour les connexions)
# ------------------------------------------------------------------------------
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 1  # en heures
AXES_LOCKOUT_TEMPLATE = '403.html'

# ------------------------------------------------------------------------------
# Sentry (monitoring)
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# Sécurité HTTPS / HSTS
# ------------------------------------------------------------------------------
if not DEBUG:
    # Forcer HTTPS
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

    # HSTS
    SECURE_HSTS_SECONDS = 60 * 60 * 24 * 30  # 30 jours
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

    # Headers de sécurité
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'

    SESSION_COOKIE_SAMESITE = 'Lax'
    CSRF_COOKIE_SAMESITE = 'Lax'
else:
    # En développement, ne pas rediriger en HTTPS
    SECURE_SSL_REDIRECT = False


