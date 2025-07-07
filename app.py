import os
import re
import json
import pickle
import numpy as np
from datetime import datetime
from flask import Flask, request, jsonify
from nltk.tokenize import TreebankWordTokenizer
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, RSLPStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from unidecode import unidecode

# Configuração inicial do Flask
app = Flask(__name__)

# =============================================
# 1. MÓDULO DE PRÉ-PROCESSAMENTO
# =============================================
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

# =============================================
# 2. MÓDULO DE DADOS E CONHECIMENTO
# =============================================
class KnowledgeBase:
    def __init__(self, data_file='filmes.json'):
        self.data_file = data_file
        self.filmes = self.load_data()
        self.corpus = self.build_corpus()
        
    def load_data(self):
        """Carrega dados de filmes do arquivo JSON"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return [
                {
                    "titulo": "Matrix",
                    "diretor": ["Lana Wachowski", "Lilly Wachowski"],
                    "atores": ["Keanu Reeves", "Laurence Fishburne", "Carrie-Anne Moss"],
                    "ano": 1999,
                    "genero": ["Ficção científica", "Ação"]
                }
            ]
    
    def build_corpus(self):
        """Constrói corpus para TF-IDF combinando informações dos filmes"""
        corpus = []
        for filme in self.filmes:
            text_parts = [
                filme['titulo'],
                ' '.join(filme['diretor']),
                ' '.join(filme['atores']),
                str(filme['ano']),
                ' '.join(filme['genero'])
            ]
            corpus.append(' '.join(text_parts))
        return corpus
    
    def get_filme(self, titulo):
        """Busca filme por título (case insensitive)"""
        for filme in self.filmes:
            if filme['titulo'].lower() == titulo.lower():
                return filme
        return None

# =============================================
# 3. MÓDULO DE PROCESSAMENTO DE PERGUNTAS
# =============================================
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

# =============================================
# 4. INICIALIZAÇÃO DO SISTEMA
# =============================================
kb = KnowledgeBase()
qa_engine = QAEngine(kb)

# =============================================
# 5. ROTAS DA API
# =============================================
@app.route('/perguntar', methods=['POST'])
def responder():
    data = request.get_json()
    
    if not data or 'pergunta' not in data:
        return jsonify({'erro': 'Campo "pergunta" é obrigatório'}), 400
    
    pergunta = data['pergunta']
    
    try:
        # Pré-processamento
        pergunta_processada = qa_engine.preprocessor.preprocess(pergunta)
        pergunta_processada = qa_engine.expand_synonyms(pergunta_processada)
        
        # Identificação do filme
        titulo_filme, score = qa_engine.find_most_similar(pergunta_processada)
        
        if score < 0.2:
            return jsonify({'resposta': "Não tenho informações suficientes sobre esse filme."})
        
        # Obtenção da resposta
        filme = kb.get_filme(titulo_filme)
        if not filme:
            return jsonify({'resposta': "Filme não encontrado na base de dados."})
        
        question_type = qa_engine.identify_question_type(pergunta)
        resposta = qa_engine.generate_answer(filme, question_type)
        
        return jsonify({
            'pergunta': pergunta,
            'resposta': resposta,
            'filme': titulo_filme,
            'score': float(score)
        })
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

if __name__ == '__main__':
    # Baixar recursos do NLTK (executar apenas na primeira vez)
    import nltk
    nltk.download('stopwords')
    app.run(debug=True)
