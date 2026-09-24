from django.db import migrations, models
import stations.validators


class Migration(migrations.Migration):
    dependencies = [('stations', '0001_initial')]

    operations = [
        migrations.AlterField(model_name='station', name='latitude', field=models.DecimalField(decimal_places=6, help_text='Verified latitude (-90 to 90).', max_digits=9, validators=[stations.validators.validate_latitude])),
        migrations.AlterField(model_name='station', name='longitude', field=models.DecimalField(decimal_places=6, help_text='Verified longitude (-180 to 180).', max_digits=9, validators=[stations.validators.validate_longitude])),
        migrations.AlterField(model_name='platform', name='latitude', field=models.DecimalField(blank=True, decimal_places=6, help_text='Verified latitude; leave blank when unknown.', max_digits=9, null=True, validators=[stations.validators.validate_latitude])),
        migrations.AlterField(model_name='platform', name='longitude', field=models.DecimalField(blank=True, decimal_places=6, help_text='Verified longitude; leave blank when unknown.', max_digits=9, null=True, validators=[stations.validators.validate_longitude])),
        migrations.AlterField(model_name='facility', name='facility_type', field=models.CharField(choices=[('WASHROOM', '🚻 Washroom / Restroom'), ('DRINKING_WATER', '💧 Clean Drinking Water'), ('LIFT', '🛗 Passenger Lift / Elevator'), ('ESCALATOR', '🚶 Escalator'), ('FOOD', '🍴 Food Court & Refreshments'), ('WAITING_ROOM', '🪑 AC & General Waiting Room'), ('PARKING', '🚗 Station Parking Area'), ('MEDICAL', '🏥 Emergency Medical Room'), ('HELP_DESK', 'ℹ️ Sahayata / Help Desk'), ('CLOAK_ROOM', '🛅 Cloak Room & Luggage Locker'), ('WHEELCHAIR_POINT', '♿ Wheelchair Pick-up Hub'), ('COOLIE_PICKUP', '🧳 Coolie Pickup Point')], max_length=30)),
        migrations.AlterField(model_name='facility', name='latitude', field=models.DecimalField(blank=True, decimal_places=6, help_text='Verified latitude; leave blank when unknown.', max_digits=9, null=True, validators=[stations.validators.validate_latitude])),
        migrations.AlterField(model_name='facility', name='longitude', field=models.DecimalField(blank=True, decimal_places=6, help_text='Verified longitude; leave blank when unknown.', max_digits=9, null=True, validators=[stations.validators.validate_longitude])),
    ]