import praw
import prawcore
from argparse import ArgumentParser
import re
from bs4 import BeautifulSoup as bs
import random


def main():
    # argparse = ArgumentParser(description='Lorem Ipsum')
    # argparse.add_argument('multi', type=str, help='the multi on your user')
    # argparse.add_argument('reddits',
    #                       type=str,
    #                       help='reddits to analyze, separated by spaces')

    # namespace = argparse.parse_args()
    # argparse.add_argument('-s')
    header_tags = 'h1', 'h2', 'h3', 'h4', 'h5'
    user_agent = 'script:substrial:v1.0 (by u/)'
    reddit = praw.Reddit(user_agent, user_agent=user_agent)
    animal = reddit.subreddit('animalreddits')
    content = animal.wiki['faq'].content_html
    parser = bs(content, 'html.parser')
    headers = [
        header for tag in header_tags for header in parser.find_all(tag)
    ]
    categories = 'Cats General',  # [sub.strip() for sub in namespace.reddits.split(',')]
    tables = list({
        header.find_next('table')
        for header in headers if header.string in categories
    })
    subreddits = list({
        match
        for table in tables
        for match in re.findall(r'r\/([A-Za-z0-9-_]+)', str(table))
    })
    print(subreddits)
    print(generate_subreddits(subreddits, reddit, 10, (1, 10)))
    multireddit_name = ''  # namespace.multi
    try:
        print(
            reddit.multireddit(reddit.user.me().name,
                               multireddit_name).subreddits)
    except prawcore.NotFound:
        create_selection = input('create y/n?')
        if create_selection.lower() == 'y':
            reddit.multireddit.create(multireddit_name, [])


def generate_subreddits(sub_pool, reddit, count: int, strata=None):
    def subscribers_least_to_greatest(sub):
        try:
            return reddit.subreddit(sub).subscribers
        except prawcore.Forbidden:
            print(f'Forbidden access to r/{sub}; banned by reddit?')
            return 0
        except prawcore.ResponseException:
            return 0

    subreddits = sorted(sub_pool,
                        key=subscribers_least_to_greatest,
                        reverse=True)
    subset = []
    if strata is not None:
        top, bottom = strata
        subset = random.sample(subreddits[top - 1:bottom], count)
    else:
        subset = random.sample(subreddits, count)
    return subset


if __name__ == '__main__':
    main()
