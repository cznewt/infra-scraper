
import os
from infra_scraper.main import InfraScraper

cluster_name = 'kubernetes'

config = {
    'name': cluster_name,
    'config_file': '{}/clusters.yaml'.format(
        os.path.dirname(os.path.realpath(__file__))),
}

scraper = InfraScraper()
scraper.scrape_data(cluster_name, 'kubernetes', config)
print(scraper.get_data(cluster_name, 'count', 'yaml'))
