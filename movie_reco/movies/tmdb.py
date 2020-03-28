import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

api_base = "https://api.themoviedb.org/3/movie/"
with open(os.path.join(BASE_DIR, 'keys/api_key.txt')) as f:
    api_key = f.read().strip()
config_url = "https://api.themoviedb.org/3/configuration?api_key=" + api_key
poster_base = "https://image.tmdb.org/t/p/"


def api_url(movie_id):
    if not isinstance(movie_id, int):
        raise TypeError
    return f"{api_base}{movie_id}?api_key={api_key}&language=ko-KR"


def poster_url(poster_path, size="w342"):
    return f"{poster_base}{size}{poster_path}"
