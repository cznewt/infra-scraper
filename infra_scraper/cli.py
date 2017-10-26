
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
    print(scraper.get_data(name, 'count', 'yaml'))


@click.command()
def scrape_all():
    scraper = InfraScraper()
    scraper.scrape_all_data()


@click.command()
def status():
    scraper = InfraScraper()
    print yaml.safe_dump(scraper.status())
