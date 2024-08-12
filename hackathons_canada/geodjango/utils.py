from django.contrib.gis.geos import Point
from models import Location
from django.contrib.gis.measure import D


def add_location(name, latitude, longitude):
    point = Point(longitude, latitude)
    location = Location(name=name, point=point)
    location.save()
    return location


def find_locations_within_radius(center_latitude, center_longitude, radius_km):
    point = Point(center_longitude, center_latitude)
    locations = Location.objects.filter(point__distance_lte=(point, D(km=radius_km)))
    return locations
