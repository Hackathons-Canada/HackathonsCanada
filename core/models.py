import random

from django.contrib.auth.models import AbstractUser

# Create your models here.
from django.db import models
from django.utils import timezone
from django_countries.fields import CountryField

from core.tasks import send_new_hackathon_email

# from django.contrib.gis.geos import Point


# from location_field.models.spatial import LocationField

EDUCATION_CHOICES = [
    (0, "Middle School"),
    (1, "High School"),
    (2, "University/College"),
    (3, "Graduated University/College"),
    (4, "Other"),
]

HACKATHON_EDUCATION_CHOICES = EDUCATION_CHOICES + [(5, "Any/All")]


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


class NotificationPolicy(models.Model):
    enabled = models.BooleanField(
        default=False, help_text="Enable or disable notifications"
    )
    weekly = models.BooleanField(default=False, help_text="Send weekly notifications")
    monthly = models.BooleanField(default=False, help_text="Send monthly notifications")
    added = models.BooleanField(
        default=False,
        help_text="Send notifications when a new hackathon is added",
    )
    local_only = models.BooleanField(
        default=False,
        help_text="Only send notifications for hackathons in your local area (as defined by radius) - Changes the behavior of all other notification settings",
    )
    only_eligible = models.BooleanField(
        default=True,
        help_text="Only send notifications for hackathons you are eligible for (based on age and education level)",
    )
    # todo: fields abt travel reimbursement?

    radius_type = models.CharField(
        max_length=255,
        choices=[
            ("km", "Kilometers"),
            ("mi", "Miles"),
        ],
        default="km",
        help_text="Unit of radius",
    )
    radius = models.PositiveIntegerField(
        default=150,
        help_text="Radius in which a hackathon must be in to be considered local",
    )

    @property
    def standard_radius(self) -> float | int:
        """
        Get the radius in kilometers
        :return: radius in kilometers
        """
        if self.radius_type == "km":
            return self.radius

        MILES_TO_KM = 1.60934
        return self.radius * MILES_TO_KM

    class Meta:
        verbose_name_plural = "Notification Policies"
        constraints = [
            models.CheckConstraint(
                check=models.Q(weekly=True) ^ models.Q(monthly=True),
                name="weekly_or_monthly_not_both",
            ),
        ]


class Notifiable(models.QuerySet):
    async def anotify(self):
        async for user in self.iterator():
            send_new_hackathon_email.delay(user)


class Hacker(AbstractUser):
    objects = Notifiable.as_manager()
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
    education = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Your current education level e.g. High School, University, etc.",
        choices=EDUCATION_CHOICES,
    )
    saved = models.ManyToManyField(
        "Hackathon",
        related_name="interested_users",
        help_text="Hackathons the user is interested in and wants updates about.",
    )
    saved_categories = models.ManyToManyField(
        "Category",
        related_name="interested_users",
        help_text="Categories the user is interested in and wants updates when new hackathons meeting this critera are created.",
    )
    notification_policy = models.OneToOneField(
        NotificationPolicy,
        on_delete=models.CASCADE,
        related_name="user",
        blank=False,
        null=False,
    )

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        if not self.notification_policy:
            self.notification_policy = NotificationPolicy.objects.create()
        super().save(force_insert, force_update, using, update_fields)


def get_random_color():
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


class Hackathon(MetaDataMixin):
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

    country = CountryField(blank_label="(select country)", blank=True, null=True)
    # location = LocationField(based_fields=['city'], zoom=7, default=Point(1.0, 1.0))

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

    image = models.ImageField(upload_to="hackathon_images")
    notes = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["start_date"]

        constraints = [
            models.CheckConstraint(  # ensure start date is before end date
                check=models.Q(start_date__lt=models.F("end_date")),
                name="start_date_lt_end_date",
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
