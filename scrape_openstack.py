
from infra_scraper.main import InfraScraper

cloud_name = 'openstack-keystone2-admin'

scraper = InfraScraper()
scraper.scrape_data(cloud_name, 'openstack')
print(scraper.get_data(cloud_name, 'count', 'yaml'))
