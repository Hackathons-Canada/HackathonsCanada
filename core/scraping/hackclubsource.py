import cloudscraper
from bs4 import BeautifulSoup
from datetime import datetime
from core.scraping.abstractdatasource import AbstractDataSource


class HackClubSource(AbstractDataSource):
    URL = "https://hackathons.hackclub.com"

    def scrape_page(self, **kwargs):
        scraper = cloudscraper.create_scraper()
        response = scraper.get(self.URL)
        if response.status_code != 200:
            return [], 0, "invalid"

        soup = BeautifulSoup(response.text, "html.parser")

        event_cards = soup.select("main > div > div a")
        events = []

        for card in event_cards:
            event_url = card["href"]
            title = card.find("h3", itemprop="name").get_text(strip=True)
            start_date_str = card.find("span", itemprop="startDate")["content"]
            end_date_str = card.find("span", itemprop="endDate")["content"]
            event_type = card.find("span").get_text(strip=True)
            if event_type == "In-Person":
                location = card.find("span", itemprop="address").get_text(strip=True)[
                    1:
                ]
            else:
                location = event_type

            if not self.is_upcoming(start_date_str):
                continue

            events.append(
                {
                    "name": title,
                    "url": event_url,
                    "location": location,
                    "start_date": start_date_str,
                    "end_date": end_date_str,
                }
            )

        return events

    def get_events(self, **kwargs):
        events = self.scrape_page(**kwargs)
        return [self.parse_event(ev, **kwargs) for ev in events]

    def parse_event(self, ev, **kwargs):
        start_date_str = ev["start_date"]
        end_date_str = ev["end_date"]

        start_date = self.parse_datetime(start_date_str)
        end_date = self.parse_datetime(end_date_str)

        return {
            "name": ev.get("name", "Unknown Title"),
            "start_date": (
                start_date.strftime("%Y-%m-%d") if start_date else "Unknown Start Date"
            ),
            "end_date": (
                end_date.strftime("%Y-%m-%d") if end_date else "Unknown End Date"
            ),
            "url": ev.get("url", "Unknown URL"),
            "location": ev.get("location", "Unknown Location"),
        }

    def parse_datetime(self, datetime_str):
        try:
            return datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%S.%fZ")
        except ValueError:
            return None

    def is_upcoming(self, start_date_str):
        current_date = datetime.utcnow()

        start_date = self.parse_datetime(start_date_str)
        if start_date is None:
            return False

        return start_date > current_date


if __name__ == "__main__":
    hackclub_scraper = HackClubSource()

    events = hackclub_scraper.get_events()

    for event in events:
        print(f"Event Name: {event['name']}")
        print(f"Start Date: {event['start_date']}")
        print(f"End Date: {event['end_date']}")
        print(f"Website URL: {event['url']}")
        print(f"Location: {event['location']}")
        print("-----------")
    print(f"Total events fetched: {len(events)}")
