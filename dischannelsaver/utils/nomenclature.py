import datetime
import re

from core.models import Hackathon


def generate_discord_timestamp(date: datetime.datetime):
    return f"<t:{int(date.timestamp())}:R"


def generate_channel_name(hackathon: Hackathon):
    """

    :param hackathon:
    :return: discord channel name (e.g. hackathon-name-Jan-3-5), or if it's a 1-day hackathon, hackathon-name-Jan-24
    """

    assert hackathon.start_date is not None, "Hackathon start date is None"
    assert hackathon.end_date is not None, "Hackathon end date is None"

    name = hackathon.name.casefold().replace(
        " ", "-"
    )  # todo redo using the spec william provided in #general
    if hackathon.end_date.day == hackathon.start_date.day:
        return f"{name}-{hackathon.start_date.strftime('%b-%-d')}"
    return f"{name}-{hackathon.start_date.strftime('%b-%-d')}-{hackathon.end_date.strftime('%-d')}"


def create_datetime(month, day) -> datetime.datetime:
    """
    Creates a datetime object for the given month and day,
    assuming the year is the one where the month is closest to now.

    Args:
            month (int): Month (1-12).
            day (int): Day (1-31).

    Returns:
            datetime.datetime: The datetime object.

    Raises:
            ValueError: If the month or day is out of range.
    """

    def month_name_to_number(name):
        return {
            "jan": 1,
            "feb": 2,
            "mar": 3,
            "apr": 4,
            "may": 5,
            "jun": 6,
            "jul": 7,
            "aug": 8,
            "sep": 9,
            "oct": 10,
            "nov": 11,
            "dec": 12,
        }[name.lower()]

    now = datetime.datetime.now()
    month = month_name_to_number(month)

    # Check for valid month and day
    if month < 1 or month > 12:
        raise ValueError("Month must be between 1 and 12")
    if day < 1 or day > 31:
        raise ValueError("Day must be between 1 and 31")

    # Try current year first
    potential_date = datetime.datetime(year=now.year, month=month, day=day)

    # Check if the month has already passed in the current year
    if potential_date < now:
        # Try next year if month has passed
        next_year = now.year + 1
    else:
        # Keep current year if month is in the future
        next_year = now.year

    # Create datetime object for next year
    next_year_date = datetime.datetime(next_year, month, day)

    # Choose the date closest to now
    return min(potential_date, next_year_date)


def get_months(channel_name):
    """

    :param channel_name:
    :return: month (e.g. Jan), day (e.g. 0
    """
    PATTERN = r"^.*-(\w{3})-(\d+)(?:-(\d+))?$"
    match = re.match(PATTERN, channel_name)
    if not match:
        return None
    if match.groups()[
        2
    ]:  # If the third group is not None (i.e. the end date is present)
        return match.groups()
    return match.groups() + (match.groups()[1],)
