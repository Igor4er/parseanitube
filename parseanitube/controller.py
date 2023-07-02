from datetime import datetime
from anitube import Anime, Anitube
import json
import asyncio
# from aiofile import AIOFile
from tqdm.asyncio import tqdm


def _get_today_year() -> int:
    date = datetime.now()
    year = date.strftime("%Y")
    return int(year)


class Controller:
    def __init__(self):
        self.fullbase = open("animes.json", "r")
        self.anitube = Anitube()
        self.difffile = open("anidiff.json", "w+")
    
    def update_by_animes(self, new_animes: list):
        old_animes = Controller._load_animes
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

    async def renew_animes_from(self, year: int):
        today_year = _get_today_year()

        animes = []
        for y in range(year, today_year+1):
            animes += await self.anitube.query_year(y)

        tasks = []
        print(f"Gonna fetch {len(animes)} animes")
        for anime in animes:
            tasks.append(asyncio.create_task(self.anitube.fetch_anime(anime)))
        await asyncio.gather(*tasks)
        self.update_by_animes(animes)

    async def renew_ongoing_animes(self):
        year = _get_today_year()
        animes = await self.anitube.query_year(year) + await self.anitube.query_year(year-1)
        tasks = []
        print(f"Gonna fetch {len(animes)} animes")
        for anime in animes:
            tasks.append(asyncio.create_task(self.anitube.fetch_anime(anime)))
        await asyncio.gather(*tasks)
        print("JOINED")
        self.update_by_animes(animes)

    def _load_animes(fullbase) -> list:
        jsond = json.load(fullbase)
        animes = []
        for jsondi in jsond:
            # print(f"{jsondi}@@@@@@@{jsond}")
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

