from lxml import html
import requests
import operator

class PageReader:

    # page and xpath info, move to a separate config file at some point
    # for easy modification and extension
    config = {
        'host': 'weworkremotely.com',
        'schema': 'https',
        'path': 'categories/2-programming/jobs#intro',
        'xpath': {
            'company': '//*[@id="category-2"]/article/ul/li[*]/a/span[1]',
            'title': '//*[@id="category-2"]/article/ul/li[*]/a/span[2]'
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

    def analyzeResults(self, results):
        for key, data in results.items():
            func = 'analyze' + key.title()
            try:
                getattr(self, func)(data)
            except AttributeError:
                print('Expected function ' + func + ' does not exist')

    def analyzeCompany(self, data):
        companyCounts = {}
        for company in data:
            if not company in companyCounts:
                companyCounts[company] = 0
            companyCounts[company] += 1
        companyCountsSorted = sorted(
            companyCounts.items(),
            key=operator.itemgetter(1),
            reverse=True
        )
        for company, count in companyCountsSorted:
            print(str(count) + ' ' + company)

    def analyzeTitle(self, data):
        targets = [
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
            'react'
        ];
        targetCounts = {};
        for target in targets:
            targetCounts[target] = 0
        for title in data:
            for target in targets:
                if (title.lower().find(target) != -1):
                    targetCounts[target] += 1
        targetCountsSorted = sorted(
            targetCounts.items(),
            key=operator.itemgetter(1),
            reverse=True
        )
        for target, count in targetCountsSorted:
            print(str(count) + ' ' + target)


pageReader = PageReader()
content = pageReader.getPage()
results = pageReader.getXPathResults(content)
analyzed = pageReader.analyzeResults(results)
# print(results)
