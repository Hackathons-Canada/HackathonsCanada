import re
import datetime
import requests
import itertools
import cloudscraper
from django.utils import timezone
from bs4 import BeautifulSoup

# from icalendar import Calendar, Event

from hackathons_canada.settings import CUR_YEAR

from django.apps import apps

if apps.ready:
    from core.models import (
        Hackathon,
        HackathonSource,
        HackathonLocation,
        Location,
        ReviewStatus,
    )

username = "Nirek"


def search_city(city_name, username):
    url = f"http://api.geonames.org/searchJSON?q={city_name}&maxRows=10&username={username}&maxRows=1&style=MEDIUM"
    if (
        "online" in city_name.lower()
        or "remote" in city_name.lower()
        or "virtual" in city_name.lower()
        or "everywhere" in city_name.lower()
    ):
        return {
            "city": "Online",
            "state": "Online",
            "country": "Online",
            "latitude": None,
            "longitude": None,
        }
    try:
        response = requests.get(url)
        response.raise_for_status()

        data = response.json()

        if "geonames" not in data or not data["geonames"]:
            return {
                "city": "Online",
                "state": "Online",
                "country": "Online",
                "latitude": None,
                "longitude": None,
            }

        # Extract relevant information for each city
        city_data = data["geonames"][0]
        if city_data:
            city = {
                "city": city_data.get("name"),
                "state": city_data.get("adminName1"),
                "country": city_data.get("countryName"),
                "latitude": city_data.get("lat"),
                "longitude": city_data.get("lng"),
            }
            return city
        else:
            return {
                "city": "Online",
                "state": "Online",
                "country": "Online",
                "latitude": None,
                "longitude": None,
            }
    except requests.RequestException:
        return None


class AbstractDataSource:
    URL = ""

    def scrape_page(self, **kwargs):
        raise NotImplementedError

    def parse_event(self, ev, **kwargs):
        raise NotImplementedError

    def get_events(self, **kwargs):
        evs = self.scrape_page(**kwargs)
        ans = [self.parse_event(ev, **kwargs) for ev in evs]
        return ans


class MLHSource(AbstractDataSource):
    URL = "https://mlh.io/seasons/{}/events"

    def scrape_page(self, **kwargs):
        scraper = cloudscraper.create_scraper()
        r = scraper.get(
            self.URL.format(kwargs.get("year", datetime.datetime.now().year))
        )

        page = BeautifulSoup(r.text, "html.parser")
        divs = page.find_all("div", {"class": "row"})

        return divs[1].find_all("a", {"class": "event-link"}) + divs[2].find_all(
            "a", {"class": "event-link"}
        )

    def parse_event(self, ev, **kwargs):
        loc = ev.find_all("div", {"class": "event-location"})[0]
        loc_data = (
            loc.find_all("span", {"itemprop": "city"})[0].contents[0]
            + "+"
            + loc.find_all("span", {"itemprop": "state"})[0].contents[0]
        )
        geoData = search_city(loc_data, username)
        name = ev.find_all("h3", {"class": "event-name"})[0].contents[0]
        end_date = timezone.make_aware(
            datetime.datetime.strptime(
                ev.find_all("meta", {"itemprop": "endDate"})[0]["content"], "%Y-%m-%d"
            )
        )
        start_date = timezone.make_aware(
            datetime.datetime.strptime(
                ev.find_all("meta", {"itemprop": "startDate"})[0]["content"], "%Y-%m-%d"
            )
        )

        if geoData["latitude"] is None:
            location_cord = None
        else:
            location_cord, created = Location.objects.get_or_create(
                latitude=geoData["latitude"], longitude=geoData["longitude"]
            )
        hackathonLocation_input, created = HackathonLocation.objects.get_or_create(
            name=f"{geoData['city']}, {geoData['state']}",
            country=geoData["country"],
            location=location_cord,
        )

        evinfo = {
            "name": name.rstrip(),
            "start_date": start_date,
            "end_date": end_date,
            "location": hackathonLocation_input,
            "hybrid": ev.find_all("div", {"class": "event-hybrid-notes"})[0]
            .find_all("span")[0]
            .contents[0][0],
            "maximum_education_level": 1
            if len(ev.find_all("div", {"class": "ribbon"})) > 0
            and len(ev.find_all("div", {"class": "diversity-event-badge"})) == 0
            else 5,
            "website": ev["href"],
            "bg_image": ev.find_all("div", {"class": "image-wrap"})[0].find_all("img")[
                0
            ]["src"],
            "fg_image": ev.find_all("div", {"class": "event-logo"})[0].find_all("img")[
                0
            ]["src"],
            "is_diversity": len(ev.find_all("div", {"class": "diversity-event-badge"}))
            > 0,
            "source": HackathonSource.Scraped,
            "scrape_source": "mlh",
            "is_public": True,
        }

        return evinfo


class DevpostSource(AbstractDataSource):
    URL = "https://devpost.com/api/hackathons?status[]=upcoming&status[]=open"

    def scrape_page(self, **kwargs):
        evs = []
        total = 1
        cur = 0
        i = 0
        while cur < total:
            r = requests.get(self.URL + (f"&page={i}" if i > 1 else ""))
            res = r.json()
            evs += res["hackathons"]
            total = res["meta"]["total_count"]
            cur += res["meta"]["per_page"]

        return evs

    def parse_event(self, ev, **kwargs):
        dates = ev["submission_period_dates"].split("-")
        startdate = dates[0].strip()
        enddate = dates[1].strip()
        if len(startdate.split(" ")) == 2:
            startdate += enddate[-6:]
        if len(enddate.split(" ")) == 2:
            enddate = startdate.split(" ")[0] + " " + enddate
        startdate = timezone.make_aware(
            datetime.datetime.strptime(startdate, "%b %d, %Y")
        )
        enddate = timezone.make_aware(datetime.datetime.strptime(enddate, "%b %d, %Y"))
        loc = ev["displayed_location"]["location"]
        geoData = search_city(loc, username)

        if geoData["latitude"] is None:
            location_cord = None
        else:
            location_cord, created = Location.objects.get_or_create(
                latitude=geoData["latitude"], longitude=geoData["longitude"]
            )
        hackathonLocation_input, created = HackathonLocation.objects.get_or_create(
            name=f"{geoData['city']}, {geoData['state']}",
            country=geoData["country"],
            location=location_cord,
        )

        evinfo = {
            "name": ev["title"].rstrip(),
            "start_date": startdate,
            "end_date": enddate,
            "location": hackathonLocation_input,
            "hybrid": "O" if ev["displayed_location"]["location"] == "Online" else "I",
            "website": ev["url"],
            "fg_image": ev["thumbnail_url"],
            "is_restricted": ev["open_state"] != "open",
            "source": HackathonSource.Scraped,
            "scrape_source": "dev",
            "is_public": True,
        }

        return evinfo


class EthGlobalSource(AbstractDataSource):
    URL = "https://ethglobal.com/events/hackathons"

    def scrape_page(self, **kwargs):
        r = requests.get(self.URL)
        page = BeautifulSoup(r.text, features="html.parser")
        return page.select('a[href^="/events/"]')

    def parse_event(self, ev, **kwargs):
        if (
            ev.get("href") == "/events/hackathons"
            or ev.get("href") == "/events/summits"
        ):
            return None

        name = ev.find_all("h3")[0].contents[0]
        try:
            startdate = ev.find_all("time")[0].contents[0]
            enddate = ev.find_all("time")[1].contents[0]
        except IndexError:
            return {}
        startdate = re.sub(r"(\d+)(st|nd|rd|th)", r"\1", startdate)
        enddate = re.sub(r"(\d+)(st|nd|rd|th)", r"\1", enddate)
        startdate = datetime.datetime.strptime(startdate, "%b %d, %Y")
        enddate = datetime.datetime.strptime(enddate, "%b %d, %Y")

        loc = " ".join(name.split()[1:])
        geoData = search_city(loc, username)

        if geoData["latitude"] is None:
            location_cord = None
        else:
            location_cord, created = Location.objects.get_or_create(
                latitude=geoData["latitude"], longitude=geoData["longitude"]
            )
        hackathonLocation_input, created = HackathonLocation.objects.get_or_create(
            name=f"{geoData['city']}, {geoData['state']}",
            country=geoData["country"],
            location=location_cord,
        )

        evinfo = {
            "name": name.rstrip(),
            "start_date": startdate,
            "end_date": enddate,
            "location": hackathonLocation_input,
            "website": "https://ethglobal.com" + ev.get("href"),
            "fg_image": ev.find_all("img")[0]["src"],
            "source": HackathonSource.Scraped,
            "scrape_source": "eth",
            "is_public": True,
        }

        return evinfo


class HackClubSource(AbstractDataSource):
    URL = "https://hackathons.hackclub.com/"

    def scrape_page(self, **kwargs):
        r = requests.get(self.URL)

        page = BeautifulSoup(r.text, features="html.parser")
        return page.find_all("div", {"class": "css-4jawwy"})[0].find_all("a")

    def parse_event(self, ev, **kwargs):
        try:
            loc = ev.find_all("span", {"itemprop": "address"})[0].contents[2]
        except IndexError:
            loc = ""
        end_date = timezone.make_aware(
            datetime.datetime.strptime(
                ev.find_all("span", {"itemprop": "endDate"})[0]["content"].split("T")[
                    0
                ],
                "%Y-%m-%d",
            )
        )
        name = ev.find_all("h3")[0].contents[0]

        geoData = search_city(loc, username)

        if geoData["latitude"] is None:
            location_cord = None
        else:
            location_cord, created = Location.objects.get_or_create(
                latitude=geoData["latitude"], longitude=geoData["longitude"]
            )
        hackathonLocation_input, created = HackathonLocation.objects.get_or_create(
            name=f"{geoData['city']}, {geoData['state']}",
            country=geoData["country"],
            location=location_cord,
        )

        evinfo = {
            "name": name.rstrip(),
            "start_date": datetime.datetime.strptime(
                ev.find_all("span", {"itemprop": "startDate"})[0]["content"].split("T")[
                    0
                ],
                "%Y-%m-%d",
            ),
            "end_date": end_date,
            "location": hackathonLocation_input,
            "hybrid": ev.find_all("span", {"itemtype": "VirtualLocation"})[0].contents[
                0
            ][0],
            "maximum_education_level": 1,
            "website": ev["href"],
            "fg_image": ev.find_all("img")[0]["src"],
            "source": HackathonSource.Scraped,
            "scrape_source": "hcl",
            "is_public": True,
        }

        return evinfo


def scrape_all():
    mlh = (
        itertools.chain.from_iterable(
            [MLHSource().get_events(year=i) for i in CUR_YEAR]
        )
        if type(CUR_YEAR) is list
        else MLHSource().get_events(year=CUR_YEAR)
    )
    evs = itertools.chain(
        mlh,
        DevpostSource().get_events(),
        EthGlobalSource().get_events(),
        HackClubSource().get_events(),
    )

    for ev in evs:
        if ev == {}:
            continue
        if ev is not None:
            end_date = ev["end_date"]
            if timezone.is_naive(end_date):
                end_date = timezone.make_aware(end_date)

            ev["duplication_id"] = ev["name"].lower().replace(
                " ", ""
            ) + end_date.strftime("-%Y")

            hackathon = Hackathon.objects.filter(
                duplication_id=ev["duplication_id"]
            ).first()

            if hackathon is not None:
                hackathon.start_date = ev["start_date"]
                hackathon.end_date = end_date
                hackathon.location = ev["location"]
                hackathon.source = HackathonSource.Scraped
                hackathon.scrape_source = ev["scrape_source"]
                hackathon.review_status = ReviewStatus.Approved
                hackathon.is_public = True
                hackathon.duplication_id = ev["duplication_id"]
                hackathon.save()
            else:
                hackathon = Hackathon()
                for attr, value in ev.items():
                    setattr(hackathon, attr, value)
                hackathon.review_status = ReviewStatus.Approved
                hackathon.duplication_id = ev["duplication_id"]

                hackathon.save()


def extract_text_from_url(url):
    # Send a GET request to fetch the content of the webpage
    scraper = cloudscraper.create_scraper()
    response = scraper.get(url)

    # Check if the request was successful
    if response.status_code != 200:
        raise Exception(
            f"Failed to fetch the page. Status code: {response.status_code}"
        )

    # Parse the webpage content
    soup = BeautifulSoup(response.content, features="html.parser")

    # Extract text from paragraphs and headings (can be adjusted based on the webpage structure)
    text = []
    for tag in soup.find_all(["p", "h1", "h2", "h3", "h4", "h5", "h6"]):
        if tag.get_text(strip=True):
            text.append(tag.get_text(strip=True))

    # Join the list into a single string
    clean_text = "\n".join(text)

    return clean_text
