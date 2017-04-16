from lxml import html
import requests
import re

class PageReader:

    # page and xpath info, see config.json
    config = None

    def analyze_page():
        page_reader = PageReader()
        content = page_reader._get_page()
        results = page_reader._get_xpath_results(content)
        return page_reader._analyze_results(results)

    def _get_page(self) :
        url = (self.config['schema'] + '://' + self.config['host']
            + '/' + self.config['path'])
        page_request = requests.get(url)
        return page_request.content

    def _get_xpath_results(self, page_content):
        tree = html.fromstring(page_content);
        results = {}
        for key, target_data in self.config['targets'].items():
            if not key in results:
                results[key] = []
            xpath_results = tree.xpath(target_data['xpath'] + '/text()')
            results[key] = results[key] + xpath_results
        return results

    def _analyze_results(self, results):
        analyzed = {};
        for key, data in results.items():
            func = self._get_analyze_strategy(key)
            try:
                analyzed[key] = getattr(self, func)(data, key)
            except AttributeError:
                print('Expected function ' + func + ' does not exist')
        return analyzed

    def _analyze_full_text(self, data, key):
        counts = {}
        for text in data:
            counts = self._add_phrase_count(counts, text)
        return counts

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

    def _add_phrase_count(self, counts, word):
        if not word in counts:
            counts[word] = 0
        counts[word] += 1
        return counts

    def _has_whitelist(self, key):
        return not self.config['targets'][key]['whitelist'] is None

    def _get_analyze_strategy(self, target_key):
        analyze_type = self.config['targets'][target_key]['type']
        return '_analyze_' + analyze_type
