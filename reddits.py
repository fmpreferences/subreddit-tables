import praw
import prawcore
from argparse import ArgumentParser
import re
from bs4 import BeautifulSoup as bs


def main():
    # argparse = ArgumentParser(description='Lorem Ipsum')
    # argparse.add_argument('multi', type=str, help='the multi on your user')
    # argparse.add_argument('reddits',
    #                       type=str,
    #                       help='reddits to analyze, separated by spaces')

    # namespace = argparse.parse_args()
    # argparse.add_argument('-s')
    header_tags = 'h1', 'h2', 'h3'
    user_agent = 'script:substrial:v1.0 (by u/)'
    reddit = praw.Reddit(user_agent, user_agent=user_agent)
    animal = reddit.subreddit('animalreddits')
    content = animal.wiki['faq'].content_html
    parser = bs(content, 'html.parser')
    headers = [
        header for tag in header_tags for header in parser.find_all(tag)
    ]
    categories = 'Identification', 'Mammals'  # [sub.strip() for sub in namespace.reddits.split(',')]
    tables = list({
        header.find_next('table')
        for header in headers if header.string in categories
    })
    subreddits = list({
        match
        for table in tables
        for match in re.findall(r'r\/[A-Za-z0-9-_]+', str(table))
    })
    print(subreddits)
    multireddit_name = ''  # namespace.multi
    try:
        print(
            reddit.multireddit(reddit.user.me().name,
                               multireddit_name).subreddits)
    except prawcore.NotFound:
        create_selection = input('create y/n?')
        if create_selection.lower() == 'y':
            reddit.multireddit.create(multireddit_name, [])


def generate_subreddits():
    pass


if __name__ == '__main__':
    main()
