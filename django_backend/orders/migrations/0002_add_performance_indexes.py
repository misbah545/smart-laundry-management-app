"""Add performance indexes for orders app."""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_driverlocation_distance_remaining_km_and_more'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['status'], name='order_status_idx'),
        ),
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['customer'], name='order_customer_idx'),
        ),
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['driver'], name='order_driver_idx'),
        ),
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['order_date'], name='order_date_idx'),
        ),
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['customer', 'status'], name='order_customer_status_idx'),
        ),
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['driver', '-order_date'], name='order_driver_recent_idx'),
        ),
    ]
