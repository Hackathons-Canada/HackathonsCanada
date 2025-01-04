import cloudscraper
from bs4 import BeautifulSoup
import datetime
from core.scraping.abstractdatasource import AbstractDataSource


class MLHSource(AbstractDataSource):
    URL = "https://mlh.io/seasons/{}/events"

    def scrape_page(self, **kwargs):
        scraper = cloudscraper.create_scraper()

        url = self.URL.format(kwargs.get("year", datetime.datetime.now().year))
        response = scraper.get(url)

        soup = BeautifulSoup(response.text, "html.parser")

        rows = soup.find_all("div", class_="row")
        events = []

        for row in rows:
            h3_tag = row.find("h3")
            if h3_tag and "Past Events" in h3_tag.text:
                break

            events.extend(row.find_all("a", class_="event-link"))
        return events

    def parse_event(self, ev, **kwargs):
        event_name = ev.find("h3", class_="event-name").text.strip()

        start_date = ev.find("meta", itemprop="startDate")["content"]
        end_date = ev.find("meta", itemprop="endDate")["content"]

        event_url = ev["href"]

        location = ev.find("div", class_="event-location")
        city = location.find("span", itemprop="city").text.strip()
        state = location.find("span", itemprop="state").text.strip()

        event_details = {
            "name": event_name,
            "start_date": start_date,
            "end_date": end_date,
            "url": event_url,
            "location": city + ", " + state,
        }

        return event_details


if __name__ == "__main__":
    mlh_scraper = MLHSource()

    events = mlh_scraper.get_events()

    for event in events:
        print(f"Event Name: {event['name']}")
        print(f"Start Date: {event['start_date']}")
        print(f"End Date: {event['end_date']}")
        print(f"Website URL: {event['url']}")
        print(f"Location: {event['location']['city']}, {event['location']['state']}")
        print("-----------")
    assert len(events) == 44
    print(len(events))
