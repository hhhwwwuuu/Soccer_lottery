import argparse
from crawler.collector import MatchCrawler

def arg_parser():
    parser = argparse.ArgumentParser(description="Collecting Team Info from web...")
    # parser.add_argument('round', type=int, help='the number of round game (default=1)', default=1)
    # parser.add_argument('host', type=str, help='Host team')
    # parser.add_argument('guest', type=str, help='guest team')
    parser.add_argument('--match', type=str, help='the web link of the game')
    parser.add_argument('--league', type=str, help='the web link of league standing for the previous season')
    return parser


if __name__ == "__main__":
    #print("asda")
    parser = arg_parser()
    args = parser.parse_args()
    #print(args.url)
    crawl = MatchCrawler(args.match, args.league)
    crawl.quit_crawl()