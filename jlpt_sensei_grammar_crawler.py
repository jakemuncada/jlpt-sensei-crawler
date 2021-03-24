"""
Script to download the grammar lessons of JLPT Sensei.
"""

import os
import json
import threading
from queue import Queue
from time import sleep
from common import fetchPage
from grammar_pattern import GrammarPattern


class JlptSenseiGrammarCrawler:
    """
    Class that can download the grammar lessons of JLPT Sensei.
    """

    WORKER_NUM = 5

    def __init__(self, level, directory):
        if level < 1 or level > 5:
            raise ValueError(f'Invalid JLPT Level: {level}')

        self.level = level
        self.grammarList = []
        self.directory = directory
        self.killEvent = threading.Event()

    def download(self):
        """
        Download the grammar lessons.
        """

        print(f'Starting N{self.level} grammar download...')

        urls = self.getListUrls()
        self.grammarList = self._getGrammarList(urls)

        queue = Queue()
        for item in self.grammarList:
            queue.put(item)

        if self.killEvent.is_set():
            return

        print(f'Starting {JlptSenseiGrammarCrawler.WORKER_NUM} threads...')

        threads = []
        for _ in range(JlptSenseiGrammarCrawler.WORKER_NUM):
            t = threading.Thread(target=self.work, args=(queue,))
            threads.append(t)
            t.start()

        while not queue.empty():
            sleep(0.3)
            if self.killEvent.is_set():
                break

        for thread in threads:
            thread.join()

    def stop(self):
        """
        Stop downloading.
        """
        self.killEvent.set()

    def work(self, queue):
        """
        The main work of each thread.
        """
        while not queue.empty():
            if self.killEvent.is_set():
                return
            item = queue.get()
            item.fetch()
            if queue.qsize() > 0 and queue.qsize() % 10 == 0:
                print(f'Remaining items to be processed: {queue.qsize()}')
            queue.task_done()

    def getListUrls(self):
        """
        Get the URLs of the grammar list pagination links.
        """
        url = f'https://jlptsensei.com/jlpt-n{self.level}-grammar-list/'
        soup = fetchPage(url)
        if soup is None:
            return []

        urls = set()
        urls.add(f'https://jlptsensei.com/jlpt-n{self.level}-grammar-list/page/1/')

        nav = soup.find('nav', 'pagination-wrap')
        aTags = nav.find_all('a', 'page-numbers')

        for aTag in aTags:
            urls.add(aTag.attrs['href'])

        return sorted(list(urls))

    def _getGrammarList(self, urls):
        """
        Get the list of grammar patterns.

        Parameters:
            urls (list of str): The URLs of each page of the grammar list.
        """
        grammarList = []

        for url in urls:
            if self.killEvent.is_set():
                return []

            print(f'Fetching grammar patterns from {url}...')

            soup = fetchPage(url)
            if soup is None:
                continue

            try:
                table = soup.find(id='jl-grammar')
                rows = table.find_all('tr', 'jl-row')
            except Exception as err:  # pylint: disable=broad-except
                print(f'Failed to parse grammar table from {url}, {err}')
                continue

            for row in rows:
                if self.killEvent.is_set():
                    return []

                item = GrammarPattern.fromRow(self.level, row)
                if item is not None:
                    grammarList.append(item)

        grammarList = sorted(grammarList, key=lambda item: item.num)

        print(f'Successfully initialized {len(grammarList)} grammar patterns.')
        return grammarList

    def save(self):
        """
        Save the grammar list as a JSON file.
        """
        grammarList = [item.toDict() for item in self.grammarList]

        os.makedirs(self.directory, exist_ok=True)
        filePath = os.path.join(self.directory, f'grammar-n{self.level}.json')

        with open(filePath, 'w', encoding='utf-8') as outputFile:
            jsonStr = json.dumps(grammarList, indent=4)
            outputFile.write(jsonStr)
            print('Saved grammar list.')


if __name__ == '__main__':
    try:
        crawler = JlptSenseiGrammarCrawler(3, './output')
        crawler.download()
        crawler.save()

    except KeyboardInterrupt:
        print('Please wait while threads are being stopped...')
        crawler.stop()
