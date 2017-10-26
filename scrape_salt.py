
from infra_scraper.main import InfraScraper

config_name = 'salt-admin'

scraper = InfraScraper()
scraper.scrape_data(config_name, 'salt')
print(scraper.get_data(config_name, 'count', 'yaml'))
