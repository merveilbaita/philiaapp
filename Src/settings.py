from pathlib import Path

import dj_database_url
from decouple import config, Csv

# Base
BASE_DIR = Path(__file__).resolve().parent.parent

# Sécurité / environnement
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='philiaapp.onrender.com,localhost', cast=Csv())

# Application definition
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
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # <-- pour servir les statics en prod
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'Src.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],  # tu peux ajouter ici des dossiers custom si besoin
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',  # nécessaire pour certains templates/admin
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'Src.wsgi.application'

# Database
DATABASES = {
    'default': dj_database_url.parse(
        config('DATABASE_URL', default='postgresql://postgres:password@localhost:5432/philiaapp_db'),
        conn_max_age=600,
        ssl_require=not DEBUG
    )
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# Internationalisation
LANGUAGE_CODE = 'fr-FR'
TIME_ZONE = 'Africa/Lubumbashi'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'  # collectstatic y déposera les fichiers
STATICFILES_DIRS = [BASE_DIR / 'static']  # si tu as des statics en développement
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'  # versionnée + gzip

# Auth / login
LOGIN_URL = '/connexion/'

# Default primary key
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- JAZZMIN SETTINGS ---
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

# Sécurité complémentaire (optionnel mais recommandé en prod)
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    # Si derrière un proxy SSL (comme Render), déclare ceci :
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = True
    # HSTS (à activer après stabilisation)
    # SECURE_HSTS_SECONDS = 31536000
    # SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    # SECURE_HSTS_PRELOAD = True

