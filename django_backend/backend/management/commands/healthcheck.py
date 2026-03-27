"""
Management command to check system health and database optimization status
Usage: python manage.py healthcheck
"""

from django.core.management.base import BaseCommand
from django.conf import settings
from backend.database_optimization import (
    DatabaseHealthCheck,
    PerformanceMonitor,
    QueryAnalyzer,
    get_optimization_recommendations,
)
from backend.monitoring import HealthCheckMetrics
import json


class Command(BaseCommand):
    help = 'Check system health and performance metrics'

    def add_arguments(self, parser):
        parser.add_argument(
            '--detailed',
            action='store_true',
            help='Show detailed performance analysis',
        )
        parser.add_argument(
            '--json',
            action='store_true',
            help='Output in JSON format',
        )

    def handle(self, *args, **options):
        verbose = options.get('verbose', 1)
        is_json = options.get('json', False)
        detailed = options.get('detailed', False)

        # Collect all health information
        health_report = HealthCheckMetrics.get_health_check()
        db_health = DatabaseHealthCheck.check_connection()
        table_stats = DatabaseHealthCheck.get_table_stats()
        slow_queries = DatabaseHealthCheck.get_slow_queries()
        missing_indexes = DatabaseHealthCheck.get_missing_indexes()
        recommendations = get_optimization_recommendations()

        report = {
            'status': health_report['status'],
            'timestamp': health_report['timestamp'],
            'database': db_health,
            'components': health_report['checks'],
            'tables': table_stats,
            'performance': {
                'slow_queries': slow_queries[:5] if slow_queries else [],
                'missing_indexes': missing_indexes,
            },
            'recommendations': recommendations,
        }

        if is_json:
            self.stdout.write(json.dumps(report, indent=2))
        else:
            self._print_report(report, detailed)

    def _print_report(self, report, detailed=False):
        """Pretty print the health report."""
        status_colors = {
            'healthy': '\033[92m',  # Green
            'degraded': '\033[93m',  # Yellow
            'unhealthy': '\033[91m',  # Red
        }
        reset_color = '\033[0m'

        status = report['status']
        color = status_colors.get(status, '')

        self.stdout.write(f"\n{color}{'='*60}")
        self.stdout.write(f"SmartLaundry System Health Check")
        self.stdout.write(f"{'='*60}{reset_color}\n")

        self.stdout.write(f"Status: {color}{status.upper()}{reset_color}")
        self.stdout.write(f"Timestamp: {report['timestamp']}\n")

        # Component Status
        self.stdout.write(self.style.SUCCESS("Component Status:"))
        for component, health in report['components'].items():
            if 'unhealthy' in str(health).lower():
                color = status_colors['unhealthy']
                symbol = '✗'
            else:
                color = status_colors['healthy']
                symbol = '✓'
            
            self.stdout.write(f"  {symbol} {component}: {color}{health}{reset_color}")

        # Database Status
        self.stdout.write("\n" + self.style.SUCCESS("Database:"))
        db_status = report['database']
        if db_status['status'] == 'healthy':
            self.stdout.write(f"  ✓ Connection: {self.style.SUCCESS('OK')}")
        else:
            self.stdout.write(f"  ✗ Connection: {self.style.ERROR(db_status.get('error', 'Unknown error'))}")

        # Table Statistics
        if report['tables']:
            self.stdout.write("\n" + self.style.SUCCESS("Table Statistics:"))
            total_size = 0
            total_rows = 0
            for table, stats in sorted(report['tables'].items(), key=lambda x: x[1]['row_count'] or 0, reverse=True)[:10]:
                rows = stats['row_count'] or 0
                size = stats['size']
                total_rows += rows
                self.stdout.write(f"  {table:30} {rows:>10,} rows  {size:>12}")
            self.stdout.write(f"  {'TOTAL':30} {total_rows:>10,} rows")

        # Performance Issues
        perf = report['performance']
        if perf['slow_queries']:
            self.stdout.write("\n" + self.style.WARNING("Slow Queries (>0.5s):"))
            for query in perf['slow_queries'][:3]:
                self.stdout.write(f"  ⚠ {query['mean_time']:.4f}s: {query['query'][:70]}")

        if perf['missing_indexes']:
            self.stdout.write("\n" + self.style.WARNING("Tables with High Sequential Scans:"))
            for idx in perf['missing_indexes'][:3]:
                self.stdout.write(f"  ⚠ {idx['table']}: {idx['seq_scans']} seq scans")

        # Recommendations
        if report['recommendations']:
            self.stdout.write("\n" + self.style.SUCCESS("Optimization Recommendations:"))
            for rec in report['recommendations'][:5]:
                self.stdout.write(f"  • {rec}")

        self.stdout.write(f"\n{self.style.SUCCESS('Health check complete!')} \n")
