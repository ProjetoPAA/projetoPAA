import json

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
