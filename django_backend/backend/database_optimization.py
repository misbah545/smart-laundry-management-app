"""
Database Optimization Module
Provides utilities for analyzing queries, monitoring performance, and optimizations.
"""

from django.db import connection, reset_queries
from django.conf import settings
from django.utils.timezone import now
import time
import logging

logger = logging.getLogger(__name__)


class QueryAnalyzer:
    """Analyze database queries for performance bottlenecks."""

    def __init__(self):
        self.queries = []
        self.slow_threshold = 0.5  # seconds

    def enable_logging(self):
        """Enable SQL query logging."""
        if settings.DEBUG:
            reset_queries()

    def analyze_queries(self, display=True):
        """
        Analyze executed queries and identify slow ones.
        
        Returns:
            dict: Analysis results with statistics
        """
        if not settings.DEBUG:
            logger.warning("Query analysis only available in DEBUG mode")
            return {}

        from django.db import connection
        queries = connection.queries
        
        if not queries:
            return {"total": 0, "slow_queries": [], "stats": {}}

        analysis = {
            "total": len(queries),
            "slow_queries": [],
            "stats": {
                "total_time": 0,
                "avg_time": 0,
                "min_time": float('inf'),
                "max_time": 0,
            }
        }

        for query in queries:
            time_taken = float(query.get('time', 0))
            sql = query.get('sql', '')
            
            analysis["stats"]["total_time"] += time_taken
            analysis["stats"]["min_time"] = min(analysis["stats"]["min_time"], time_taken)
            analysis["stats"]["max_time"] = max(analysis["stats"]["max_time"], time_taken)

            if time_taken > self.slow_threshold:
                analysis["slow_queries"].append({
                    "sql": sql[:200] + "..." if len(sql) > 200 else sql,
                    "time": round(time_taken, 4),
                })

        if analysis["total"] > 0:
            analysis["stats"]["avg_time"] = round(
                analysis["stats"]["total_time"] / analysis["total"], 4
            )

        if analysis["stats"]["min_time"] == float('inf'):
            analysis["stats"]["min_time"] = 0

        if display and analysis["slow_queries"]:
            logger.warning(f"Found {len(analysis['slow_queries'])} slow queries:")
            for q in analysis["slow_queries"]:
                logger.warning(f"  {q['time']}s: {q['sql']}")

        return analysis


class DatabaseHealthCheck:
    """Monitor database health and performance metrics."""

    @staticmethod
    def check_connection():
        """Check database connection status."""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                return {"status": "healthy", "error": None}
        except Exception as e:
            logger.error(f"Database connection error: {str(e)}")
            return {"status": "unhealthy", "error": str(e)}

    @staticmethod
    def get_table_stats():
        """Get table statistics (row counts, sizes)."""
        stats = {}
        
        try:
            with connection.cursor() as cursor:
                # PostgreSQL specific query
                if connection.vendor == 'postgresql':
                    cursor.execute("""
                        SELECT 
                            schemaname,
                            tablename,
                            pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
                            n_live_tup AS row_count
                        FROM pg_stat_user_tables
                        ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
                    """)
                    
                    for row in cursor.fetchall():
                        stats[row[1]] = {
                            "size": row[2],
                            "row_count": row[3],
                        }
        except Exception as e:
            logger.error(f"Error getting table stats: {str(e)}")

        return stats

    @staticmethod
    def get_missing_indexes():
        """Identify potentially missing indexes on frequently queried columns."""
        missing = []
        
        try:
            with connection.cursor() as cursor:
                if connection.vendor == 'postgresql':
                    # Find tables with many sequential scans
                    cursor.execute("""
                        SELECT 
                            schemaname,
                            tablename,
                            seq_scan,
                            seq_tup_read,
                            idx_scan
                        FROM pg_stat_user_tables
                        WHERE seq_scan > 1000
                        AND seq_tup_read > 100000
                        ORDER BY seq_scan DESC
                        LIMIT 10
                    """)
                    
                    for row in cursor.fetchall():
                        missing.append({
                            "table": row[1],
                            "seq_scans": row[2],
                            "tuples_read": row[3],
                            "index_scans": row[4],
                            "recommendation": "Consider adding index on frequently filtered columns"
                        })
        except Exception as e:
            logger.error(f"Error analyzing indexes: {str(e)}")

        return missing

    @staticmethod
    def get_slow_queries():
        """Get recently slow queries from pg_stat_statements (PostgreSQL)."""
        queries = []
        
        try:
            with connection.cursor() as cursor:
                if connection.vendor == 'postgresql':
                    cursor.execute("""
                        SELECT 
                            query,
                            calls,
                            total_time,
                            mean_time,
                            max_time
                        FROM pg_stat_statements
                        ORDER BY mean_time DESC
                        LIMIT 10
                    """)
                    
                    for row in cursor.fetchall():
                        queries.append({
                            "query": row[0][:100] + "..." if len(row[0]) > 100 else row[0],
                            "calls": row[1],
                            "total_time": round(row[2], 2),
                            "mean_time": round(row[3], 4),
                            "max_time": round(row[4], 2),
                        })
        except Exception as e:
            logger.error(f"Error getting slow queries: {str(e)}")

        return queries


class CacheOptimizer:
    """Manage and optimize caching strategies."""

    @staticmethod
    def get_cache_stats():
        """Get cache statistics from Django cache framework."""
        from django.core.cache import cache
        
        stats = {
            "backend": str(cache.__class__),
            "available": True,
        }
        
        try:
            # Try to get backend-specific stats
            if hasattr(cache, 'get_stats'):
                stats["details"] = cache.get_stats()
            else:
                stats["details"] = "Stats not available for this backend"
        except Exception as e:
            stats["available"] = False
            stats["error"] = str(e)

        return stats

    @staticmethod
    def clear_expired_cache():
        """Clear expired cache entries."""
        from django.core.cache import cache
        
        try:
            cache.clear()
            return {"success": True, "message": "Cache cleared"}
        except Exception as e:
            logger.error(f"Error clearing cache: {str(e)}")
            return {"success": False, "message": str(e)}


class PerformanceMonitor:
    """Monitor overall application performance metrics."""

    @staticmethod
    def get_performance_report():
        """Generate comprehensive performance report."""
        from django.core.cache import cache
        
        report = {
            "timestamp": now().isoformat(),
            "database": DatabaseHealthCheck.check_connection(),
            "table_stats": DatabaseHealthCheck.get_table_stats(),
            "missing_indexes": DatabaseHealthCheck.get_missing_indexes(),
            "slow_queries": DatabaseHealthCheck.get_slow_queries(),
            "cache": CacheOptimizer.get_cache_stats(),
        }

        return report

    @staticmethod
    def check_query_performance(view_func=None):
        """Decorator to measure query count and time in views."""
        def decorator(func):
            def wrapper(*args, **kwargs):
                if settings.DEBUG:
                    reset_queries()
                    start_time = time.time()

                result = func(*args, **kwargs)

                if settings.DEBUG:
                    elapsed = time.time() - start_time
                    query_count = len(connection.queries)
                    
                    if query_count > 10 or elapsed > 0.5:
                        logger.warning(
                            f"View {func.__name__} took {elapsed:.3f}s "
                            f"with {query_count} queries"
                        )

                return result
            return wrapper
        return decorator


# Recommended indexes based on common query patterns
RECOMMENDED_INDEXES = {
    "orders_order": [
        "status",  # Frequently filtered
        "customer_id",  # Foreign key
        "driver_id",  # Foreign key
        "order_date",  # Range queries
        ("customer_id", "status"),  # Composite index
        ("driver_id", "-order_date"),  # Composite index with DESC
    ],
    "messaging_message": [
        "sender_id",  # Foreign key
        "recipient_id",  # Foreign key
        "order_id",  # Foreign key
        ("sender_id", "recipient_id", "-timestamp"),  # Conversation queries
    ],
    "messaging_chatroom": [
        "order_id",  # Foreign key
        ("updated_at",),  # Sorting for list views
    ],
    "tracking_tracking": [
        "driver_id",  # Foreign key
        "order_id",  # Foreign key
        ("-timestamp",),  # Recent tracking data
    ],
    "payments_payment": [
        "order_id",  # Foreign key
        "status",  # Frequently filtered
        ("status", "-created_at"),  # Recent payments by status
    ],
    "feedback_feedback": [
        "order_id",  # Foreign key
        "rating",  # Frequently filtered
        ("rating", "-created_at"),  # Trending analysis
    ],
    "complaints_complaint": [
        "order_id",  # Foreign key
        "status",  # Frequently filtered
        ("status", "-created_at"),  # Recent complaints
    ],
}


def get_optimization_recommendations():
    """
    Generate database optimization recommendations based on current state.
    
    Returns:
        list: List of actionable recommendations
    """
    recommendations = []
    
    monitor = PerformanceMonitor()
    report = monitor.get_performance_report()
    
    # Check for slow queries
    if report["slow_queries"]:
        recommendations.append(
            "✓ Slow queries detected. Consider adding indexes on frequently filtered columns: "
            + ", ".join([q["query"] for q in report["slow_queries"][:3]])
        )
    
    # Check for missing indexes
    if report["missing_indexes"]:
        recommendations.append(
            f"✓ {len(report['missing_indexes'])} tables have high sequential scans. "
            "These may benefit from indexes on frequently filtered columns."
        )
    
    # Check table sizes
    large_tables = {
        k: v for k, v in report["table_stats"].items()
        if v["row_count"] and v["row_count"] > 100000
    }
    if large_tables:
        recommendations.append(
            f"✓ Large tables detected: {list(large_tables.keys())}. "
            "Consider partitioning or archiving historical data."
        )
    
    # Cache recommendations
    if report["cache"]["available"]:
        recommendations.append(
            "✓ Caching is enabled. Ensure cache TTL is appropriate for your use case."
        )
    else:
        recommendations.append(
            "⚠ Cache not properly configured. Enable caching to improve performance."
        )
    
    return recommendations


if __name__ == "__main__":
    print("Database Optimization Report")
    print("=" * 50)
    
    monitor = PerformanceMonitor()
    report = monitor.get_performance_report()
    
    print(f"\nDatabase Status: {report['database']['status']}")
    print(f"\nTable Statistics:")
    for table, stats in report['table_stats'].items():
        print(f"  {table}: {stats['row_count']} rows, {stats['size']}")
    
    print(f"\nSlow Queries (threshold > 0.5s):")
    if report['slow_queries']:
        for q in report['slow_queries']:
            print(f"  {q['mean_time']}s: {q['query']}")
    else:
        print("  None found")
    
    print(f"\nMissing Indexes (potential bottlenecks):")
    if report['missing_indexes']:
        for idx in report['missing_indexes']:
            print(f"  {idx['table']}: {idx['recommendation']}")
    else:
        print("  None identified")
    
    print(f"\nOptimization Recommendations:")
    for rec in get_optimization_recommendations():
        print(f"  {rec}")
