from lxml import html
import requests
import re

# Reads individual web pages and analyzes them based on config info
class PageReader:
    # page and xpath info, see config.json
    config = None

    # Main public function to analyze a page based on config
    def analyze_page():
        page_reader = PageReader()
        content = page_reader._get_page()
        results = page_reader._get_xpath_results(content)
        return page_reader._analyze_results(results)

    # Fetches page content via an HTTP request
    def _get_page(self) :
        url = (self.config['schema'] + '://' + self.config['host']
            + '/' + self.config['path'])
        page_request = requests.get(url)
        return page_request.content

    # Runs an xpath query on page content and returns the results
    def _get_xpath_results(self, page_content):
        tree = html.fromstring(page_content);
        results = {}
        for key, target_data in self.config['targets'].items():
            if not key in results:
                results[key] = []
            xpath_results = tree.xpath(target_data['xpath'])
            results[key] = results[key] + xpath_results
        return results

    # Strategy pattern function that calls the analyze strategy found in
    # the config. Prints an error if the function cannot be found
    def _analyze_results(self, results):
        analyzed = {};
        for key, data in results.items():
            func = self._get_analyze_strategy(key)
            try:
                analyzed[key] = getattr(self, func)(data, key)
            except AttributeError:
                print('Expected function ' + func + ' does not exist')
        return analyzed

    # Gets instances of the full text value (lowercased)
    def _analyze_full_text(self, data, key):
        counts = {}
        for text in data:
            counts = self._add_phrase_count(counts, text.lower())
        return counts

    # Gets instances of a link
    def _analyze_link(self, data, key):
        counts = {}
        for text in data:
            counts = self._add_phrase_count(counts, text)
        return counts

    # Gets instances of individual words (lowercased), optionally
    # using a whitelist (only returns words found the the whitelist)
    def _analyze_words(self, data, key):
        counts = {};
        use_whitelist = self._has_whitelist(key)
        if (use_whitelist):
            whitelist = self.config['targets'][key]['whitelist']
        for text in data:
            words = text.split()
            for word in words:
                word = re.sub(r"[^a-z\+#]", "", word.lower())
                if (use_whitelist):
                    try:
                        whitelist.index(word)
                        counts = self._add_phrase_count(counts, word)
                    except ValueError:
                        pass
                else:
                    counts = self._add_phrase_count(counts, word)
        return counts

    # Helper function to increment the count of a phrase, adding the
    # key to the counts dict if it doesn't exist
    def _add_phrase_count(self, counts, phrase):
        if not phrase in counts:
            counts[phrase] = 0
        counts[phrase] += 1
        return counts

    # Helper function to determine if a target uses a whitelist
    def _has_whitelist(self, key):
        return not self.config['targets'][key]['whitelist'] is None

    # Helper function to get the function name of the analyze strategy
    def _get_analyze_strategy(self, target_key):
        analyze_type = self.config['targets'][target_key]['type']
        return '_analyze_' + analyze_type
