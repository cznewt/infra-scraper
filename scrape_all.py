
from infra_scraper.main import InfraScraper

cluster_name = 'kubernetes-clientcert-admin'

scraper = InfraScraper()
scraper.scrape_all_data()
