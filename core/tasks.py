from typing import TYPE_CHECKING

from celery.utils.log import get_task_logger

from hackathons_canada.celery import app

if TYPE_CHECKING:
    from core.models import Hacker

logger = get_task_logger(__name__)


# title=f"New hackathon: {instance.name}",
# message=f"New hackathon: {instance.name} has been created. Check it out at {instance.website}",


@app.task
def send_new_hackathon_email(user: "Hacker"):
    # todo setup email notifications
    # send_mail(
    #     "Your Feedback",
    #     f"\t{self.cleaned_data['message']}\n\nThank you!",
    #     "support@example.com",
    #     [self.cleaned_data["email_address"]],
    #     fail_silently=False,
    # )
    pass
