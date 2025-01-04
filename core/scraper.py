from core.scraping.devpost import DevpostSource
from core.scraping.ethglobal import EthGlobalSource
from core.scraping.hackclubsource import HackClubSource
from core.scraping.mlh import MLHSource


def scrape_all(num):
    if num == 1:
        src = MLHSource()
        evs = src.get_events()
    if num == 2:
        src = DevpostSource()
        evs = src.get_events()
    if num == 3:
        src = EthGlobalSource()
        evs = src.get_events()
    if num == 4:
        src = HackClubSource()
        evs = src.get_events()

    src.save(evs)
