from core.models import Hackathon, ReviewStatus


def unreviewed_hackathons(request) -> str:
    """Returns count of all hackathons that haven't yet been reviewed."""
    unreviewed_hackathons_count: int = Hackathon.objects.filter(
        review_status=ReviewStatus.Pending
    ).count()
    if unreviewed_hackathons_count == 0:
        return ""  # No unreviewed hackathons, no need to display anything
    return str(unreviewed_hackathons_count)
