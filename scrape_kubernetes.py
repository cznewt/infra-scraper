
from infra_scraper.main import InfraScraper

cluster_name = 'kubernetes-clientcert-admin'

scraper = InfraScraper()
scraper.scrape_data(cluster_name, 'kubernetes')
print(scraper.get_data(cluster_name, 'count', 'yaml'))
