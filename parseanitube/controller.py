from datetime import datetime
from anitube import Anime, Anitube
import json
from tqdm import tqdm


class Controller:
    def __init__(self):
        self.fullbase = open("animes.json", "r")
        self.anitube = Anitube()
        self.difffile =  open("anidiff.json", "w+")
    
    def update_by_animes(self, new_animes: list):
        old_animes = Controller._load_animes(self.fullbase)
        old_animes_dr = Controller._into_dict_repr(old_animes)
        for anime in new_animes:
            old_animes_dr[anime.url] = anime
        actual_animes = Controller._from_dict_repr(old_animes_dr)
        diff = Controller._differende_between_lists(actual_animes, old_animes)
        print(f"DIFF: {len(diff)} --- OA: {len(old_animes)} --- OADR: {len(old_animes_dr)}")

        self.fullbase.close()
        self.fullbase = open("animes.json", "w")
        Controller._write_animes_in_file(actual_animes, self.fullbase)
        Controller._write_animes_in_file(diff, self.difffile)

    
    def renew_animes_from(self, year: int):
        pass

    def renew_ongoing_animes(self):
        year = Controller._get_today_year()
        animes = self.anitube.query_year(year) + self.anitube.query_year(year-1)
        for anime in tqdm(animes, desc="Fetching animes"):
            self.anitube.fetch_anime(anime)
        self.update_by_animes(animes)

    def _get_today_year() -> int:
        date = datetime.now()
        year = date.strftime("%Y")
        return int(year)
    
    def _load_animes(fullbase) -> list:
        jsond = json.load(fullbase)
        animes = []
        for jsondi in jsond:
            #print(f"{jsondi}@@@@@@@{jsond}")
            animes.append(Anime.from_dict(jsondi))
        return animes
    
    def _into_dict_repr(animes: list) -> dict:
        danimes = {}
        for anime in animes:
            danimes[anime.url] = anime
        return danimes
    
    def _from_dict_repr(animes: dict) -> list:
        return list(animes.values())
    
    def _differende_between_lists(l1: list, l2: list) -> list:
        return [l for l in l1 if l not in l2]
    
    def _write_animes_in_file(animes: list, file):
        list_of_anime_dicts = []
        for anime in animes:
            list_of_anime_dicts.append(anime.to_dict())
        file.write(json.dumps(list_of_anime_dicts))


if __name__ == "__main__":
    cnt = Controller()
    cnt.renew_ongoing_animes()

