import argparse
from crawler.collector import *

def arg_parser():
    parser = argparse.ArgumentParser(description="Collecting Team Info from web...")
    # parser.add_argument('round', type=int, help='the number of round game (default=1)', default=1)
    # parser.add_argument('host', type=str, help='Host team')
    # parser.add_argument('guest', type=str, help='guest team')
    parser.add_argument('--url', type=str, help='the web link of the game')
    return parser


if __name__ == "__main__":
    #print("asda")
    parser = arg_parser()
    args = parser.parse_args()
    print(args.url)
