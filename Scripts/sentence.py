import re
import string

class Sentence:
    def __init__(self, content, startt, endt):
        self.content = content
        self.startt = startt
        self.endt = endt        
        for c in string.punctuation:
            content = content.replace(c, '')
        self.words = re.split(r'\s', content)
        
    def numwords(self):
        return len(words)