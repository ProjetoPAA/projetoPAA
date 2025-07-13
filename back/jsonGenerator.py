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
        # Marvel - MCU Fase 1 a 4
        "Iron Man", "The Incredible Hulk", "Iron Man 2", "Thor", "Captain America: The First Avenger",
        "The Avengers", "Iron Man 3", "Thor: The Dark World", "Captain America: The Winter Soldier",
        "Guardians of the Galaxy", "Avengers: Age of Ultron", "Ant-Man", "Captain America: Civil War",
        "Doctor Strange", "Guardians of the Galaxy Vol. 2", "Spider-Man: Homecoming", "Thor: Ragnarok",
        "Black Panther", "Avengers: Infinity War", "Ant-Man and the Wasp", "Captain Marvel",
        "Avengers: Endgame", "Spider-Man: Far From Home", "Black Widow", "Shang-Chi and the Legend of the Ten Rings",
        "Eternals", "Spider-Man: No Way Home", "Doctor Strange in the Multiverse of Madness",
        "Thor: Love and Thunder", "Black Panther: Wakanda Forever", "Ant-Man and the Wasp: Quantumania",
        "Guardians of the Galaxy Vol. 3","X-Men", "X2", "X-Men: The Last Stand", "X-Men Origins: Wolverine", "X-Men: First Class",
        "The Wolverine", "X-Men: Days of Future Past", "Deadpool", "X-Men: Apocalypse",
        "Logan", "Deadpool 2", "Dark Phoenix", "The New Mutants","Superman", "Superman II", "Batman", "Batman Returns", "Batman Forever",
        "Batman & Robin", "Batman Begins", "The Dark Knight", "The Dark Knight Rises",
        "Man of Steel", "Batman v Superman: Dawn of Justice", "Suicide Squad",
        "Wonder Woman", "Justice League", "Aquaman", "Shazam!", "Joker",
        "Birds of Prey", "Wonder Woman 1984", "The Suicide Squad", "Zack Snyder's Justice League",
        "The Batman", "Black Adam", "Shazam! Fury of the Gods", "The Flash","Hellboy", "Hellboy II: The Golden Army", "Hellboy (2019)", "The Crow",
        "The Mask", "Men in Black", "Men in Black II", "Men in Black 3",
        "The Phantom", "The Shadow", "The Rocketeer", "Blade", "Blade II",
        "Blade: Trinity", "The Punisher (2004)", "Punisher: War Zone","Pokémon: Detective Pikachu", "Pokémon: The First Movie", "Pokémon 2000",
        "Pokémon 3: The Movie", "Pokémon 4Ever", "Dragonball Evolution",
        "Teenage Mutant Ninja Turtles", "TMNT", "Teenage Mutant Ninja Turtles (2014)",
        "Teenage Mutant Ninja Turtles: Out of the Shadows", "Mortal Kombat",
        "Mortal Kombat: Annihilation", "Mortal Kombat (2021)", "Prince of Persia: The Sands of Time",
        "Warcraft", "Tron", "Tron: Legacy", "The League of Extraordinary Gentlemen",
        "Ghost in the Shell", "Alita: Battle Angel", "Ready Player One",
        "Scott Pilgrim vs. the World", "R.I.P.D.", "Power Rangers (2017)","The Incredibles", "The Incredibles 2", "Big Hero 6", "Megamind",
        "Spider-Man: Into the Spider-Verse", "Spider-Man: Across the Spider-Verse",
        "Batman: Mask of the Phantasm", "Batman: The Killing Joke"
    ]
    
    omdb_to_json = OMDBToJson(API_KEY)
    omdb_to_json.create_movies_json(filmes)