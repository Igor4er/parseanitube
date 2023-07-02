import sys
import asyncio
from datetime import datetime
from controller import Controller


async def main():
    start_time = datetime.now()
    print(f"Startad at {start_time}")

    try:
        year = int(sys.argv[1])
    except IndexError:
        year = None

    cnt = Controller()
    if year is not None:
        await cnt.renew_animes_from(year)
    else:
        await cnt.renew_ongoing_animes()

    end_time = datetime.now()
    print(f"Program finished in {(end_time - start_time).total_seconds() / 60}min")


if __name__ == "__main__":
    asyncio.run(main())
