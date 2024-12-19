import math
import operator
import random
from functools import reduce
from typing import Final, Tuple, List

from django.contrib.auth.models import AbstractUser
from core.utils import get_coordinates

# Create your models here.
from django.db import models
from django.db.models import DecimalField
from django.utils import timezone
from django_countries.fields import CountryField


__all__ = [
    "Hacker",
    "School",
    "Hackathon",
    "HackathonLocation",
    "HackathonSource",
    "Location",
    "Category",
    "EmailPreferences",
    "EDUCATION_CHOICES",
    "HACKATHON_EDUCATION_CHOICES",
    "HYBRID_CHOICES",
    "ReviewStatus",
]


EDUCATION_CHOICES: Final = [
    (0, "Middle School"),
    (1, "High School"),
    (2, "University/College"),
    (3, "Graduated University/College"),
    (4, "Other"),
]

FREQUENCY_CHOICES = [
    ("never", "Never"),
    ("weekly", "Weekly Digest"),
    ("monthly", "Monthly Digest"),
    ("instant", "Instant Updates"),
]

HACKATHON_EDUCATION_CHOICES: List[Tuple[int, str]] = EDUCATION_CHOICES + [
    (5, "Any/All")
]


HYBRID_CHOICES = (
    ("I", "In-Person"),
    ("O", "Online"),
    ("H", "Hybrid"),
)


class MetaDataMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        self.updated_at = timezone.now()
        super().save(force_insert, force_update, using, update_fields)


class School(models.Model):
    name = models.CharField(max_length=255)
    added_by = models.ForeignKey(
        "core.Hacker",
        on_delete=models.CASCADE,
        related_name="schools_added",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    public = models.BooleanField(
        default=False,
        help_text="Is the school public (Is displayed on fields)",
        db_index=True,
    )

    def __str__(self):
        return self.name


class EmailPreferences(models.Model):
    user = models.OneToOneField(
        "Hacker", on_delete=models.CASCADE, related_name="email_preferences"
    )
    frequency = models.CharField(
        max_length=10, choices=FREQUENCY_CHOICES, default="weekly"
    )
    last_email_sent = models.DateTimeField(null=True, blank=True)
    radius_km = models.PositiveIntegerField(
        default=150, help_text="Search radius in kilometers"
    )
    categories_of_interest = models.ManyToManyField(
        "core.Category", blank=True, related_name="interested_users"
    )
    min_prize_pool = models.IntegerField(
        null=True, blank=True, help_text="Minimum prize pool to notify about"
    )
    include_virtual = models.BooleanField(default=True)
    include_in_person = models.BooleanField(default=True)
    include_hybrid = models.BooleanField(default=True)
    only_with_travel_reimbursement = models.BooleanField(default=False)

    def is_due_for_email(self):
        if not self.last_email_sent:
            return True

        now = timezone.now()
        time_diff = now - self.last_email_sent

        if self.frequency == "daily":
            return time_diff.days >= 1
        elif self.frequency == "weekly":
            return time_diff.days >= 7
        elif self.frequency == "monthly":
            return time_diff.days >= 30
        return False

    def get_relevant_hackathons(self):
        base_query = Hackathon.objects.filter(
            is_public=True,
            review_status="approved",
            application_deadline__gt=timezone.now(),
        )

        # Location filtering
        if not all([self.include_virtual, self.include_in_person, self.include_hybrid]):
            location_filters = []
            if self.include_virtual:
                location_filters.append(models.Q(hybrid="V"))
            if self.include_in_person:
                location_filters.append(models.Q(hybrid="I"))
            if self.include_hybrid:
                location_filters.append(models.Q(hybrid="H"))
            base_query = base_query.filter(reduce(operator.or_, location_filters))

        # Category filtering
        if self.categories_of_interest.exists():
            base_query = base_query.filter(
                categories__in=self.categories_of_interest.all()
            )

        # Prize pool filtering
        if self.min_prize_pool:
            base_query = base_query.filter(
                numerical_prize_pool__gte=self.min_prize_pool
            )

        # Travel reimbursement filtering
        if self.only_with_travel_reimbursement:
            base_query = base_query.exclude(reimbursements__isnull=True).exclude(
                reimbursements=""
            )

        # Location-based filtering for in-person events
        if self.user.city and self.user.country:
            in_person_hackathons = base_query.filter(
                models.Q(hybrid="I") | models.Q(hybrid="H"), location__isnull=False
            )

            nearby_hackathons = [
                h
                for h in in_person_hackathons
                if self._calculate_distance(h.location) <= self.radius_km
            ]

            virtual_hackathons = base_query.filter(hybrid="V")
            return list(virtual_hackathons) + nearby_hackathons

        return base_query

    def _calculate_distance(self, hackathon_location):
        """Calculate distance between user and hackathon location using Haversine formula"""
        # TODO: redo in geodjango
        if not (self.user.city and self.user.country and hackathon_location):
            return float("inf")

        user_lat, user_lon = get_coordinates(self.user.city, self.user.country)
        hack_lat, hack_lon = get_coordinates(
            hackathon_location.city, hackathon_location.country
        )

        R = 6371  # Earth's radius in km

        lat1, lon1 = math.radians(user_lat), math.radians(user_lon)
        lat2, lon2 = math.radians(hack_lat), math.radians(hack_lon)

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c


class Hacker(AbstractUser):
    country = CountryField(
        blank_label="(select country)",
        blank=True,
        null=True,
        help_text="Country you live in",
    )
    city = models.CharField(
        max_length=255, blank=True, null=True, help_text="City you live in"
    )
    school = models.CharField(
        max_length=512,
        blank=True,
        null=True,
        help_text="Name of your school or university",
    )
    birthday = models.DateField(blank=True, null=True)
    personal_website = models.CharField(null=True, blank=True, max_length=255)

    education = models.SmallIntegerField(
        blank=True,
        null=True,
        help_text="Your current education level e.g. High School, University, etc.",
        choices=EDUCATION_CHOICES,
    )
    saved = models.ManyToManyField(
        "core.Hackathon",
        related_name="interested_users",
        help_text="Hackathons the user is interested in and wants updates about.",
    )

    def __str__(self):
        return f"Hacker(username={self.username}, email={self.email}, first_name={self.first_name}, last_name={self.last_name})"


def get_random_color() -> str:
    # generate a random color in hex format
    return "#" + "%06x" % random.randint(0, 0xFFFFFF)


class Category(models.Model):
    name = models.CharField(max_length=255)
    color = models.CharField(
        max_length=7,
        default=get_random_color,
        help_text="Color of the category in hex format e.g. #FF0000",
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"


class HackathonSource(models.TextChoices):
    Scraped = "SCR", "Scrapped"
    UserSubmitted = "USR", "User Submitted"
    Partner = "PRT", "Partner"


class HackthonsManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_public=True)

    def admin(self):
        return super().get_queryset()

    def unapproved(self):
        return (
            super().get_queryset().filter(is_public=False)
        )  # todo add a "approval_status" field

    def online(self):
        return self.filter(country="Onl")

    def in_person(self):
        return self.exclude(country="Onl")

    def local(self, user: Hacker): ...  # todo: implement this

    def eligible(self, user: Hacker):
        # todo rewrite
        return self.filter(
            application_deadline__gte=timezone.now(),
            # min_age__lte=user.age,
            maximum_education_level__gte=user.education,
        )


class Location(models.Model):
    """
    TODO:
     - remove this model and replace with a proper implementation of GeoDjango for location
     - Add a proper Widget for the location field in the Hackathon model (look into django-map-widgets)

    """

    latitude = DecimalField(max_digits=22, decimal_places=16)
    longitude = DecimalField(max_digits=22, decimal_places=16)


class HackathonLocation(models.Model):
    name = models.CharField(
        max_length=255,
        help_text="Where the hackathon is located (e.g. University of Toronto)",
    )
    country = CountryField(blank_label="(select country)")
    location = models.OneToOneField(
        Location, on_delete=models.RESTRICT, related_name="location"
    )


class ReviewStatus(models.TextChoices):
    Approved = "approved", "Approved"
    Rejected = "rejected", "Rejected"
    Pending = "pending", "Pending"
    RequestingChanges = "requesting_changes", "Requesting Changes"


class Hackathon(MetaDataMixin):
    objects = HackthonsManager()

    # This ID is to make it easier to identify hackathons when scraping in order to avoid duplicates
    # id = models.GeneratedField(
    #         expression=F("name") + F("date"),
    #         output_field=models.IntegerField(),
    #         db_persist=True,
    #         primary_key=True, editable=False, unique=True)

    source = models.CharField(
        max_length=3,
        choices=HackathonSource.choices,
        default=HackathonSource.UserSubmitted,
    )

    metadata = models.JSONField(
        blank=True, null=True, help_text="Metadata about the source of the hackathon"
    )

    is_public = models.BooleanField(
        help_text="Is the hackathon visible to all users", default=False
    )
    review_status = models.CharField(
        max_length=255,
        blank=True,
        null=False,
        default=ReviewStatus.Pending,
        help_text="Status of the review process",
        choices=ReviewStatus.choices,
    )

    categories = models.ManyToManyField(Category, related_name="hackathons")
    created_by = models.ForeignKey(
        Hacker,
        on_delete=models.SET_NULL,
        null=True,
        related_name="hackathons",
        blank=False,
    )
    curators = models.ManyToManyField(Hacker, related_name="curated_hackathons")

    short_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Short name for the hackathon e.g. HTV",
    )
    name = models.CharField(
        max_length=255, help_text="Full name of the hackathon e.g. Hack the Valley"
    )
    website = models.URLField()

    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)

    application_start = models.DateTimeField(blank=True, null=True)
    application_deadline = models.DateTimeField(blank=True, null=True)

    reimbursements = models.CharField(max_length=255, blank=True, null=True)

    location = models.ForeignKey(
        HackathonLocation,
        on_delete=models.RESTRICT,
        related_name="hackathons",
        blank=True,
        null=True,
    )

    min_age = models.SmallIntegerField(
        blank=True,
        null=True,
        default=0,
        help_text="Minimum age to participate, set to 0 if there is no minimum age and don't set if unknown",
    )
    minimum_education_level = models.SmallIntegerField(
        choices=HACKATHON_EDUCATION_CHOICES,
        blank=True,
        null=True,
        help_text="Minimum education level required to participate, set to Any/All if there is no minimum education level and don't set if unknown",
    )
    maximum_education_level = models.SmallIntegerField(
        choices=HACKATHON_EDUCATION_CHOICES,
        blank=True,
        null=True,
        help_text="Maximum education level required to participate, set to Any/All if there is no maximum education level and don't set if unknown",
    )

    numerical_prize_pool = models.IntegerField(
        blank=True, null=True, default=0
    )  # if blank, then Unknown
    prize_pool_items = models.TextField(
        blank=True, null=True, help_text="List of items in the prize pool"
    )

    fg_image = models.ImageField(upload_to="hackathon_images", null=True, blank=True)
    bg_image = models.ImageField(upload_to="hackathon_images", null=True, blank=True)
    notes = models.TextField(blank=True, default="")

    hybrid = models.CharField(
        max_length=1,
        choices=HYBRID_CHOICES,
        default="I",
        help_text="Location of the hackathon, I for in-person, V for virtual, H for hybrid",
    )

    # Boolean fields for whether the hackathon is specific to certain groups
    is_web3 = models.BooleanField(default=False)  # Web 3 hackathons
    is_diversity = models.BooleanField(
        default=False
    )  # Diversity hackathons for specific marginalized groups
    is_restricted = models.BooleanField(
        default=False
    )  # Hackathons with restricrted enrollment (ex. only students of some university)
    is_nonenglish = models.BooleanField(
        default=False
    )  # Hackathons which are not in English
    is_over18 = models.BooleanField(
        default=False
    )  # Hackathons which are only for people over 18

    freeze_data = models.BooleanField(
        default=False,
        help_text="Set to True to not update any details using scraped data. Use if you get accurate details directly from the hackathon organizers.",
    )

    custom_info = models.JSONField(
        default=dict, null=True, blank=True
    )  # Anything else that we might want to add in a structured format

    class Meta:
        ordering = ["start_date"]

        constraints = [
            models.CheckConstraint(  # ensure start date is before end date
                check=models.Q(start_date__lte=models.F("end_date")),
                name="start_date_lte_end_date",
            ),
            models.CheckConstraint(  # ensure application start is before deadline
                check=models.Q(application_start__lt=models.F("application_deadline")),
                name="application_start_lt_application_deadline",
            ),
            models.CheckConstraint(  # ensure application deadline is before start date
                check=models.Q(application_deadline__lt=models.F("start_date")),
                name="application_deadline_lt_start_date",
            ),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.start_date and timezone.is_naive(self.start_date):
            self.start_date = timezone.make_aware(self.start_date)
        if self.end_date and timezone.is_naive(self.end_date):
            self.end_date = timezone.make_aware(self.end_date)

        super().save(*args, **kwargs)


class CuratorRequest(models.Model):
    hackathon = models.ForeignKey(Hackathon, on_delete=models.CASCADE)
    team_name = models.CharField(max_length=255)
    team_description = models.TextField()
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Curator request from {self.team_name} for {self.hackathon}"
