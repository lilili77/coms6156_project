import requests


class ImdbApi:
    url = "https://moviesdb5.p.rapidapi.com/om"

    headers = {
        "X-RapidAPI-Key": "7c86bf219cmsh6f8359103235194p14fe98jsncd11bca70731",
        "X-RapidAPI-Host": "moviesdb5.p.rapidapi.com"
    }

    def search_movie(self, title):
        querystring = {"t": title}
        response = requests.request("GET", self.url, headers=self.headers, params=querystring)

        return response.json()
