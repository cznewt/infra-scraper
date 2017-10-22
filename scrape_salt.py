
import os
from infra_scraper.main import InfraScraper

config_name = 'salt'

config = {
    'name': config_name,
    'config_file': '{}/configs.yaml'.format(
        os.path.dirname(os.path.realpath(__file__))),
}

scraper = InfraScraper()
scraper.scrape_data(config_name, 'salt', config)
print(scraper.get_data(config_name, 'count', 'yaml'))
