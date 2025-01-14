import cloudscraper
from datetime import datetime
from core.scraping.abstractdatasource import AbstractDataSource


class DevpostSource(AbstractDataSource):
    URL = "https://devpost.com/api/hackathons?status[]=upcoming&status[]=open"

    def scrape_page(self, **kwargs):
        page = kwargs.get("page", 1)
        scraper = cloudscraper.create_scraper()  # Create a Cloudscraper instance
        response = scraper.get(f"{self.URL}&page={page}")
        if response.status_code != 200:
            return [], 0, "invalid"
        data = response.json()
        return (
            data.get("hackathons", []),
            data.get("meta", {}).get("total_count", 0),
            "valid",
        )

    def get_events(self, **kwargs):
        all_events = []
        page = 1
        total_count = 1
        while len(all_events) < total_count:
            events, temp, status = self.scrape_page(page=page, **kwargs)
            if (not events) and status == "valid":
                break
            if not events:
                page += 1
                continue
            total_count = temp
            all_events.extend(events)
            page += 1
        return [self.parse_event(ev, **kwargs) for ev in all_events]

    def parse_event(self, ev, **kwargs):
        submission_dates = ev.get("submission_period_dates", "").split(" - ")
        start_date_str = submission_dates[0] if len(submission_dates) > 0 else ""
        end_date_str = (
            submission_dates[1] if len(submission_dates) > 1 else start_date_str
        )
        current_year = datetime.now().year
        start_date, end_date = self.parse_date(
            start_date_str, end_date_str, current_year
        )
        location = ev.get("displayed_location", {}).get("location", "Unknown Location")
        return {
            "name": ev.get("title", "Unknown Title"),
            "start_date": (
                start_date.strftime("%Y-%m-%d") if start_date else "Unknown Start Date"
            ),
            "end_date": (
                end_date.strftime("%Y-%m-%d") if end_date else "Unknown End Date"
            ),
            "url": ev.get("url", "Unknown URL"),
            "location": location,
        }

    def parse_date(self, start_date_str, end_date_str, current_year):
        start_date, end_date = None, None
        try:
            if start_date_str:
                if "," in start_date_str:
                    date_parts = start_date_str.split(", ")
                    start_date = datetime.strptime(
                        f"{date_parts[0]} {date_parts[1]}", "%b %d %Y"
                    ).date()
                    date_parts = end_date_str.split(", ")
                    end_date = datetime.strptime(
                        f"{date_parts[0]} {date_parts[1]}", "%b %d %Y"
                    ).date()
                else:
                    start_date = datetime.strptime(
                        f"{start_date_str} {current_year}", "%b %d %Y"
                    )
                    end_date = start_date

            if end_date_str and not end_date:
                end_date = datetime.strptime(
                    f"{end_date_str} {current_year}", "%b %d %Y"
                ).date()
        except ValueError:
            pass

        return start_date, end_date


if __name__ == "__main__":
    devpost_scraper = DevpostSource()

    events = devpost_scraper.get_events()

    for event in events:
        print(f"Event Name: {event['name']}")
        print(f"Start Date: {event['start_date']}")
        print(f"End Date: {event['end_date']}")
        print(f"Website URL: {event['url']}")
        print(f"Location: {event['location']}")
        print("-----------")
    print(f"Total events fetched: {len(events)}")
