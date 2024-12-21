import django_filters
from .models import Hackathon
from django.db.models import Q
from django.utils import timezone


class HackathonFilter(django_filters.FilterSet):
    next_week = django_filters.DateFilter(
        field_name="created_at", method="filter_next_week"
    )
    next_month = django_filters.DateFilter(
        field_name="created_at", method="filter_next_month"
    )
    location_country = django_filters.CharFilter(lookup_expr="iexact")
    location_city = django_filters.CharFilter(lookup_expr="iexact")
    date_range = django_filters.DateFromToRangeFilter(field_name="created_at")

    class Meta:
        model = Hackathon
        fields = ["date_range", "location_country", "location_city"]

    def filter_next_week(self, queryset, name, value):
        start_date = timezone.now().date()
        end_date = start_date + timezone.timedelta(days=7)
        return queryset.filter(created_at__range=[start_date, end_date])

    def filter_next_month(self, queryset, name, value):
        start_date = timezone.now().date()
        end_date = start_date + timezone.timedelta(days=30)
        return queryset.filter(created_at__range=[start_date, end_date])


class LocationFilter(django_filters.FilterSet):
    country = django_filters.CharFilter(lookup_expr="icontains")
    city = django_filters.CharFilter(lookup_expr="iexact")
    proximity = django_filters.NumberFilter(method="filter_by_proximity")

    class Meta:
        model = Hackathon
        fields = ["country", "city"]

    def filter_by_proximity(self, queryset, name, value):
        # Get latitude and longitude from the query parameters
        lat = self.request.GET.get("latitude")
        lon = self.request.GET.get("longitude")
        if lat and lon:
            lat, lon = float(lat), float(lon)
            queryset = queryset.filter(
                Q(
                    latitude__range=(lat - value, lat + value),
                    longitude__range=(lon - value, lon + value),
                )
            )
        return queryset
