import argparse
from watchdog.app import run_app


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--id', required=True)
    args = parser.parse_args()

    run_app(args.id)


if __name__ == '__main__':
    main()
