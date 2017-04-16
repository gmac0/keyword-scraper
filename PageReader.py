from lxml import html
import requests
import operator
import re

class PageReader:

    # page and xpath info, move to a separate config file at some point
    # for easy modification and extension
    config = {
        'host': 'weworkremotely.com',
        'schema': 'https',
        'path': 'categories/2-programming/jobs#intro',
        'targets': {
            'company': {
                'xpath': '//*[@id="category-2"]/article/ul/li[*]/a/span[1]',
                'type': 'full_text'
            },
            'title': {
                'xpath': '//*[@id="category-2"]/article/ul/li[*]/a/span[2]',
                'type': 'words',
                'whitelist': [
                    'php',
                    'typescript',
                    'javascript',
                    'angular',
                    'ruby',
                    'java ',
                    'rails',
                    'node',
                    'go',
                    'python',
                    'react',
                    'c',
                    'c++',
                    'c#'
                ]
            }
        }
    }

    def get_page(self) :
        url = (self.config['schema'] + '://' + self.config['host']
            + '/' + self.config['path'])
        page_request = requests.get(url)
        return page_request.content

    def get_xpath_results(self, page_content):
        tree = html.fromstring(page_content);
        results = {}
        for key, target_data in self.config['targets'].items():
            if not key in results:
                results[key] = []
            xpath_results = tree.xpath(target_data['xpath'] + '/text()')
            results[key] = results[key] + xpath_results
        return results

    def analyze_results(self, results):
        for key, data in results.items():
            func = self.get_analyze_strategy(key)
            try:
                getattr(self, func)(data, key)
            except AttributeError:
                print('Expected function ' + func + ' does not exist')

    def analyze_full_text(self, data, key):
        counts = {}
        for text in data:
            counts = self.add_phrase_count(counts, text)
        counts_sorted = sorted(
            counts.items(),
            key=operator.itemgetter(1),
            reverse=True
        )
        for text, count in counts_sorted:
            print(str(count) + ' ' + text)

    def analyze_words(self, data, key):
        counts = {};
        use_whitelist = self.has_whitelist(key)
        if (use_whitelist):
            whitelist = self.config['targets'][key]['whitelist']
        for text in data:
            words = text.split()
            for word in words:
                word = re.sub(r"[^a-z\+#]", "", word.lower())
                if (use_whitelist):
                    try:
                        whitelist.index(word)
                        counts = self.add_phrase_count(counts, word)
                    except ValueError:
                        pass
                else:
                    counts = self.add_phrase_count(counts, word)
        counts_sorted = sorted(
            counts.items(),
            key=operator.itemgetter(1),
            reverse=True
        )
        for target, count in counts_sorted:
            print(str(count) + ' ' + target)

    def add_phrase_count(self, counts, word):
        if not word in counts:
            counts[word] = 0
        counts[word] += 1
        return counts

    def has_whitelist(self, key):
        return not self.config['targets'][key]['whitelist'] is None

    def get_analyze_strategy(self, target_key):
        analyze_type = self.config['targets'][target_key]['type']
        return 'analyze_' + analyze_type

page_reader = PageReader()
content = page_reader.get_page()
results = page_reader.get_xpath_results(content)
analyzed = page_reader.analyze_results(results)
