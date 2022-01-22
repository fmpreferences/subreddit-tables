import praw
import prawcore
from argparse import ArgumentParser
import re
from bs4 import BeautifulSoup as bs
import random
import sys


def main():
    # namespace = reddits_parser()
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
    print(generate_subreddits(subreddits, reddit, 10, 'content.w', (1, 10)))
    multireddit_name = ''  # namespace.multi
    try:
        print(
            reddit.multireddit(reddit.user.me().name,
                               multireddit_name).subreddits)
    except prawcore.NotFound:
        create_selection = input('create y/n?')
        if create_selection.lower() == 'y':
            reddit.multireddit.create(multireddit_name, [])


def generate_subreddits(sub_pool, reddit, count: int, error=None, strata=None):
    def subscribers_least_to_greatest(sub):
        try:
            return reddit.subreddit(sub).subscribers
        except prawcore.Forbidden:
            errormsg = f'Access to r/{sub} is private'
            if error is not None:
                with open(error, 'a') as error_file:
                    error_file.write(errormsg + '\n')
            print(errormsg, file=sys.stderr)
            return 0
        except prawcore.Redirect:
            errormsg = f'r/{sub} does not exist; possibly banned'
            if error is not None:
                with open(error, 'a') as error_file:
                    error_file.write(errormsg + '\n')
            print(errormsg, file=sys.stderr)
            return 0
        except prawcore.NotFound:
            errormsg = f'r/{sub} has been banned'
            if error is not None:
                with open(error, 'a') as error_file:
                    error_file.write(errormsg + '\n')
            print(errormsg, file=sys.stderr)
            return 0
        except prawcore.ResponseException as e:
            print(e, type(e), sub, file=sys.stderr)
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


# def reddits_parser():
#     argparse = ArgumentParser(description='Lorem Ipsum')
#     argparse.add_argument('multi', type=str, help='the multi on your user')
#     argparse.add_argument('reddits',
#                           type=str,
#                           help='reddits to analyze, separated by spaces')
#     argparse.add_argument('-r',
#                           '--range',
#                           type=str,
#                           help='ranks of the subreddits to analyze')
#     argparse.add_argument('-c',
#                           '--count',
#                           type=int,
#                           help='number of subs to choose')
#     argparse.add_argument('-e',
#                           '--error',
#                           type=str,
#                           help='write errors to this file')

#     return argparse.parse_args()

if __name__ == '__main__':
    main()
