from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('bookings', '0002_booking_payment_amount_booking_payment_status_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='payment_method',
            field=models.CharField(blank=True, max_length=30),
        ),
    ]