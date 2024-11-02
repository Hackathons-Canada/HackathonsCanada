import random
from typing import Final, Tuple, List

from django.contrib.auth.models import AbstractUser, UserManager

# Create your models here.
from django.db import models
from django.db.models import DecimalField
from django.utils import timezone
from django_countries.fields import CountryField

from core.tasks import send_new_hackathon_email

__all__ = [
    "Hacker",
    "School",
    "Hackathon",
    "HackathonLocation",
    "Location",
    "Category",
    "NotificationPolicy",
    "EDUCATION_CHOICES",
    "HACKATHON_EDUCATION_CHOICES",
    "ReviewStatus",
]

EDUCATION_CHOICES: Final = [
    (0, "Middle School"),
    (1, "High School"),
    (2, "University/College"),
    (3, "Graduated University/College"),
    (4, "Other"),
]

HACKATHON_EDUCATION_CHOICES: List[Tuple[int, str]] = EDUCATION_CHOICES + [
    (5, "Any/All")
]


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

    def __str__(self):
        return self.name


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
        # constraints = [
        #     models.CheckConstraint(
        #         check=models.Q(weekly=True)&  models.Q(monthly=True),
        #         name="weekly_or_monthly_not_both",
        #     ),
        # ]


class Notifiable(UserManager):
    async def anotify(self):
        async for user in self.iterator():
            send_new_hackathon_email.delay(user)


class Hacker(AbstractUser):
    objects = Notifiable()  # type: ignore
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

    education = models.CharField(
        max_length=255,
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
    saved_categories = models.ManyToManyField(
        "core.Category",
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
        if self.notification_policy_id is None:
            self.notification_policy = NotificationPolicy.objects.create()
        super().save(force_insert, force_update, using, update_fields)


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
    source = models.CharField(
        max_length=3,
        choices=HackathonSource.choices,
        default=HackathonSource.UserSubmitted,
    )
    metadata = models.JSONField(
        blank=True,
        null=True,
        help_text="Metadata about the source of the hackathon",
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


class CuratorRequest(models.Model):
    hackathon = models.ForeignKey(Hackathon, on_delete=models.CASCADE)
    team_name = models.CharField(max_length=255)
    team_description = models.TextField()
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Curator request from {self.team_name} for {self.hackathon}"
