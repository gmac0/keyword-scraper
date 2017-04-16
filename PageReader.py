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
                'type': 'fullText'
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

    def getPage(self) :
        url = (self.config['schema'] + '://' + self.config['host']
            + '/' + self.config['path'])
        pageRequest = requests.get(url)
        return pageRequest.content

    def getXPathResults(self, pageContent):
        tree = html.fromstring(pageContent);
        results = {}
        pathsDict = self.config['xpath']
        for key, xpathString in pathsDict.items():
            if not key in results:
                results[key] = []
            xpathResults = tree.xpath(xpathString + '/text()')
            results[key] = results[key] + xpathResults
        return results

    def getXPathResults(self, pageContent):
        tree = html.fromstring(pageContent);
        results = {}
        for key, targetData in self.config['targets'].items():
            if not key in results:
                results[key] = []
            xpathResults = tree.xpath(targetData['xpath'] + '/text()')
            results[key] = results[key] + xpathResults
        return results

    def analyzeResults(self, results):
        for key, data in results.items():
            func = self.getAnalyzeStrategy(key)
            try:
                getattr(self, func)(data, key)
            except AttributeError:
                print('Expected function ' + func + ' does not exist')

    def analyzeFullText(self, data, key):
        counts = {}
        for text in data:
            counts = self.addPhraseCount(counts, text)
        countsSorted = sorted(
            counts.items(),
            key=operator.itemgetter(1),
            reverse=True
        )
        for text, count in countsSorted:
            print(str(count) + ' ' + text)

    def analyzeWords(self, data, key):
        counts = {};
        useWhitelist = self.hasWhitelist(key)
        if (useWhitelist):
            whitelist = self.config['targets'][key]['whitelist']
        for text in data:
            words = text.split()
            for word in words:
                word = re.sub(r"[^a-z\+#]", "", word.lower())
                if (useWhitelist):
                    try:
                        whitelist.index(word)
                        counts = self.addPhraseCount(counts, word)
                    except ValueError:
                        pass
                else:
                    counts = self.addPhraseCount(counts, word)
        countsSorted = sorted(
            counts.items(),
            key=operator.itemgetter(1),
            reverse=True
        )
        for target, count in countsSorted:
            print(str(count) + ' ' + target)

    def addPhraseCount(self, counts, word):
        if not word in counts:
            counts[word] = 0
        counts[word] += 1
        return counts

    def hasWhitelist(self, key):
        return not self.config['targets'][key]['whitelist'] is None

    def getAnalyzeStrategy(self, targetKey):
        analyzeType = self.config['targets'][targetKey]['type']
        analyzeType = analyzeType[0].upper() + analyzeType[1:]
        return 'analyze' + analyzeType

pageReader = PageReader()
content = pageReader.getPage()
results = pageReader.getXPathResults(content)
analyzed = pageReader.analyzeResults(results)
