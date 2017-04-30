import json
import csv
import time
from PageReader import PageReader

# Main class, loads config, runs the scrape, and handles scrape output
class SiteScraper:
    # Config data loaded from JSON
    config = None
    # Raw page scraper results
    results = {}
    # Results after analysis (collation, key counting, etc.)
    analyzed_results = {}

    # Loads config from a JSON file
    def load_config(self, config_path):
        json_data = open(config_path).read()
        data = json.loads(json_data)
        self.config = data

    # Main run function, scrapes all pages in the config and outputs results
    def run_scrape(self):
        for key, page in self.config['pages'].items():
            self.results[key] = self._get_page_reader_results(page, True)
        self._analyze_scrape()
        self._output_results()

    # Runs through results and counts key occurances if config has the
    # xpath target set to save the results
    def _analyze_scrape(self):
        target_results = {}
        for key, results in self.results.items():
            for result in results:
                for target, data in result.items():
                    if self._should_save_results(key, target) == False:
                        continue;
                    if not target in target_results:
                        target_results[target] = {}
                    target_keys = data.keys()
                    for target_key in target_keys:
                        if not target_key in target_results.get(target, {}):
                            target_results[target][target_key] = 0
                        target_results[target][target_key] += 1
        self.analyzed_results = target_results

    # Determines output strategy from config and calls the function
    # prints an error if the function doesn't exist
    def _output_results(self):
        output_strategy = '_output_' + self.config['output']
        try:
            getattr(self, output_strategy)()
        except AttributeError:
            print('Expected function ' + output_strategy + ' does not exist')

    # Saves analyzed results by appending them to a csv file
    def _output_csv(self):
        print(self.analyzed_results)
        date = time.strftime("%m-%d-%Y %H:%M:%S")
        for target, data in self.analyzed_results.items():
            filename = self.config['host'] + '.' + target + '.csv'
            with open(filename, 'a', newline='') as file_handle:
                writer = csv.writer(file_handle, delimiter=',')
                for key, value in data.items():
                    writer.writerow([date, key, value])

    # Helper function to determine if the target results should be 
    # included in the output
    def _should_save_results(self, key, target):
        target_config = self.config['pages'][key]['targets'][target]
        if not 'save' in target_config:
            return False
        if (target_config['save'] == False):
            return False
        return True

    # Calls into PageReader to scrape the site by running through each
    # page from the config, referencing urls from a previous page if specified
    def _get_page_reader_results(self, page, top_level = False):
        PageReader.config = page
        if (page['path']['type'] == 'url'):
            PageReader.config['path'] = page['path']['value']
        else:
            reference_page = page
            page_keys = page['path']['value'].split('.')
            path_values = self.results[page_keys[0]][0][page_keys[1]]
            results = []
            for path in path_values:
                reference_page['path'] = {
                    'value': str(path),
                    'type': 'url',
                }
                result = self._get_page_reader_results(reference_page);
                print(result)
                results.append(result)
            return results
        PageReader.config['schema'] = self.config['schema']
        PageReader.config['host'] = self.config['host']
        final_results = PageReader.analyze_page()
        if top_level == True:
            final_results = [final_results]
        return final_results

# Load up the config and run the site scrape!
site_scaper = SiteScraper()
site_scaper.load_config('./config.json')
results = site_scaper.run_scrape()
