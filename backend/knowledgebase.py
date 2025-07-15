import json

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
            print(f"Falha ao carregar a base de dados{self.data_file}.")
            return []
    
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
