from lxml import html
import requests

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
            results[key].append(tree.xpath(xpathString + '/text()'))
        return results

pageReader = PageReader()
content = pageReader.getPage()
results = pageReader.getXPathResults(content)
print(results)
