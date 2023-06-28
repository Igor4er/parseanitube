import sys
from datetime import datetime
from controller import Controller


def main():
    start_time = datetime.now()
    print(f"Startad at {start_time}")

    try:
        year = int(sys.argv[1])
    except IndexError:
        year = None
    
    cnt = Controller()
    if year is not None:
        pass
    else:
        cnt.renew_ongoing_animes()

    end_time = datetime.now()
    print(f"Program finished in {(start_time - end_time).total_seconds() / 60}")


if __name__ == "__main__":
    main()
