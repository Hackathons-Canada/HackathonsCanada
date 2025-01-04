import cloudscraper
from bs4 import BeautifulSoup
from datetime import datetime
from core.scraping.abstractdatasource import AbstractDataSource


class EthGlobalSource(AbstractDataSource):
    URL = "https://ethglobal.com/events/hackathons"

    def scrape_page(self):
        scraper = cloudscraper.create_scraper()
        response = scraper.get(self.URL)
        if response.status_code != 200:
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        event_cards = soup.find_all("a", href=True)
        events = []

        for card in event_cards:
            event_url = f"https://ethglobal.com{card['href']}"
            header = card.find("header")
            if header:
                title = header.find("h3").get_text(strip=True)
                start_date, end_date = self.extract_dates(card)
                location = self.extract_location(card, title)

                events.append(
                    {
                        "name": title,
                        "url": event_url,
                        "location": location,
                        "start_date": start_date,
                        "end_date": end_date,
                    }
                )

        return events

    def extract_dates(self, card):
        dates = card.find_all("time")
        if dates:
            start_date_str = dates[0].get_text(strip=True).split(", ")
            end_date_str = dates[1].get_text(strip=True).split(", ")
            start_date = str(
                self.parse_date(f"{start_date_str[0]} {start_date_str[1]}")
            )
            end_date = str(self.parse_date(f"{end_date_str[0]} {end_date_str[1]}"))
        else:
            dates = card.find_all("div")[-1].get_text().split(", ")
            start_date = (
                str(datetime.strptime(f"{dates[0]} {dates[1]}", "%b %Y").date())[:-2]
                + "xx"
            )
            end_date = start_date

        return start_date, end_date

    def extract_location(self, card, name):
        location_div = card.find_all("div")[2]
        is_virtual = location_div.get_text(strip=True)
        if is_virtual == "Virtual":
            return is_virtual
        return " ".join(name.split()[1:])

    def parse_event(self, ev):
        start_date = ev["start_date"]
        end_date = ev["end_date"]

        return {
            "name": ev.get("name", "Unknown Title"),
            "start_date": (start_date if start_date else "Unknown Start Date"),
            "end_date": (end_date if end_date else "Unknown End Date"),
            "url": ev.get("url", "Unknown URL"),
            "location": ev.get("location", "Unknown Location"),
        }

    def parse_date(self, date_str):
        try:
            return datetime.strptime(date_str, "%b %d %Y").date()
        except ValueError:
            return None


if __name__ == "__main__":
    ethglobal_scraper = EthGlobalSource()
    events = ethglobal_scraper.get_events()

    for event in events:
        print(f"Event Name: {event['name']}")
        print(f"Start Date: {event['start_date']}")
        print(f"End Date: {event['end_date']}")
        print(f"Website URL: {event['url']}")
        print(f"Location: {event['location']}")
        print("-----------")
    print(f"Total events fetched: {len(events)}")
