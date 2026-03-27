"""
Production settings for SmartLaundry Django Backend
Use this for production deployments only
"""

import os
from pathlib import Path
from .settings import *  # noqa - import all base settings
from .monitoring import init_sentry, init_datadog, SENTRY_CONFIG, DATADOG_CONFIG

# MONITORING INITIALIZATION
# =========================

# Initialize Sentry for error tracking
if SENTRY_CONFIG['enabled']:
    init_sentry(environment=os.getenv('ENVIRONMENT', 'production'))

# Initialize Datadog for APM and profiling
if DATADOG_CONFIG['enabled']:
    init_datadog(service_name='smartlaundry', environment=os.getenv('ENVIRONMENT', 'production'))

# SECURITY SETTINGS
# ================

DEBUG = False

# Allowed hosts - Set via environment variable
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Security headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_SECURITY_POLICY = {
    "default-src": ("'self'",),
    "script-src": ("'self'", "'unsafe-inline'"),
    "style-src": ("'self'", "'unsafe-inline'"),
    "img-src": ("'self'", "data:", "https:"),
    "font-src": ("'self'",),
    "connect-src": ("'self'", "https:"),
}

# HTTPS/SSL Settings
SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', 'True') == 'True'
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
CSRF_TRUSTED_ORIGINS = os.getenv('CSRF_TRUSTED_ORIGINS', '').split(',') if os.getenv('CSRF_TRUSTED_ORIGINS') else []

# Security middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # For serving static files
    'backend.monitoring.MonitoringMiddleware',  # Request/response monitoring
] + MIDDLEWARE

# CORS Settings
CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', '').split(',') if os.getenv('CORS_ALLOWED_ORIGINS') else []

# Database Settings
# =================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'smartlaundry'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
        'ATOMIC_REQUESTS': True,
        'CONN_MAX_AGE': 600,
        'OPTIONS': {
            'sslmode': 'require' if os.getenv('DB_SSL', 'False') == 'True' else 'disable',
        },
    }
}

# Cache Settings
# ==============

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {'max_connections': 50},
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
        }
    }
}

# Session using Redis cache
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# Celery Settings for Background Tasks
# =====================================

CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://127.0.0.1:6379/2')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://127.0.0.1:6379/3')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_RESULT_EXPIRES = 3600
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes
CELERY_TASK_SOFT_TIME_LIMIT = 25 * 60  # 25 minutes
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_WORKER_MAX_TASKS_PER_CHILD = 1000

# Channels Settings for WebSocket
# ===============================

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [(os.getenv('REDIS_HOST', '127.0.0.1'), int(os.getenv('REDIS_PORT', 6379)))],
            'capacity': 3000,
            'expiry': 10,
            'symmetric_encryption_keys': [os.getenv('SECRET_KEY')],
        },
    },
}

# Logging Configuration
# ====================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {asctime} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/smartlaundry/django.log',
            'maxBytes': 1024 * 1024 * 100,  # 100 MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'celery_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/smartlaundry/celery.log',
            'maxBytes': 1024 * 1024 * 100,  # 100 MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console', 'file'],
            'level': 'WARNING',
            'propagate': False,
        },
        'celery': {
            'handlers': ['console', 'celery_file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Storage Settings
# ================

# Use S3 for file storage in production
if os.getenv('USE_S3', 'False') == 'True':
    STORAGES = {
        'default': {
            'BACKEND': 'storages.backends.s3boto3.S3Boto3Storage',
            'OPTIONS': {
                'bucket_name': os.getenv('AWS_STORAGE_BUCKET_NAME'),
                'region_name': os.getenv('AWS_S3_REGION_NAME', 'us-east-1'),
                'access_key': os.getenv('AWS_ACCESS_KEY_ID'),
                'secret_key': os.getenv('AWS_SECRET_ACCESS_KEY'),
                'custom_domain': os.getenv('AWS_S3_CUSTOM_DOMAIN', ''),
                'location': 'media',
                'file_overwrite': False,
            },
        },
        'staticfiles': {
            'BACKEND': 'storages.backends.s3boto3.S3StaticStorage',
            'OPTIONS': {
                'bucket_name': os.getenv('AWS_STORAGE_BUCKET_NAME'),
                'region_name': os.getenv('AWS_S3_REGION_NAME', 'us-east-1'),
                'access_key': os.getenv('AWS_ACCESS_KEY_ID'),
                'secret_key': os.getenv('AWS_SECRET_ACCESS_KEY'),
                'custom_domain': os.getenv('AWS_S3_CUSTOM_DOMAIN', ''),
                'location': 'static',
            },
        },
    }
    AWS_S3_SIGNATURE_VERSION = 's3v4'
    AWS_S3_ADDRESSING_STYLE = 'virtual'
else:
    STORAGES = {
        'default': {
            'BACKEND': 'django.core.files.storage.FileSystemStorage',
            'OPTIONS': {
                'location': '/var/www/smartlaundry/media',
                'base_url': '/media/',
            },
        },
        'staticfiles': {
            'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
        },
    }

MEDIA_URL = '/media/'
MEDIA_ROOT = '/var/www/smartlaundry/media'

STATIC_URL = '/static/'
STATIC_ROOT = '/var/www/smartlaundry/static'

# Static files compression
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Email Settings
# ==============

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@smartlaundry.com')

# API Settings
# ============

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
    },
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
}

# Stripe Settings
# ===============

STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', '')
STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY', '')

# Sentry Error Tracking
# ====================

if os.getenv('SENTRY_DSN'):
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.celery import CeleryIntegration

    sentry_sdk.init(
        dsn=os.getenv('SENTRY_DSN'),
        integrations=[
            DjangoIntegration(),
            CeleryIntegration(),
        ],
        traces_sample_rate=0.1,
        send_default_pii=False,
        environment=os.getenv('ENVIRONMENT', 'production'),
    )

# Monitoring & Health Check
# ==========================

HEALTH_CHECK_PATHS = [
    'django.db',
    'django_redis',
    'celery',
]

# Performance Settings
# ====================

# Optimize Django ORM
CONN_MAX_AGE = 600
ATOMIC_REQUESTS = True

# Compress responses
MIDDLEWARE += ['django.middleware.gzip.GZipMiddleware']

# Template caching
TEMPLATES[0]['OPTIONS']['loaders'] = [
    ('django.template.loaders.cached.Loader', [
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    ]),
]

# Optimize static files
WHITENOISE_COMPRESSION_QUALITY = 90
WHITENOISE_SKIP_COMPRESS_OFFLINE = ['admin', 'rest_framework']
