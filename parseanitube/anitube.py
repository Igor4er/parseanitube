import requests
from dataclasses import dataclass
from dataclasses_json import dataclass_json
from bs4 import BeautifulSoup
from tqdm import tqdm
import time
import json

ANITUBE_URL = "https://anitube.in.ua/"
ANITUBE_QUERY_URL_BY = "f/ne-chpati=DUB/r.real_rating=6;10/r.year="
ANITUBE_QUERY_URL_AY = "/type=ТБ/sort=date/order=desc/"

@dataclass_json
@dataclass
class Anime:
    url: str
    title: str
    year:str
    description: str
    image_url: str
    director: str
    studio: str
    genres: list
    series: list
    ongoing: bool

    def __init__(self, url: str, title: str, **kwargs):
        self.url = url
        self.title = title
        self.year = kwargs.get("year", None)
        self.description = kwargs.get("description", None)
        self.image_url  = kwargs.get("image_url", None)
        self.director = kwargs.get("director", None)
        self.studio = kwargs.get("studio", None)
        self.genres = kwargs.get("genres", None)
        self.series = kwargs.get("series", None)
        self.ongoing = kwargs.get("ongoing", True)
    
    def __hash__(self):
        hashed = hash((
            getattr(self, key)
            for key in self.__annotations__
        ))
        return hashed

    def animes_from_page(page: bytes) -> list:
        soup = BeautifulSoup(page, features="lxml")
        animes = []
        for anime_page_object in Anime._list_animes_of_page(soup):
            animes.append(
                Anime._url_and_title_anime_from_anime_page_object(anime_page_object)
            )
        return animes

    def update_by_page(self, page: bytes):
        soup = BeautifulSoup(page, features="lxml").find("article")
        story = Anime._story_by_page(soup)
        storytable = Anime._storytable_by_story(story)
        # print(f"====================================\n{storytable}\n---------------------------------")

        self.description = Anime._description_by_story(story)
        self.image_url = Anime._image_url_by_page(soup)

        Anime._update_params_by_storytable(storytable, self)
        # TODO: Series

    def _update_params_by_storytable(storytable: list, anime):
        anime.year = storytable.get(" Рік виходу аніме", None)
        anime.genres = storytable.get("Жанр", ",").split(", ")
        anime.director = storytable.get("Режисер", None)
        anime.studio = storytable.get("Студія", None)

        # Is ongoing:
        og = storytable.get("Серій", "0 _ 0").split()
        anime.ongoing = og[0] != og[2]

    def _image_url_by_page(page: BeautifulSoup) -> str:
        return page.find("span", class_="story_post").find("img")["src"]

    def _description_by_story(story: BeautifulSoup) -> str:
        return story.find("div", class_="my-text").text.replace("<br>", "\n\n")

    # def _ongoing_by_storytable(storytable: list) -> bool:
    #     pst = storytable[3].split(">")[-1].split()
    #     return pst[0] == pst[2]

    # def _studio_by_storytable(storytable: list) -> str:
    #     return storytable[3].split(">")[-1]

    # def _director_by_storytable(storytable: list) -> str:
    #     return storytable[2].split(">")[-1]

    # def _genres_by_storytable(storytable: list) -> list:
    #     genres = []
    #     for genre in storytable[1].find_all("a"):
    #         genres.append(genre.text)
    #     return genres

    # def _year_by_storytable(storytable: list) -> str:
    #     return storytable[0].find("a").text

    def _storytable_by_story(story: list) -> dict:
        lines = {}
        tsplit = story.text.split("\n\n")
        for line in tsplit:
            if len(line) != 0:
                rs = line.replace("<html><body><p>", "").replace("</p></body></html>", "").replace("\n", " ").replace("\r", "").split(": ")
                if len(rs) >= 2:
                    lines[rs[0]] = rs[1]
        return lines

    def _story_by_page(page: BeautifulSoup):
        return page.find_all("div", class_="story_c_r")[-1]

    def _list_animes_of_page(page: BeautifulSoup) -> list:
        return page.find_all("article")

    def _url_and_title_anime_from_anime_page_object(anime_page_object: BeautifulSoup):
        tiu = anime_page_object.find("a")
        return Anime(url=tiu["href"], title=tiu.text)


class Anitube:
    def _get_page_or_none(url: str) -> bytes | None:
        resp = requests.get(url)
        if resp.ok:
            return resp.content
        else:
            return None

    def _get_page_anyway(url: str) -> bytes:
        resp = requests.get(url)
        if resp.ok:
            return resp.content
        else:
            if resp.status_code == 429:
                time.sleep(10)
            return Anitube._get_page_anyway(url)
    
    def _max_page(query_url:str) -> int:
        return int(BeautifulSoup(Anitube._get_page_anyway(query_url), features="lxml").find("span", class_="lcol navi_pages").find_all("a")[-1].text)

    def query_year(self, year: int = 2023):
        page = 1
        query_url = f"{ANITUBE_URL}{ANITUBE_QUERY_URL_BY}{year};{year}{ANITUBE_QUERY_URL_AY}"
        max_page = Anitube._max_page(query_url)
        animes = []
        with tqdm(total=max_page, desc="Querying animes") as pbar:
            while page <= max_page:
                query_page = Anitube._get_page_anyway(query_url + f"/page/{page}")
                animes += (Anime.animes_from_page(query_page))
                page +=1
                pbar.update(1)
            return animes

    def fetch_anime(self, anime: Anime):
        page = Anitube._get_page_anyway(anime.url)
        if page is not None:
            anime.update_by_page(page)


if __name__ == "__main__":
    an = Anitube()
    ql = an.query_year()
    for q in ql:
        an.fetch_anime(q)
        jsond = json.dumps(q.to_dict())
        print(f"{jsond} at {q.url}\n\n")
