"""
Prometheus metrics for monitoring application performance and business metrics.
"""
from prometheus_client import Counter, Gauge, Histogram

# Business metrics
books_created_total = Counter(
    'books_created_total',
    'Total number of books created'
)

books_deleted_total = Counter(
    'books_deleted_total',
    'Total number of books deleted'
)

books_count = Gauge(
    'books_count',
    'Current number of books in the database'
)

# Database operation metrics
db_errors_total = Counter(
    'db_errors_total',
    'Total number of database errors',
    ['operation']
)

db_query_duration = Histogram(
    'db_query_duration_seconds',
    'Time spent on database queries',
    ['operation']
)
