"""
Monitoring and Observability Configuration
Integrates Sentry and Datadog for error tracking and performance monitoring.
"""

import os
import logging

# ========== SENTRY CONFIGURATION ==========

def init_sentry(app_name='SmartLaundry', environment='production'):
    """
    Initialize Sentry for error tracking and monitoring.
    
    Environment Variables:
        SENTRY_DSN: Sentry project DSN
        SENTRY_ENVIRONMENT: 'production', 'staging', 'development'
        SENTRY_TRACES_SAMPLE_RATE: Tracing sample rate (0.0-1.0)
        SENTRY_PROFILES_SAMPLE_RATE: Profiling sample rate (0.0-1.0)
    
    Usage in settings.py:
        from backend.monitoring import init_sentry
        init_sentry(environment=ENVIRONMENT)
    """
    try:
        import sentry_sdk
        from sentry_sdk.integrations.django import DjangoIntegration
        from sentry_sdk.integrations.celery import CeleryIntegration
        from sentry_sdk.integrations.redis import RedisIntegration
        from sentry_sdk.integrations.logging import LoggingIntegration
    except ImportError:
        logging.warning("sentry_sdk not installed. Install with: pip install sentry-sdk")
        return False

    sentry_dsn = os.environ.get('SENTRY_DSN')
    if not sentry_dsn:
        logging.debug("SENTRY_DSN not set. Sentry disabled.")
        return False

    traces_sample_rate = float(os.environ.get('SENTRY_TRACES_SAMPLE_RATE', '0.1'))
    profiles_sample_rate = float(os.environ.get('SENTRY_PROFILES_SAMPLE_RATE', '0.1'))

    sentry_sdk.init(
        dsn=sentry_dsn,
        integrations=[
            DjangoIntegration(
                transaction_style='function_name',
                signals_spans=True,
                signals_glossary=True,
            ),
            CeleryIntegration(
                monitor_beat_tasks=True,
                transaction_style='function_name',
            ),
            RedisIntegration(),
            LoggingIntegration(
                level=logging.INFO,  # Capture info and above as breadcrumbs
                event_level=logging.ERROR,  # Send errors as events
            ),
        ],
        environment=environment,
        traces_sample_rate=traces_sample_rate,
        profiles_sample_rate=profiles_sample_rate,
        
        # Error filtering
        before_send=lambda event, hint: event,  # Customize filtering here
        
        # Performance tuning
        max_breadcrumbs=50,
        attach_stacktrace=True,
        include_source_context=True,
        
        # Release tracking
        release=os.environ.get('APP_VERSION', 'unknown'),
    )

    logging.info(f"Sentry initialized for {app_name} ({environment})")
    return True


SENTRY_CONFIG = {
    'enabled': bool(os.environ.get('SENTRY_DSN')),
    'dsn': os.environ.get('SENTRY_DSN'),
    'environment': os.environ.get('SENTRY_ENVIRONMENT', 'production'),
    'traces_sample_rate': float(os.environ.get('SENTRY_TRACES_SAMPLE_RATE', '0.1')),
    'profiles_sample_rate': float(os.environ.get('SENTRY_PROFILES_SAMPLE_RATE', '0.1')),
}


# ========== DATADOG CONFIGURATION ==========

def init_datadog(service_name='smartlaundry', environment='production'):
    """
    Initialize Datadog APM and Logging.
    
    Environment Variables:
        DD_API_KEY: Datadog API key
        DD_APP_KEY: Datadog application key
        DD_SITE: Datadog site (datadoghq.com, datadoghq.eu)
        DD_AGENT_HOST: Datadog agent hostname (default: localhost)
        DD_AGENT_PORT: Datadog agent port (default: 8126)
        DD_TRACE_SAMPLING_RULES: Sampling rules JSON
        DD_PROFILING_ENABLED: Enable profiling (true/false)
        DD_SERVICE_NAME: Service name for metrics
    
    Usage in settings.py:
        from backend.monitoring import init_datadog
        init_datadog(service_name='smartlaundry', environment=ENVIRONMENT)
    """
    try:
        from ddtrace import initialize, config
        from ddtrace.profiling import profiler
    except ImportError:
        logging.warning("ddtrace not installed. Install with: pip install ddtrace")
        return False

    api_key = os.environ.get('DD_API_KEY')
    if not api_key:
        logging.debug("DD_API_KEY not set. Datadog disabled.")
        return False

    agent_host = os.environ.get('DD_AGENT_HOST', 'localhost')
    agent_port = int(os.environ.get('DD_AGENT_PORT', '8126'))
    site = os.environ.get('DD_SITE', 'datadoghq.com')

    # Initialize APM
    initialize(
        hostname=agent_host,
        port=agent_port,
        service=service_name,
        env=environment,
        version=os.environ.get('APP_VERSION', 'unknown'),
    )

    # Configure integrations
    config.django.trace_request_headers = True
    config.redis.trace_on_connect = True
    config.psycopg.trace_on_connect = True
    config.celery.enabled = True
    config.http_server_middleware.enabled = True

    # Profiling
    if os.environ.get('DD_PROFILING_ENABLED', 'true').lower() == 'true':
        profiler.start(
            service=service_name,
            env=environment,
            api_key=api_key,
            api_base_url=f'https://api.{site}',
            enabled=True,
        )
        logging.info("Datadog profiler enabled")

    logging.info(f"Datadog APM initialized for {service_name} ({environment})")
    return True


DATADOG_CONFIG = {
    'enabled': bool(os.environ.get('DD_API_KEY')),
    'api_key': os.environ.get('DD_API_KEY'),
    'app_key': os.environ.get('DD_APP_KEY'),
    'site': os.environ.get('DD_SITE', 'datadoghq.com'),
    'agent_host': os.environ.get('DD_AGENT_HOST', 'localhost'),
    'agent_port': int(os.environ.get('DD_AGENT_PORT', '8126')),
    'service_name': os.environ.get('DD_SERVICE_NAME', 'smartlaundry'),
    'environment': os.environ.get('ENVIRONMENT', 'production'),
    'profiling_enabled': os.environ.get('DD_PROFILING_ENABLED', 'true').lower() == 'true',
}


# ========== LOGGING CONFIGURATION FOR MONITORING ==========

MONITORING_HANDLERS = {
    'file': {
        'level': 'INFO',
        'class': 'logging.handlers.RotatingFileHandler',
        'filename': os.environ.get('LOG_DIR', '/var/log/smartlaundry') + '/monitoring.log',
        'maxBytes': 104857600,  # 100 MB
        'backupCount': 10,
        'formatter': 'verbose',
    },
    'console': {
        'level': 'INFO',
        'class': 'logging.StreamHandler',
        'formatter': 'simple',
    },
}

MONITORING_LOGGERS = {
    'monitoring': {
        'handlers': ['file', 'console'],
        'level': os.environ.get('LOG_LEVEL', 'INFO'),
        'propagate': False,
    },
    'database': {
        'handlers': ['file'],
        'level': 'WARNING',  # Log slow queries
        'propagate': False,
    },
    'api': {
        'handlers': ['file', 'console'],
        'level': 'INFO',
        'propagate': False,
    },
}


# ========== PERFORMANCE MONITORING UTILITIES ==========

class MonitoringMetrics:
    """Collect and report application metrics."""

    @staticmethod
    def record_metric(name, value, tags=None):
        """
        Record a custom metric.
        
        Args:
            name (str): Metric name (e.g., 'orders.created')
            value (float): Metric value
            tags (dict): Optional tags for the metric
        """
        try:
            from ddtrace import statsd
            if statsd:
                metric_tags = tags or {}
                statsd.gauge(name, value, tags=[f"{k}:{v}" for k, v in metric_tags.items()])
        except ImportError:
            pass

        # Also log for Sentry
        logging.info(f"Metric: {name}={value}", extra={'tags': tags or {}})

    @staticmethod
    def record_timing(name, duration_ms, tags=None):
        """
        Record operation timing.
        
        Args:
            name (str): Operation name
            duration_ms (float): Duration in milliseconds
            tags (dict): Optional tags
        """
        try:
            from ddtrace import statsd
            if statsd:
                metric_tags = tags or {}
                statsd.timing(name, duration_ms, tags=[f"{k}:{v}" for k, v in metric_tags.items()])
        except ImportError:
            pass

    @staticmethod
    def record_exception(exception, context=None):
        """
        Record an exception with context.
        
        Args:
            exception (Exception): The exception to record
            context (dict): Additional context information
        """
        import sentry_sdk
        
        with sentry_sdk.push_scope() as scope:
            if context:
                for key, value in context.items():
                    scope.set_context(key, value)
            sentry_sdk.capture_exception(exception)


class HealthCheckMetrics:
    """Health check metrics for monitoring."""

    @staticmethod
    def get_health_check():
        """
        Get overall system health status.
        
        Returns:
            dict: Health status for all components
        """
        from django.db import connection
        from django.core.cache import cache
        
        health = {
            'status': 'healthy',
            'timestamp': __import__('django.utils.timezone', fromlist=['now']).now().isoformat(),
            'checks': {}
        }

        # Database check
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            health['checks']['database'] = 'healthy'
        except Exception as e:
            health['checks']['database'] = f'unhealthy: {str(e)}'
            health['status'] = 'degraded'

        # Cache check
        try:
            cache.set('health_check', 'ok', 10)
            if cache.get('health_check') == 'ok':
                health['checks']['cache'] = 'healthy'
            else:
                health['checks']['cache'] = 'unhealthy: cache not persisting'
                health['status'] = 'degraded'
        except Exception as e:
            health['checks']['cache'] = f'unhealthy: {str(e)}'
            health['status'] = 'degraded'

        return health

    @staticmethod
    def report_health_check():
        """Report health check to monitoring systems."""
        health = HealthCheckMetrics.get_health_check()
        
        # Report to Datadog
        try:
            MonitoringMetrics.record_metric(
                'system.health',
                1 if health['status'] == 'healthy' else 0,
                {'status': health['status']}
            )
        except Exception as e:
            logging.error(f"Failed to report health check: {str(e)}")

        return health


# ========== MONITORING MIDDLEWARE ==========

class MonitoringMiddleware:
    """Middleware for tracking request/response metrics."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        import time
        start_time = time.time()

        response = self.get_response(request)

        duration_ms = (time.time() - start_time) * 1000
        
        # Record metrics
        try:
            MonitoringMetrics.record_timing(
                'http.request_duration',
                duration_ms,
                {
                    'method': request.method,
                    'path': request.path,
                    'status': response.status_code,
                }
            )
        except Exception as e:
            logging.debug(f"Failed to record request metric: {str(e)}")

        return response


# ========== ENVIRONMENT VARIABLES DOCUMENTATION ==========

MONITORING_ENV_VARS = """
SENTRY CONFIGURATION:
  SENTRY_DSN                    - Sentry project DSN URL
  SENTRY_ENVIRONMENT           - Environment (production/staging/development)
  SENTRY_TRACES_SAMPLE_RATE    - Tracing sample rate 0.0-1.0 (default: 0.1)
  SENTRY_PROFILES_SAMPLE_RATE  - Profiling sample rate 0.0-1.0 (default: 0.1)

DATADOG CONFIGURATION:
  DD_API_KEY                    - Datadog API key
  DD_APP_KEY                    - Datadog application key
  DD_SITE                       - Datadog site (datadoghq.com or datadoghq.eu)
  DD_AGENT_HOST                 - Datadog agent hostname (default: localhost)
  DD_AGENT_PORT                 - Datadog agent port (default: 8126)
  DD_SERVICE_NAME               - Service name (default: smartlaundry)
  DD_PROFILING_ENABLED          - Enable profiling (true/false, default: true)
  DD_TRACE_SAMPLING_RULES       - Sampling rules JSON

GENERAL MONITORING:
  LOG_LEVEL                     - Logging level (default: INFO)
  LOG_DIR                       - Log directory (default: /var/log/smartlaundry)
  APP_VERSION                   - Application version for tracking
"""
