import json
from collections import OrderedDict
from lxml import html
import requests
from PageReader import PageReader

class SiteScraper:
    config = None
    results = {}

    def load_config(self, config_path):
        json_data = open(config_path).read()
        data = json.loads(json_data)
        self.config = data

    def run_scrape(self):
        for key, page in self.config['pages'].items():
            print(key)
            # print(page)
            self.results[key] = self.get_page_reader_results(page)
            # print(self.results)
            print("\n")
        self.analyze_scrape()

    def analyze_scrape(self):
        targets = {}
        for post_results in self.results['posts']:
            keys = post_results['body'].keys()
            for key in keys:
                if not key in targets:
                    targets[key] = 0
                targets[key] += 1
        targets = OrderedDict(sorted(targets.items(), key=lambda x:x[1]))
        print(targets)


    def get_page_reader_results(self, page):
        PageReader.config = page
        if (page['path']['type'] == 'url'):
            PageReader.config['path'] = page['path']['value']
        else:
            reference_page = page
            page_keys = page['path']['value'].split('.')
            path_values = self.results[page_keys[0]][page_keys[1]]
            results = []
            for path in path_values:
                reference_page['path'] = {
                    'value': str(path),
                    'type': 'url',
                }
                result = self.get_page_reader_results(reference_page);
                print(result)
                results.append(result)
            return results
        PageReader.config['schema'] = self.config['schema']
        PageReader.config['host'] = self.config['host']
        return PageReader.analyze_page()

site_scaper = SiteScraper()
site_scaper.load_config('./config.json')
results = site_scaper.run_scrape()
# print(results)