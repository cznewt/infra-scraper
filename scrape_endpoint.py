
from infra_scraper.main import InfraScraper

# name = 'openstack-keystone2-admin'
name = 'kubernetes-clientcert-admin'
#name = 'salt-admin'
#name = 'terraform-openstack-app'

scraper = InfraScraper()
scraper.scrape_data(name)
print(scraper.get_data(name, 'count', 'yaml'))
