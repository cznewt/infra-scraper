
from infra_scraper.main import InfraScraper

cloud_name = 'keystone'

config = {
    'name': cloud_name,
}

scraper = InfraScraper()
scraper.scrape_data(cloud_name, 'openstack', config)
print(scraper.get_data(cloud_name, 'count', 'yaml'))
