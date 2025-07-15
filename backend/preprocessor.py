import re
from nltk.tokenize import TreebankWordTokenizer
from nltk.corpus import stopwords
from nltk.stem import RSLPStemmer, PorterStemmer
from unidecode import unidecode

class TextPreprocessor:
    def __init__(self):
        self.tokenizer = TreebankWordTokenizer()
        self.stopwords = set(stopwords.words('english') + stopwords.words('portuguese'))
        self.stemmer_pt = RSLPStemmer()
        self.stemmer_en = PorterStemmer()
        
    def preprocess(self, text):
        text = unidecode(text.lower())
        text = re.sub(r'[^\w\s]', '', text)
        text = re.sub(r'\d+', '', text)
        tokens = self.tokenizer.tokenize(text)
        processed_tokens = []
        for token in tokens:
            if token not in self.stopwords:
                try:
                    processed_tokens.append(self.stemmer_pt.stem(token))
                except:
                    processed_tokens.append(self.stemmer_en.stem(token))
        return ' '.join(processed_tokens)