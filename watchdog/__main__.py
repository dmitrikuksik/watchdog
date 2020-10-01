import argparse
from watchdog.app import run_app


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-i', '--id', required=True
    )
    parser.add_argument(
        '-l', '--log', required=False
    )
    args = parser.parse_args()

    run_app(args.id, args.log)


if __name__ == '__main__':
    main()
