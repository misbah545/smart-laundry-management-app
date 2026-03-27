"""
Environment Variable Loader and Validator for SmartLaundry
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional, Type, Union

# Load .env file
ENV_FILE = Path(__file__).parent / '.env'
if ENV_FILE.exists():
    load_dotenv(ENV_FILE)


class EnvVarError(Exception):
    """Custom exception for environment variable errors"""
    pass


class Config:
    """Central configuration class for environment variables"""

    # Type definitions
    BOOL_MAPPING = {
        'true': True, 'false': False,
        'yes': True, 'no': False,
        '1': True, '0': False,
        'on': True, 'off': False,
    }

    @staticmethod
    def get_bool(key: str, default: bool = False) -> bool:
        """Get boolean environment variable"""
        value = os.getenv(key, str(default)).lower()
        if value not in Config.BOOL_MAPPING:
            raise EnvVarError(f"Invalid boolean value for {key}: {value}")
        return Config.BOOL_MAPPING[value]

    @staticmethod
    def get_str(key: str, default: str = None, required: bool = False) -> str:
        """Get string environment variable"""
        value = os.getenv(key, default)
        if required and not value:
            raise EnvVarError(f"Required environment variable {key} is not set")
        return value

    @staticmethod
    def get_int(key: str, default: int = None, required: bool = False) -> int:
        """Get integer environment variable"""
        value = os.getenv(key, default)
        if required and value is None:
            raise EnvVarError(f"Required environment variable {key} is not set")
        if value is None:
            return default
        try:
            return int(value)
        except ValueError:
            raise EnvVarError(f"Invalid integer value for {key}: {value}")

    @staticmethod
    def get_float(key: str, default: float = None, required: bool = False) -> float:
        """Get float environment variable"""
        value = os.getenv(key, default)
        if required and value is None:
            raise EnvVarError(f"Required environment variable {key} is not set")
        if value is None:
            return default
        try:
            return float(value)
        except ValueError:
            raise EnvVarError(f"Invalid float value for {key}: {value}")

    @staticmethod
    def get_list(key: str, default: list = None, separator: str = ',') -> list:
        """Get list environment variable (comma-separated by default)"""
        value = os.getenv(key)
        if not value:
            return default or []
        return [item.strip() for item in value.split(separator)]

    @staticmethod
    def get_dict(key: str, separator: str = ';', delimiter: str = '=') -> dict:
        """Get dictionary from environment variable (key=value;key=value)"""
        value = os.getenv(key, '')
        result = {}
        if value:
            for pair in value.split(separator):
                if delimiter in pair:
                    k, v = pair.split(delimiter, 1)
                    result[k.strip()] = v.strip()
        return result

    @staticmethod
    def get_choice(key: str, choices: list, default: str = None) -> str:
        """Get environment variable with restricted choices"""
        value = os.getenv(key, default)
        if value not in choices:
            raise EnvVarError(f"{key} must be one of {choices}, got {value}")
        return value

    @staticmethod
    def validate_required(*keys: str) -> None:
        """Validate that required environment variables are set"""
        missing = [key for key in keys if not os.getenv(key)]
        if missing:
            raise EnvVarError(f"Missing required environment variables: {', '.join(missing)}")


# Application Settings
DEBUG = Config.get_bool('DEBUG', False)
ENVIRONMENT = Config.get_choice('ENVIRONMENT', ['development', 'staging', 'production'], 'production')
SECRET_KEY = Config.get_str('SECRET_KEY', required=DEBUG is False)

# Database
DB_ENGINE = Config.get_str('DB_ENGINE', 'django.db.backends.postgresql')
DB_NAME = Config.get_str('DB_NAME', 'smartlaundry')
DB_USER = Config.get_str('DB_USER', 'postgres')
DB_PASSWORD = Config.get_str('DB_PASSWORD', '')
DB_HOST = Config.get_str('DB_HOST', 'localhost')
DB_PORT = Config.get_int('DB_PORT', 5432)
DB_SSL = Config.get_bool('DB_SSL', False)

# Redis
REDIS_HOST = Config.get_str('REDIS_HOST', '127.0.0.1')
REDIS_PORT = Config.get_int('REDIS_PORT', 6379)
REDIS_DB = Config.get_int('REDIS_DB', 0)
REDIS_URL = Config.get_str('REDIS_URL', f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}')

# Celery
CELERY_BROKER_URL = Config.get_str('CELERY_BROKER_URL', REDIS_URL.replace('/0', '/1'))
CELERY_RESULT_BACKEND = Config.get_str('CELERY_RESULT_BACKEND', REDIS_URL.replace('/0', '/2'))

# Email
EMAIL_BACKEND = Config.get_str('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = Config.get_str('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = Config.get_int('EMAIL_PORT', 587)
EMAIL_USE_TLS = Config.get_bool('EMAIL_USE_TLS', True)
EMAIL_HOST_USER = Config.get_str('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = Config.get_str('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = Config.get_str('DEFAULT_FROM_EMAIL', 'noreply@smartlaundry.com')

# Stripe
STRIPE_SECRET_KEY = Config.get_str('STRIPE_SECRET_KEY', '')
STRIPE_PUBLISHABLE_KEY = Config.get_str('STRIPE_PUBLISHABLE_KEY', '')

# AWS S3
USE_S3 = Config.get_bool('USE_S3', False)
AWS_ACCESS_KEY_ID = Config.get_str('AWS_ACCESS_KEY_ID', '')
AWS_SECRET_ACCESS_KEY = Config.get_str('AWS_SECRET_ACCESS_KEY', '')
AWS_STORAGE_BUCKET_NAME = Config.get_str('AWS_STORAGE_BUCKET_NAME', '')
AWS_S3_REGION_NAME = Config.get_str('AWS_S3_REGION_NAME', 'us-east-1')
AWS_S3_CUSTOM_DOMAIN = Config.get_str('AWS_S3_CUSTOM_DOMAIN', '')

# Security
ALLOWED_HOSTS = Config.get_list('ALLOWED_HOSTS', ['localhost', '127.0.0.1'])
CORS_ALLOWED_ORIGINS = Config.get_list('CORS_ALLOWED_ORIGINS', [])
CSRF_TRUSTED_ORIGINS = Config.get_list('CSRF_TRUSTED_ORIGINS', [])
SECURE_SSL_REDIRECT = Config.get_bool('SECURE_SSL_REDIRECT', ENVIRONMENT == 'production')

# API Rate Limiting
API_RATE_LIMIT_ANON = Config.get_str('API_RATE_LIMIT_ANON', '100/hour')
API_RATE_LIMIT_USER = Config.get_str('API_RATE_LIMIT_USER', '1000/hour')

# WebSocket
WEBSOCKET_TIMEOUT = Config.get_int('WEBSOCKET_TIMEOUT', 300)
WEBSOCKET_MAX_CONNECTIONS = Config.get_int('WEBSOCKET_MAX_CONNECTIONS', 1000)

# Geofencing
GEOFENCE_RADIUS_METERS = Config.get_int('GEOFENCE_RADIUS_METERS', 100)
GEOFENCE_UPDATE_INTERVAL = Config.get_int('GEOFENCE_UPDATE_INTERVAL', 60)

# Analytics
ANALYTICS_RETENTION_DAYS = Config.get_int('ANALYTICS_RETENTION_DAYS', 90)
ANALYTICS_BATCH_SIZE = Config.get_int('ANALYTICS_BATCH_SIZE', 100)

# Push Notifications
EXPO_ACCESS_TOKEN = Config.get_str('EXPO_ACCESS_TOKEN', '')
PUSH_NOTIFICATION_ENABLED = Config.get_bool('PUSH_NOTIFICATION_ENABLED', True)
PUSH_NOTIFICATION_TIMEOUT = Config.get_int('PUSH_NOTIFICATION_TIMEOUT', 30)

# Sentry
SENTRY_DSN = Config.get_str('SENTRY_DSN', '')
SENTRY_ENABLED = bool(SENTRY_DSN)

# Logging
LOG_LEVEL = Config.get_choice('LOG_LEVEL', ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], 'INFO')
LOG_FORMAT = Config.get_choice('LOG_FORMAT', ['json', 'text'], 'text')
LOG_FILE = Config.get_str('LOG_FILE', '/var/log/smartlaundry/django.log')

# Validate critical settings for production
if ENVIRONMENT == 'production':
    Config.validate_required('SECRET_KEY', 'DB_PASSWORD')
    if SECURE_SSL_REDIRECT and not ALLOWED_HOSTS:
        raise EnvVarError("ALLOWED_HOSTS must be configured in production with SSL enabled")


def print_config_status():
    """Print current configuration status (safe for production)"""
    safe_keys = [
        'DEBUG', 'ENVIRONMENT', 'DB_NAME', 'DB_HOST', 'REDIS_HOST',
        'ALLOWED_HOSTS', 'EMAIL_BACKEND', 'LOG_LEVEL'
    ]
    config = {key: globals().get(key) for key in safe_keys if key in globals()}
    return config
