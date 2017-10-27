
import click
import yaml
import logging
from infra_scraper.main import InfraScraper

logger = logging.getLogger(__name__)


@click.command()
@click.argument('name')
def scrape(name):
    scraper = InfraScraper()
    scraper.scrape_data(name)


@click.command()
@click.argument('name')
@click.argument('interval', default=10)
def scrape_forever(name, interval):
    scraper = InfraScraper()
    scraper.scrape_data_forever(name, int(interval))


@click.command()
def scrape_all():
    scraper = InfraScraper()
    scraper.scrape_all_data()


@click.command()
@click.argument('--interval', default=10)
def scrape_all_forever(interval):
    scraper = InfraScraper()
    scraper.scrape_all_data_forever(int(interval))


@click.command()
def status():
    scraper = InfraScraper()
    print yaml.safe_dump(scraper.status())
