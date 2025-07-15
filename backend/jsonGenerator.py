import requests
import json

class OMDBToJson:
    def __init__(self, api_key):
        self.api_key = "23361dd0"
        self.base_url = "http://www.omdbapi.com/"
    
    def get_movie_data(self, movie_title):
        params = {
            'apikey': self.api_key,
            't': movie_title,
            'type': 'movie',
            'r': 'json'
        }
        response = requests.get(self.base_url, params=params)
        return response.json()
    
    def format_movie_data(self, raw_data):
        return {
            'titulo': raw_data.get('Title', 'Desconhecido'),
            'diretor': raw_data.get('Director', 'Desconhecido').split(', '),
            'atores': raw_data.get('Actors', 'Desconhecido').split(', '),
            'genero': raw_data.get('Genre', 'Desconhecido').split(', '),
            'ano': raw_data.get('Year', 'Desconhecido'),
            'sinopse': raw_data.get('Plot', 'Sinopse não disponível')
        }
    
    def save_to_json(self, movies_data, filename='filmes.json'):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(movies_data, f, ensure_ascii=False, indent=4)
    
    def create_movies_json(self, movie_titles):
        movies_data = []
        
        for title in movie_titles:
            print(f"Obtendo dados para: {title}")
            raw_data = self.get_movie_data(title)
            
            if raw_data.get('Response') == 'True':
                formatted_data = self.format_movie_data(raw_data)
                movies_data.append(formatted_data)
                print(f"Dados obtidos com sucesso para: {title}")
            else:
                print(f"Erro ao obter dados para: {title} - {raw_data.get('Error', 'Erro desconhecido')}")
        
        self.save_to_json(movies_data)
        print(f"Arquivo filmes.json criado com {len(movies_data)} filmes.")

if __name__ == "__main__":
    API_KEY = "23361dd0"
    
    filmes = [
        "Iron Man", "The Incredible Hulk", "Thor", "Captain America: The First Avenger",
        "The Avengers",
        "Guardians of the Galaxy", "Ant-Man",
        "Doctor Strange", "Spider-Man: Homecoming",
        "Black Panther", "Captain Marvel",
        "Black Widow", "Shang-Chi and the Legend of the Ten Rings",
        "Eternals",
        "X-Men", "X2",
        "The Wolverine", "Deadpool",
        "Logan", "Dark Phoenix", "The New Mutants", "The Dark Knight",
        "Man of Steel", "Suicide Squad", "Justice League", "Aquaman", "Shazam!", "Joker",
        "Birds of Prey", "Wonder Woman 1984",
        "The Batman", "Black Adam", "Shazam! Fury of the Gods", "The Flash","Hellboy (2019)", "The Crow",
        "The Mask", "Men in Black",
        "The Phantom", "The Shadow", "The Rocketeer", "Blade", "Blade II",
        "Blade: Trinity", "The Punisher (2004)", "Punisher: War Zone","Pokémon: Detective Pikachu", "Dragonball Evolution",
        "Teenage Mutant Ninja Turtles", "Mortal Kombat", "Prince of Persia: The Sands of Time",
        "Warcraft", "Tron: Legacy", "The League of Extraordinary Gentlemen",
        "Ghost in the Shell", "Alita: Battle Angel", "Ready Player One",
        "Scott Pilgrim vs. the World", "R.I.P.D.", "Power Rangers (2017)","The Incredibles", "Big Hero 6", "Megamind",
    ]
    
    omdb_to_json = OMDBToJson(API_KEY)
    omdb_to_json.create_movies_json(filmes)