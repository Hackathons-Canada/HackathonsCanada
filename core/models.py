import random
from typing import Final, Tuple, List
from django.contrib.auth.models import AbstractUser, UserManager
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import (
    DecimalField,
    BooleanField,
    Exists,
    Subquery,
    OuterRef,
    Value,
    When,
    Case,
)
from django.db.models.fields import IntegerField
from django.utils import timezone

# from django.core.exceptions import ValidationError
from django_countries.fields import CountryField


__all__ = [
    "Hacker",
    "School",
    "Hackathon",
    "HackathonLocation",
    "HackathonSource",
    "Location",
    "Category",
    "NotificationPolicy",
    "EDUCATION_CHOICES",
    "HACKATHON_EDUCATION_CHOICES",
    "HYBRID_CHOICES",
    "Vote",
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


HYBRID_CHOICES = (
    ("I", "In-Person"),
    ("O", "Online"),
    ("H", "Hybrid"),
)


SCRAPE_SOURCES = (
    ("mlh", "MLH"),
    ("dev", "Devpost"),
    ("eth", "ETHGlobal"),
    ("hcl", "Hack Club"),
    ("na", "Not Applicable"),
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
            pass
            """
            At the moment, we cannot call `core.tasks.send_hackathon_emails.delay()`
            as its parameter is `frequency` which is a string
            that can either be the values "monthly" or "weekly".
            
            Originally, the email-sending task/function
            would iterate through each `user` as its argument,
            and it is no longer dependent on `user` now.
            """


class Hacker(AbstractUser):
    objects = Notifiable()
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

    @classmethod
    def annotate_vote_status(cls, queryset, user):
        """
        Annotates the queryset with user's vote status using a single efficient query.
        Returns:
         - 1 for upvote
         - -1 for downvote
         - 0 for no vote
        """
        if not user.is_authenticated:
            return queryset.annotate(
                user_vote_status=Value(0, output_field=IntegerField())
            )

        return queryset.annotate(
            user_vote_status=Case(
                When(votes__hacker=user, votes__is_upvote=True, then=Value(1)),
                When(votes__hacker=user, votes__is_upvote=False, then=Value(-1)),
                default=Value(0),
                output_field=IntegerField(),
            )
        )

    def __str__(self):
        return f"Hacker(username={self.username}, email={self.email}, first_name={self.first_name}, last_name={self.last_name})"

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
    Scraped = "SCR", "Scraped"
    UserSubmitted = "USR", "User Submitted"
    Partner = "PRT", "Partner"


class HackathonsManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_public=True)

    def with_user_data(self, user):
        """
        Annotate hackathons with user-specific data efficiently.
        """
        if not user.is_authenticated:
            return self
        return self.annotate(
            user_saved=Exists(Hacker.objects.filter(saved=OuterRef("pk"), id=user.id)),
            vote_state=Subquery(
                Vote.objects.filter(hackathon=OuterRef("pk"), hacker=user.id).values(
                    "is_upvote"
                )[:1]
            ),
        )

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

    # def eligible(self, user: Hacker):
    #     # todo rewrite
    #     return self.filter(
    #         application_deadline__gte=timezone.now(),
    #         # min_age__lte=user.age,
    #         maximum_education_level__gte=user.education,
    #     )


class Location(models.Model):
    """
    TODO:
     - remove this model and replace with a proper implementation of GeoDjango for location
     - Add a proper Widget for the location field in the Hackathon model (look into django-map-widgets)

    """

    latitude = DecimalField(max_digits=22, decimal_places=16, blank=True, null=True)
    longitude = DecimalField(max_digits=22, decimal_places=16, blank=True, null=True)


class HackathonLocation(models.Model):
    name = models.CharField(
        max_length=255,
        help_text="Where the hackathon is located (e.g. Buringlont, Ontario)",
        null=True,
        blank=True,
        db_index=True,
    )
    venue = models.CharField(
        max_length=255,
        help_text="what venue is the hackathon renting (e.g. University of Toronto)",
        null=True,
        blank=True,
    )
    country = models.CharField(
        max_length=255,
        help_text="what country",
        null=True,
        blank=True,
    )
    location = models.OneToOneField(
        Location,
        on_delete=models.RESTRICT,
        related_name="location",
        blank=True,
        null=True,
        db_index=True,
    )

    def __str__(self):
        return self.name


class ReviewStatus(models.TextChoices):
    Approved = "approved", "Approved"
    Rejected = "rejected", "Rejected"
    Pending = "pending", "Pending"
    RequestingChanges = "requesting_changes", "Requesting Changes"


class Hackathon(MetaDataMixin):
    objects = HackathonsManager()

    duplication_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        unique=True,
        help_text="Duplication ID for the Hackathon",
    )
    net_vote = models.BigIntegerField(default=0)

    source = models.CharField(
        max_length=255,
        choices=HackathonSource.choices,
        default=HackathonSource.UserSubmitted,
    )
    scrape_source = models.CharField(
        max_length=255, choices=SCRAPE_SOURCES, default="na"
    )
    metadata = models.JSONField(
        blank=True, null=True, help_text="Metadata about the source of the hackathon"
    )

    is_public = models.BooleanField(
        help_text="Is the hackathon visible to all users", default=False, db_index=True
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
    end_date = models.DateTimeField(blank=True, null=True, db_index=True)

    application_start = models.DateTimeField(blank=True, null=True)
    application_deadline = models.DateTimeField(blank=True, null=True)

    reimbursements = models.BooleanField(default=False)

    location = models.ForeignKey(
        HackathonLocation,
        on_delete=models.RESTRICT,
        related_name="hackathons",
        blank=True,
        null=True,
        db_index=True,
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

    fg_image = models.ImageField(
        upload_to="hackathon_images", null=True, blank=True, max_length=500
    )
    bg_image = models.ImageField(
        upload_to="hackathon_images", null=True, blank=True, max_length=500
    )

    hybrid = models.CharField(
        max_length=1,
        choices=HYBRID_CHOICES,
        default="I",
        help_text="Location of the hackathon, I for in-person, V for virtual, H for hybrid",
    )

    freeze_data = models.BooleanField(
        default=False,
        help_text="Set to True to not update any details using scraped data. Use if you get accurate details directly from the hackathon organizers.",
    )

    is_web3 = models.BooleanField(
        default=False, help_text="Is the hackathon Web3 themed"
    )
    is_diversity = models.BooleanField(
        default=False, help_text="Is the hackathon only for underrepresented groups"
    )
    is_restricted = models.BooleanField(
        default=False,
        help_text="Is enrollment in this hackathon restricted to only some group of people (like those enrolled in one specific school or unoversity)",
    )
    is_nonenglish = models.BooleanField(
        default=False, help_text="Is the primary language of this hackathon not English"
    )

    custom_info = models.JSONField(
        default=dict, null=True, blank=True
    )  # Anything else that we might want to add in a structured format

    class Meta:
        ordering = ["start_date"]
        indexes = [
            models.Index(
                fields=["end_date", "is_public"],
                name="hkthn_end_date_and_public_idx",
            ),
        ]

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

    @classmethod
    def annotate_user_data(cls, queryset, user):
        """
        Annotates the queryset with user's vote status using a single efficient query.
        Returns:
         - 1 for upvote
         - -1 for downvote
         - 0 for no vote
        """
        if not user.is_authenticated:
            return queryset.annotate(
                user_vote_status=Value(0, output_field=IntegerField()),
                user_saved=Value(False, output_field=BooleanField()),
            )

        return queryset.annotate(
            user_vote_status=Case(
                When(votes__hacker=user, votes__is_upvote=True, then=Value(1)),
                When(votes__hacker=user, votes__is_upvote=False, then=Value(-1)),
                default=Value(0),
                output_field=IntegerField(),
            ),
            user_saved=Exists(Hacker.objects.filter(saved=OuterRef("pk"), id=user.id)),
        )

    def save(self, *args, **kwargs):
        if self.start_date and timezone.is_naive(self.start_date):
            self.start_date = timezone.make_aware(self.start_date)
        elif self.end_date and timezone.is_naive(self.end_date):
            self.end_date = timezone.make_aware(self.end_date)

        if self.review_status == ReviewStatus.Approved:
            self.is_public = True
        elif self.review_status == ReviewStatus.Rejected:
            self.is_public = False

        if self.duplication_id is None:
            self.duplication_id = self.name.lower().replace(
                " ", ""
            ) + self.end_date.strftime("-%Y")
        else:
            pass

        super().save(*args, **kwargs)


class Vote(models.Model):
    is_upvote = models.BooleanField(blank=False)
    hackathon = models.ForeignKey(
        Hackathon, on_delete=models.CASCADE, related_name="votes"
    )
    hacker = models.ForeignKey(Hacker, on_delete=models.CASCADE, related_name="votes")
    time_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["hackathon", "hacker"], name="unique_hackathon_hacker_vote"
            )
        ]

    @property
    def vote_type(self):
        return "upvote" if self.is_upvote else "downvote"

    def __str__(self):
        return f"{self.vote_type} vote for {self.hackathon} by {self.hacker}"

    def save(self, *args, **kwargs):
        if not self.pk:  # New vote
            if Vote.objects.filter(
                hackathon=self.hackathon, hacker=self.hacker
            ).exists():
                raise ValidationError("User has already voted for this hackathon")
        super().save(*args, **kwargs)


class CuratorRequest(models.Model):
    hackathon = models.ForeignKey(Hackathon, on_delete=models.CASCADE)
    team_name = models.CharField(max_length=255)
    team_description = models.TextField()
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ManyToManyField(Hacker, related_name="curation_requests")
    review_status = models.CharField(
        max_length=255,
        blank=True,
        null=False,
        default=ReviewStatus.Pending,
        help_text="Status of the review process",
        choices=ReviewStatus.choices,
    )

    def __str__(self):
        return f"Curator request from {self.team_name} for {self.hackathon}"
