"""
A single grammar item.
"""

import json
from common import fetchPage


class GrammarPattern:
    """
    A single grammar item.
    """

    def __init__(self, level, pageUrl, num, eng, jap, meaning, usage,
                 notes, flashcardUrl, flashcardFilepath, sampleSentences):
        self.level = level
        self.pageUrl = pageUrl
        self.num = num
        self.eng = eng
        self.jap = jap
        self.meaning = meaning
        self.usage = usage
        self.notes = notes
        self.flashcardUrl = flashcardUrl
        self.flashcardFilepath = flashcardFilepath
        self.sampleSentences = sampleSentences

    @classmethod
    def fromRow(cls, level, rowElement):
        """
        Instantiate a GrammarPattern from the given row of the grammar list.

        Parameters:
            level (int): The JLPT level. Should be between 1 and 5 inclusive.
            rowElement (BeautifulSoup): The row element of the grammar item.

        Returns:
            The instantiated GrammarPattern. None if the parsing failed.
        """
        try:
            num = int(rowElement.find('td', 'jl-td-num').text.strip())
            pageUrl = rowElement.find('a', 'jl-link').attrs['href']
            eng = rowElement.find('td', 'jl-td-gr').get_text().strip()
            jap = rowElement.find('td', 'jl-td-gj').get_text().strip()
            meaning = rowElement.find('td', 'jl-td-gm').get_text().strip()
            return cls(level, pageUrl, num, eng, jap, meaning, None, None, None, None, None)
        except Exception as err:  # pylint: disable=broad-except
            print(f'Failed to parse grammar pattern from {rowElement}, {err}')
            return None

    def fetch(self):
        """
        Fetch the grammar pattern details.
        """
        soup = fetchPage(self.pageUrl)
        if soup is None:
            return

        self.usage = self._parseUsage(soup)
        self.flashcardUrl = self._parseFlashcardUrl(soup)
        self.notes = self._parseNotes(soup)
        self.sampleSentences = self._parseSampleSentences(soup)

    def _parseUsage(self, soup):
        """
        Parse the usage from the page soup.
        """
        try:
            table = soup.find('table', 'usage')
            return table
        except Exception as err:  # pylint: disable=broad-except
            print(f'Failed to parse usage of N{self.level} grammar pattern',
                  f'#{self.num} ({self.eng}), {err}')
            return None

    def _parseFlashcardUrl(self, soup):
        """
        Parse the flashcard image URL from the page soup.
        """
        try:
            img = soup.find(id='header-image')
            src = img.attrs['src']
            return src
        except Exception as err:  # pylint: disable=broad-except
            print(f'Failed to parse flashcard image URL of N{self.level} grammar pattern',
                  f'#{self.num} ({self.eng}), {err}')
            return None

    def _parseNotes(self, soup):
        """
        Parse the notes from the page soup.
        """
        try:
            notes = soup.find('div', 'grammar-notes')
            return notes
        except Exception as err:  # pylint: disable=broad-except
            print(f'Failed to parse notes of N{self.level} grammar pattern',
                  f'#{self.num} ({self.eng}), {err}')
            return None

    def _parseSampleSentences(self, soup):
        """
        Parse the sample sentences from the page soup.
        """

        try:
            samples = soup.find_all('div', 'example-cont')
        except Exception as err:  # pylint: disable=broad-except
            print(f'Failed to parse sample sentences of N{self.level} grammar pattern',
                  f'#{self.num} ({self.eng}), {err}')
            return None

        result = []
        for idx, sample in enumerate(samples):
            try:
                main = sample.find('div', 'example-main')
                furi = sample.find('div', 'alert-success')
                meaning = sample.find('div', 'alert-primary')
                result.append((main, furi, meaning))
            except Exception as err:  # pylint: disable=broad-except
                print(f'Failed to parse sample sentence #{idx+1} of N{self.level} grammar pattern',
                      f'#{self.num} ({self.eng}), {err}')

        return result

    def toDict(self):
        """
        Returns the dictionary representation of the GrammarPattern.
        """
        sentences = []
        for sentence in self.sampleSentences:
            obj = {
                'main': str(sentence[0]),
                'furi': str(sentence[1]),
                'meaning': str(sentence[2])
            }
            sentences.append(obj)

        result = {
            'level': self.level,
            'pageUrl': self.pageUrl,
            'num': self.num,
            'eng': self.eng,
            'jap': self.jap,
            'meaning': self.meaning,
            'usage': str(self.usage),
            'notes': str(self.notes),
            'flashcardUrl': self.flashcardUrl,
            'flashcardFilepath': self.flashcardFilepath,
            'sampleSentences': sentences
        }
        return result

    def __str__(self):
        return f'{self.num}: {self.eng} : {self.jap} : {self.meaning}'
