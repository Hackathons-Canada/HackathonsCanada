import re
import json
import sqlite3
import datetime
import requests
import itertools
import cloudscraper

from bs4 import BeautifulSoup
from icalendar import Calendar, Event

from hackathons_canada.settings import CUR_YEAR
from core.models import Hackathon

# Abstract source class that can be extended to create new sources
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
        r = scraper.get(self.URL.format(kwargs.get('year', datetime.datetime.now().year)))

        page = BeautifulSoup(r.text)
        divs = page.find_all("div", {"class": "row"})

        return divs[1].find_all("a", {"class": "event-link"}) + divs[2].find_all("a", {"class": "event-link"})

    def parse_event(self, ev, **kwargs):
        loc = ev.find_all("div", {"class": "event-location"})[0]

        evinfo = {
            "name": ev.find_all("h3", {"class": "event-name"})[0].contents[0],
            "startdate": datetime.datetime.strptime(ev.find_all("meta", {"itemprop": "startDate"})[0]["content"], "%Y-%m-%d"),
            "enddate": datetime.datetime.strptime(ev.find_all("meta", {"itemprop": "endDate"})[0]["content"], "%Y-%m-%d"),
            "location": loc.find_all("span", {"itemprop": "city"})[0].contents[0] + ", " \
                + loc.find_all("span", {"itemprop": "state"})[0].contents[0],
            "hybrid": ev.find_all("div", {"class": "event-hybrid-notes"})[0].find_all("span")[0].contents[0][0],
            "is_diversity": len(ev.find_all("div", {"class": "diversity-event-badge"})) > 0,
            "max_edulevel": "H" if len(ev.find_all("div", {"class": "ribbon"})) > 0 and \
                len(ev.find_all("div", {"class": "diversity-event-badge"})) == 0 else "X",
            "url": ev["href"],
            "bgimage": ev.find_all("div", {"class": "image-wrap"})[0].find_all("img")[0]["src"],
            "fgimage": ev.find_all("div", {"class": "event-logo"})[0].find_all("img")[0]["src"],
            "source": "mlh"
        }

        return evinfo


class DevpostSource(AbstractDataSource):
    URL = "https://devpost.com/api/hackathons?status[]=upcoming&status[]=open"

    def scrape_page(self, **kwargs):
        evs = []
        total = 1; cur = 0; i = 0
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
        startdate += enddate[-6:]
        startdate = datetime.datetime.strptime(startdate, "%b %d, %Y")
        enddate = datetime.datetime.strptime(enddate, "%b %d, %Y")

        evinfo = {
            "name": ev["title"],
            "startdate": startdate,
            "enddate": enddate,
            "location": ev["displayed_location"]["location"],
            "hybrid": "O" if ev["displayed_location"]["location"] == "Online" else "I",
            "is_diversity": False,
            "is_restricted": ev["open_state"] != "open",
            "url": ev["url"],
            "fgimage": ev["thumbnail_url"],
            "source": "dev"
        }

        return evinfo


class EthGlobalSource(AbstractDataSource): 
    URL = "https://ethglobal.com/events/hackathons"
    
    def scrape_page(self, **kwargs):
        r = requests.get(self.URL)
        page = BeautifulSoup(r.text)
        return page.select('a[href^="/events/"]')

    def parse_event(self, ev, **kwargs):
        if ev.get("href") == "/events/hackathons" or ev.get("href") == "/events/summits":
            return None

        name = ev.find_all("h3")[0].contents[0]
        startdate = ev.find_all("time")[0].contents[0]
        enddate = ev.find_all("time")[1].contents[0]
        startdate = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', startdate)
        enddate = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', enddate)
        startdate = datetime.datetime.strptime(startdate, "%b %d, %Y")
        enddate = datetime.datetime.strptime(enddate, "%b %d, %Y")

        evinfo = {
            "name": name,
            "startdate": startdate,
            "enddate": enddate,
            "location": " ".join(name.split()[1:]) \
                if (name.split()[0].lower() == "ethglobal") else "",
            "is_web3": True,
            "is_restricted": False,
            "url": "https://ethglobal.com" + ev.get("href"),
            "fgimage": ev.find_all("img")[0]["src"],
            "source": "eth"
        }

        return evinfo


class HackClubSource(AbstractDataSource):
    URL = "https://hackathons.hackclub.com/"

    def scrape_page(self, **kwargs):
        r = requests.get(self.URL)

        page = BeautifulSoup(r.text)
        return page.find_all("div", {"class": "css-4jawwy"})[0].find_all("a")

    def parse_event(self, ev, **kwargs):
        try:
            loc = ev.find_all("span", {"itemprop": "address"})[0].contents[2]
        except IndexError: loc = ""

        evinfo = {
            "name": ev.find_all("h3")[0].contents[0],
            "startdate": datetime.datetime.strptime(ev.find_all("span", \
                {"itemprop": "startDate"})[0]["content"].split("T")[0], "%Y-%m-%d"),
            "enddate": datetime.datetime.strptime(ev.find_all("span", \
                {"itemprop": "endDate"})[0]["content"].split("T")[0], "%Y-%m-%d"),
            "location": loc,
            "hybrid": ev.find_all("span", {"itemtype": "VirtualLocation"})[0].contents[0][0],
            "max_edulevel": "H",
            "url": ev["href"],
            "fgimage": ev.find_all("img")[0]["src"],
            "source": "hcl"
        }

        return evinfo


def scrape_all():
    mlh = itertools.chain.from_iterable([MLHSource().get_events(year=i) for i in CUR_YEAR]) \
        if type(CUR_YEAR) is list else MLHSource().get_events(year=CUR_YEAR)
    evs = itertools.chain(
        mlh,
        DevpostSource().get_events(),
        EthGlobalSource().get_events(),
        HackClubSource().get_events(),
    )

    for ev in evs:
        if ev is not None:
            h = Hackathon.objects.filter(id=Hackathon.get_id(ev["name"], ev["enddate"]))
            if len(h) == 0:
                h1 = Hackathon()
            else:
                h1 = h[0]
                if h1.freeze_data: continue

            for attr, value in ev.items():
                setattr(h1, attr, value)

            if h1.location == "":
                h1.location = "Online" if h1.hybrid == "O" else "Unknown"
            h1.last_scraped = datetime.datetime.now()
            h1.save()


def extract_text_from_url(url):
    # Send a GET request to fetch the content of the webpage
    scraper = cloudscraper.create_scraper()
    response = scraper.get(url)
    
    # Check if the request was successful
    if response.status_code != 200:
        raise Exception(f"Failed to fetch the page. Status code: {response.status_code}")
    
    # Parse the webpage content
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extract text from paragraphs and headings (can be adjusted based on the webpage structure)
    text = []
    for tag in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
        if tag.get_text(strip=True):
            text.append(tag.get_text(strip=True))
    
    # Join the list into a single string
    clean_text = "\n".join(text)
    
    return clean_text
