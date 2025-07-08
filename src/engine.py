import numpy as np
from src.text_preprocessor import TextPreprocessor
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

class QAEngine:
    def __init__(self, knowledge_base):
        self.kb = knowledge_base
        self.preprocessor = TextPreprocessor()
        self.vectorizer = TfidfVectorizer()
        self.tfidf_matrix = self.vectorizer.fit_transform([self.preprocessor.preprocess(doc) for doc in self.kb.corpus])
        
        # Configuração de sinônimos
        self.sinonimos = {
            'diretor': ['dirigiu', 'realizador', 'criou'],
            'ator': ['elenco', 'estrela', 'protagonista'],
            'genero': ['categoria', 'tipo', 'estilo']
        }
    
    def expand_synonyms(self, text):
        """Substitui sinônimos por termos canônicos"""
        for termo, lista_sinonimos in self.sinonimos.items():
            for sinonimo in lista_sinonimos:
                text = text.replace(sinonimo, termo)
        return text
    
    def find_most_similar(self, processed_question):
        """Encontra o filme mais relevante usando similaridade de cosseno"""
        question_vec = self.vectorizer.transform([processed_question])
        similarities = cosine_similarity(question_vec, self.tfidf_matrix)
        most_similar_idx = np.argmax(similarities)
        return self.kb.filmes[most_similar_idx]['titulo'], similarities[0][most_similar_idx]
    
    def identify_question_type(self, question):
        """Identifica o tipo de informação solicitada"""
        question = question.lower()
        patterns = {
            'diretor': r'diretor|dirigiu|realizador',
            'ator': r'ator|atriz|elenco|estrela',
            'genero': r'gênero|genero|tipo|estilo',
            'ano': r'ano|lançamento|lançou',
            'sinopse': r'sinopse|resumo|enredo'
        }
        
        for qtype, pattern in patterns.items():
            if re.search(pattern, question):
                return qtype
        return 'geral'
    
    def generate_answer(self, filme, question_type):
        """Gera resposta baseada no tipo de pergunta"""
        answers = {
            'diretor': f"O diretor de {filme['titulo']} é {', '.join(filme['diretor'])}.",
            'ator': f"Os atores principais de {filme['titulo']} são: {', '.join(filme['atores'])}.",
            'genero': f"O gênero de {filme['titulo']} é: {', '.join(filme['genero'])}.",
            'ano': f"O filme {filme['titulo']} foi lançado em {filme['ano']}.",
            'geral': f"Sobre {filme['titulo']}: Diretor(es): {', '.join(filme['diretor'])}, Ano: {filme['ano']}, Gênero: {', '.join(filme['genero'])}"
        }
        return answers.get(question_type, "Não consegui entender sua pergunta.")
