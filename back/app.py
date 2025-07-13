import os
import re
import json
import pickle
import numpy as np
import random
from datetime import datetime
from flask import Flask, request, jsonify, session
from nltk.tokenize import TreebankWordTokenizer
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, RSLPStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from unidecode import unidecode
from flask_cors import CORS
from fuzzywuzzy import fuzz
from exemplosPerguntas import bancoDePerguntas

# Configuração inicial do Flask
app = Flask(__name__)
app.secret_key = 'estigma'
CORS(
    app,
    supports_credentials=True,
    origins=["http://localhost:3000"],
    methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"]
)

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

# =============================================
# 2. MÓDULO DE DADOS E CONHECIMENTO
# =============================================
class KnowledgeBase:
    def __init__(self, data_file='filmes.json'):
        self.data_file = data_file
        self.filmes = self.load_data()
        self.corpus = self.build_corpus()
        
    def load_data(self):
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
                },
                {
                    "titulo": "Pokémon: Detective Pikachu",
                    "diretor": ["Rob Letterman"],
                    "atores": ["Ryan Reynolds", "Justice Smith", "Kathryn Newton"],
                    "ano": 2019,
                    "genero": ["Ação", "Aventura", "Fantasia"]
                }
            ]
    
    def build_corpus(self):
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
        for filme in self.filmes:
            if filme['titulo'].lower() == titulo.lower():
                return filme
        return None

# =============================================
# 3. MÓDULO DE PROCESSAMENTO DE PERGUNTAS (APRIMORADO)
# =============================================
class EnhancedQAEngine:
    def __init__(self, knowledge_base):
        self.kb = knowledge_base
        self.preprocessor = TextPreprocessor()
        self.vectorizer = TfidfVectorizer()
        self.tfidf_matrix = self.vectorizer.fit_transform([self.preprocessor.preprocess(doc) for doc in self.kb.corpus])
        self.banco_de_perguntas = bancoDePerguntas
        self.padroes_perguntas = self._construir_padroes()
        self.sinonimos = {
            'diretor': ['dirigiu', 'realizador', 'criou'],
            'ator': ['elenco', 'estrela', 'protagonista'],
            'genero': ['categoria', 'tipo', 'estilo']
        }
    
    def _construir_padroes(self):
        padroes = {
            'diretor': [],
            'ator': [],
            'genero': [],
            'ano': [],
            'geral': []
        }
        for item in self.banco_de_perguntas:
            for tipo in item['tipo']:
                padroes[tipo].append(item['pergunta'])
        return padroes

    def expand_synonyms(self, text):
        for termo, lista_sinonimos in self.sinonimos.items():
            for sinonimo in lista_sinonimos:
                text = text.replace(sinonimo, termo)
        return text
    
    def find_most_similar(self, processed_question):
        try:
            question_vec = self.vectorizer.transform([processed_question])
            similarities = cosine_similarity(question_vec, self.tfidf_matrix)
            most_similar_idx = np.argmax(similarities)
            score = similarities[0][most_similar_idx]
            
            if score < 0.3 and 'ultimo_filme' in session:
                last_film = session['ultimo_filme']
                if last_film in [f['titulo'] for f in self.kb.filmes]:
                    return last_film, 0.5
                
            return self.kb.filmes[most_similar_idx]['titulo'], score
        except Exception as e:
            print(f"Erro em find_most_similar: {str(e)}")
            raise
    
    def identificar_tipo_pergunta(self, pergunta):
        pergunta = pergunta.lower()
        
        # Verifica correspondência com perguntas conhecidas
        for tipo, perguntas in self.padroes_perguntas.items():
            for pergunta_conhecida in perguntas:
                if fuzz.ratio(pergunta, pergunta_conhecida.lower()) > 70:
                    return tipo if tipo != 'geral' else self.identify_question_type(pergunta)
                
        return self.identify_question_type(pergunta)
    
    def identify_question_type(self, question):
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
    
    def gerar_resposta_avancada(self, filme, question_type):
        templates = {
            'diretor': [
                f"O diretor de {filme['titulo']} é {', '.join(filme['diretor'])}.",
                f"{filme['titulo']} foi dirigido por {', '.join(filme['diretor'])}."
            ],
            'ator': [
                f"No elenco de {filme['titulo']} temos: {', '.join(filme['atores'])}.",
                f"Os atores principais são {', '.join(filme['atores'])}."
            ],
            'genero': [
                f"{filme['titulo']} é do gênero: {', '.join(filme['genero'])}.",
                f"Classificado como: {', '.join(filme['genero'])}."
            ],
            'ano': [
                f"Foi lançado em {filme['ano']}.",
                f"Ano de lançamento: {filme['ano']}."
            ]
        }
        
        if isinstance(question_type, list):
            respostas = []
            for qt in question_type:
                if qt in templates:
                    respostas.append(random.choice(templates[qt]))
                else:
                    respostas.append(self.generate_answer(filme, qt))
            return " ".join(respostas)
        elif question_type in templates:
            return random.choice(templates[question_type])
        else:
            return self.generate_answer(filme, question_type)
    
    def generate_answer(self, filme, question_type):
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
qa_engine = EnhancedQAEngine(kb)

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
        pergunta_processada = qa_engine.preprocessor.preprocess(pergunta)
        pergunta_processada = qa_engine.expand_synonyms(pergunta_processada)
        
        titulo_filme, score = qa_engine.find_most_similar(pergunta_processada)
        
        if score < 0.2:
            return jsonify({'resposta': "Não tenho informações suficientes sobre esse filme."})
        
        filme = kb.get_filme(titulo_filme)
        if not filme:
            return jsonify({'resposta': "Filme não encontrado na base de dados."})
        
        question_type = qa_engine.identificar_tipo_pergunta(pergunta)
        resposta = qa_engine.gerar_resposta_avancada(filme, question_type)

        session['ultimo_filme'] = titulo_filme
        
        return jsonify({
            'pergunta': pergunta,
            'resposta': resposta,
            'filme': titulo_filme,
            'score': float(score),
            'ultimo_filme': session.get('ultimo_filme')
        })
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@app.route('/debug_sessao', methods=['GET'])
def debug_sessao():
    return jsonify({
        'session_id': session.sid,
        'ultimo_filme': session.get('ultimo_filme'),
        'todos_dados': dict(session)
    })

if __name__ == '__main__':
    import nltk
    nltk.download('stopwords')
    app.run(debug=True)