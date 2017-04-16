import json
from lxml import html
import requests
from PageReader import PageReader

class SiteScraper:
    config = None

    def load_config(self, config_path):
        json_data = open(config_path).read()
        data = json.loads(json_data)
        self.config = data

    def run_scrape(self):
        PageReader.config = self.config
        results = PageReader.analyze_page()
        return results

site_scaper = SiteScraper()
site_scaper.load_config('./config.json')
results = site_scaper.run_scrape()
print(results)