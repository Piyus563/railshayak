from django.core.exceptions import ValidationError


def validate_latitude(value):
    if value is not None and not -90 <= value <= 90:
        raise ValidationError('Latitude must be between -90 and 90.')


def validate_longitude(value):
    if value is not None and not -180 <= value <= 180:
        raise ValidationError('Longitude must be between -180 and 180.')


def validate_coordinate_pair(latitude, longitude):
    if (latitude is None) != (longitude is None):
        raise ValidationError('Latitude and longitude must both be provided or both be empty.')
    if latitude is not None:
        validate_latitude(latitude)
        validate_longitude(longitude)
