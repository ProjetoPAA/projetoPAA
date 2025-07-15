import re
import random
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from fuzzywuzzy import fuzz
from flask import session
from preprocessor import TextPreprocessor

class EnhancedQAEngine:
    def __init__(self, knowledge_base):
        self.kb = knowledge_base
        self.preprocessor = TextPreprocessor()
        self.vectorizer = TfidfVectorizer()
        self.tfidf_matrix = self.vectorizer.fit_transform([self.preprocessor.preprocess(doc) for doc in self.kb.corpus])
        self.banco_de_perguntas = banco_de_perguntas
        self.padroes_perguntas = self._construir_padroes()
        self.sinonimos = {
            'diretor': ['dirigiu', 'realizador', 'criou','idealizador', 'criador', 'direção', 'diretora', 'diretores', 'dirigido'],
            'ator': ['elenco', 'estrela', 'protagonista', 'atores', 'atriz', 'elenco'],
            'genero': ['categoria', 'tipo', 'estilo', 'tema', 'característica', 'ação', 'aventura', 'ficção científica', 'fantasia', 'terror', 'comédia'],
            'ano': ['lançamento', 'estreia', 'data', 'quando', 'lançou', 'lançado'],
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
            
            if score < 0.2 and 'ultimo_filme' in session:
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
            'geral': f"Sobre {filme['titulo']}: Diretor(es): {', '.join(filme['diretor'])}, Ano: {filme['ano']}, Gênero: {', '.join(filme['genero'])}",
            'sinopse': f"A sinopse de {filme['titulo']} é: {filme['sinopse']}."
        }
        return answers.get(question_type, "Não consegui entender sua pergunta.")


banco_de_perguntas = [
    # Perguntas sobre direção
    {"pergunta": "Quem é o diretor de Iron Man?", "tipo": ["diretor"]},
    {"pergunta": "Quem dirigiu The Avengers?", "tipo": ["diretor"]},
    {"pergunta": "De quem foi a direção de The Dark Knight?", "tipo": ["diretor"]},
    {"pergunta": "Qual o nome do diretor de Logan?", "tipo": ["diretor"]},
    {"pergunta": "Quem fez a direção de Joker?", "tipo": ["diretor"]},
    {"pergunta": "Diretor do filme Black Panther?", "tipo": ["diretor"]},
    {"pergunta": "Quem está creditado como diretor em Alita: Battle Angel?", "tipo": ["diretor"]},
    {"pergunta": "Quem realizou a direção de Guardians of the Galaxy?", "tipo": ["diretor"]},
    {"pergunta": "Nome do diretor responsável por The Batman?", "tipo": ["diretor"]},
    {"pergunta": "Quem comandou a direção de Scott Pilgrim vs. the World?", "tipo": ["diretor"]},
    {"pergunta": "Quem assina a direção de Man of Steel?", "tipo": ["diretor"]},
    {"pergunta": "Direção de Deadpool?", "tipo": ["diretor"]},
    {"pergunta": "Quem esteve à frente da direção de Warcraft?", "tipo": ["diretor"]},
    {"pergunta": "Quem dirigiu o filme X-Men?", "tipo": ["diretor"]},
    {"pergunta": "Quem ficou responsável pela direção de Shazam!?", "tipo": ["diretor"]},

    # Perguntas sobre elenco
    {"pergunta": "Quem são os atores principais de The Avengers?", "tipo": ["ator"]},
    {"pergunta": "Qual o elenco de Guardians of the Galaxy?", "tipo": ["ator"]},
    {"pergunta": "Quem atua em The Dark Knight?", "tipo": ["ator"]},
    {"pergunta": "Atores principais de Suicide Squad (2016)?", "tipo": ["ator"]},
    {"pergunta": "Quem está no elenco de Justice League?", "tipo": ["ator"]},
    {"pergunta": "Protagonistas de Men in Black?", "tipo": ["ator"]},
    {"pergunta": "Quem são os atores de X-Men?", "tipo": ["ator"]},
    {"pergunta": "Elenco principal de The Batman?", "tipo": ["ator"]},
    {"pergunta": "Quem faz o papel principal em Deadpool?", "tipo": ["ator"]},
    {"pergunta": "Atores que participam de Black Panther?", "tipo": ["ator"]},
    {"pergunta": "Quem está no elenco de The Incredibles (vozes originais)?", "tipo": ["ator"]},
    {"pergunta": "Protagonistas de Shang-Chi and the Legend of the Ten Rings?", "tipo": ["ator"]},
    {"pergunta": "Quem atua em Doctor Strange?", "tipo": ["ator"]},
    {"pergunta": "Atores principais de Aquaman?", "tipo": ["ator"]},
    {"pergunta": "Quem faz parte do elenco de Alita: Battle Angel?", "tipo": ["ator"]},

    # Perguntas sobre gênero
    {"pergunta": "Qual o gênero do filme Logan?", "tipo": ["genero"]},
    {"pergunta": "Que tipo de filme é The Mask?", "tipo": ["genero"]},
    {"pergunta": "Gênero cinematográfico de Joker?", "tipo": ["genero"]},
    {"pergunta": "Classificação por gênero de Scott Pilgrim vs. the World?", "tipo": ["genero"]},
    {"pergunta": "Que estilo de filme é Blade?", "tipo": ["genero"]},
    {"pergunta": "Gênero predominante em The Avengers?", "tipo": ["genero"]},
    {"pergunta": "Tipo de filme: Shazam!?", "tipo": ["genero"]},
    {"pergunta": "Qual a categoria de The Incredibles?", "tipo": ["genero"]},
    {"pergunta": "Gênero principal de Doctor Strange?", "tipo": ["genero"]},
    {"pergunta": "Que tipo de produção é Alita: Battle Angel?", "tipo": ["genero"]},
    {"pergunta": "Classificação por gênero de The New Mutants?", "tipo": ["genero"]},
    {"pergunta": "Gênero cinematográfico de Ready Player One?", "tipo": ["genero"]},
    {"pergunta": "Que estilo de filme é Deadpool?", "tipo": ["genero"]},
    {"pergunta": "Gênero de The Batman?", "tipo": ["genero"]},
    {"pergunta": "Tipo de produção de Big Hero 6?", "tipo": ["genero"]},

    # Perguntas sobre ano
    {"pergunta": "Em que ano foi lançado The Dark Knight?", "tipo": ["ano"]},
    {"pergunta": "Ano de lançamento de Iron Man?", "tipo": ["ano"]},
    {"pergunta": "Quando estreou The Avengers nos cinemas?", "tipo": ["ano"]},
    {"pergunta": "Data de lançamento de Man of Steel?", "tipo": ["ano"]},
    {"pergunta": "Em que ano saiu Black Panther?", "tipo": ["ano"]},
    {"pergunta": "Ano de produção de X-Men?", "tipo": ["ano"]},
    {"pergunta": "Quando foi lançado Guardians of the Galaxy?", "tipo": ["ano"]},
    {"pergunta": "Em que ano chegou aos cinemas The Batman?", "tipo": ["ano"]},
    {"pergunta": "Ano de estreia de Deadpool?", "tipo": ["ano"]},
    {"pergunta": "Quando foi produzido o primeiro Blade?", "tipo": ["ano"]},
    {"pergunta": "Data de lançamento de Joker?", "tipo": ["ano"]},
    {"pergunta": "Em que ano foi feito The Mask?", "tipo": ["ano"]},
    {"pergunta": "Ano de lançamento de Logan?", "tipo": ["ano"]},
    {"pergunta": "Quando estreou Scott Pilgrim vs. the World?", "tipo": ["ano"]},
    {"pergunta": "Em que ano foi lançado Alita: Battle Angel?", "tipo": ["ano"]},

    # Perguntas compostas
    {"pergunta": "Quem dirigiu e qual o ator principal de Iron Man?", "tipo": ["diretor", "ator"]},
    {"pergunta": "Qual o gênero e ano de lançamento de The Dark Knight?", "tipo": ["genero", "ano"]},
    {"pergunta": "Diretor e ano de Logan?", "tipo": ["diretor", "ano"]},
    {"pergunta": "Atores e gênero de Guardians of the Galaxy?", "tipo": ["ator", "genero"]},
    {"pergunta": "Me fale sobre o diretor e o ano de Joker", "tipo": ["diretor", "ano"]},
    {"pergunta": "Quem são os atores e qual o gênero de The Batman?", "tipo": ["ator", "genero"]},
    {"pergunta": "Ano e diretor de Man of Steel?", "tipo": ["ano", "diretor"]},
    {"pergunta": "Gênero e atores principais de The Avengers?", "tipo": ["genero", "ator"]},
    {"pergunta": "Quem dirigiu e quando foi lançado Black Panther?", "tipo": ["diretor", "ano"]},
    {"pergunta": "Atores e ano de lançamento de Deadpool?", "tipo": ["ator", "ano"]},
    {"pergunta": "Diretor e gênero de Doctor Strange?", "tipo": ["diretor", "genero"]},
    {"pergunta": "Me informe o ano e os atores de X-Men?", "tipo": ["ano", "ator"]},
    {"pergunta": "Qual o diretor e o gênero de The Mask?", "tipo": ["diretor", "genero"]},
    {"pergunta": "Quando foi lançado e quem são os atores de Men in Black?", "tipo": ["ano", "ator"]},
    {"pergunta": "Gênero e diretor de Alita: Battle Angel?", "tipo": ["genero", "diretor"]},

    # Perguntas gerais
    {"pergunta": "Me fale sobre o filme The Avengers", "tipo": ["geral"]},
    {"pergunta": "Dê-me informações sobre The Dark Knight", "tipo": ["geral"]},
    {"pergunta": "Conte-me sobre Logan", "tipo": ["geral"]},
    {"pergunta": "Resumo de Joker", "tipo": ["geral"]},
    {"pergunta": "Detalhes sobre Black Panther", "tipo": ["geral"]},
    {"pergunta": "Informações sobre Man of Steel", "tipo": ["geral"]},
    {"pergunta": "O que sabe sobre Guardians of the Galaxy?", "tipo": ["geral"]},
    {"pergunta": "Me dê detalhes de Iron Man", "tipo": ["geral"]},
    {"pergunta": "Fale sobre The Batman", "tipo": ["geral"]},
    {"pergunta": "Me informe sobre Deadpool", "tipo": ["geral"]},
    {"pergunta": "Conte-me detalhes de Scott Pilgrim vs. the World", "tipo": ["geral"]},
    {"pergunta": "Resumo de The Incredibles", "tipo": ["geral"]},
    {"pergunta": "Dados sobre Alita: Battle Angel", "tipo": ["geral"]},
    {"pergunta": "O que pode me dizer sobre Men in Black?", "tipo": ["geral"]},
    {"pergunta": "Informações gerais de X-Men", "tipo": ["geral"]}
]
