import re
from nltk.tokenize import TreebankWordTokenizer
from nltk.stem import PorterStemmer, RSLPStemmer
from nltk.corpus import stopwords
from unidecode import unidecode

class TextPreprocessor:
    def __init__(self):
        self.tokenizer = TreebankWordTokenizer()
        self.stopwords = set(stopwords.words('english') + stopwords.words('portuguese'))
        self.stemmer_pt = RSLPStemmer()
        self.stemmer_en = PorterStemmer()
        
    def preprocess(self, text):
        """Processa texto em 5 etapas: normalização, limpeza, tokenização, stemming e reconstrução"""
        # Etapa 1: Normalização (acentos, maiúsculas)
        text = unidecode(text.lower())
        
        # Etapa 2: Limpeza (pontuação, números)
        text = re.sub(r'[^\w\s]', '', text)
        text = re.sub(r'\d+', '', text)
        
        # Etapa 3: Tokenização
        tokens = self.tokenizer.tokenize(text)
        
        # Etapa 4: Remoção de stopwords e stemming
        processed_tokens = []
        for token in tokens:
            if token not in self.stopwords:
                try:
                    processed_tokens.append(self.stemmer_pt.stem(token))
                except:
                    processed_tokens.append(self.stemmer_en.stem(token))
        
        # Etapa 5: Reconstrução do texto
        return ' '.join(processed_tokens)
