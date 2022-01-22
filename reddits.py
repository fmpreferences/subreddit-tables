import praw
import prawcore
from argparse import ArgumentParser
import re
from bs4 import BeautifulSoup as bs
import random
import sys


def main():
    # declaration for important global variables
    # namespace = reddits_parser()
    categories = 'General Cats', 'Cat Media', 'Cats Being Cats', 'Cats in Shapes'  # [sub.strip() for sub in namespace.reddits.split(',')]
    multireddit_name = 'abc'  # namespace.multi
    ranks = 1, 25  # namespace.range
    count = 25  # namespace.count
    error = 'content.w'  # namespace.error

    header_tags = 'h1', 'h2', 'h3', 'h4', 'h5'
    user_agent = 'script:substrial:v1.0 (by u/Animal_Subs_Trial)'
    reddit = praw.Reddit(user_agent, user_agent=user_agent)

    # declaration for global methods

    def generate_subreddits(sub_pool):
        '''generates subreddits based on argparser'''
        banned = []

        def handle_errors(sub, errormsg):
            if error is not None:
                with open(error, 'w') as error_file:
                    error_file.write(errormsg + '\n')
            print(errormsg, file=sys.stderr)
            banned.append(sub)

        def subscribers_least_to_greatest(sub):
            try:
                return reddit.subreddit(sub).subscribers
            except prawcore.Forbidden:
                errormsg = f'Access to r/{sub} is private'
                handle_errors(sub, errormsg)
                return 0
            except prawcore.Redirect:
                errormsg = f'r/{sub} does not exist; possibly banned'
                handle_errors(sub, errormsg)
                return 0
            except prawcore.NotFound:
                errormsg = f'r/{sub} has been banned'
                handle_errors(sub, errormsg)
                return 0
            except prawcore.ResponseException as e:
                errormsg = ' '.join(e, type(e), sub)
                handle_errors(sub, errormsg)
                return 0

        subreddits = sorted(sub_pool,
                            key=subscribers_least_to_greatest,
                            reverse=True)
        if ranks is not None:
            top, bottom = ranks
            top = max(0, top)
            bottom = min(100, bottom)
            subset = random.sample(subreddits[top - 1:bottom], count)
        else:
            subset = random.sample(subreddits, count)
        return list(set(subset) - set(banned))

    animal = reddit.subreddit('catsubs')
    content = animal.wiki['index'].content_html
    parser = bs(content, 'html.parser')

    headers = [
        header for tag in header_tags for header in parser.find_all(tag)
    ]
    if categories:
        tables = list({
            header.find_next('table')
            for header in headers if header.string in categories
        })
    else:
        tables = list({header.find_next('table') for header in headers})
    subreddits = list({
        match
        for table in tables
        for match in re.findall(r'r\/([A-Za-z0-9-_]+)', str(table))
    })
    print(subreddits)
    try:
        target_multi = reddit.multireddit(reddit.user.me().name,
                                          multireddit_name)
        sub_names = {sub.display_name for sub in target_multi.subreddits}
        generated_subs = set(
            generate_subreddits(subreddits, reddit, count, error, ranks))
        intersection = sub_names & generated_subs
        subs_to_remove = sub_names - intersection
        subs_to_add = generated_subs - intersection
        print(subs_to_remove, subs_to_add)
        for sub in subs_to_remove:
            target_multi.remove(reddit.subreddit(sub))
        for sub in subs_to_add:
            target_multi.add(reddit.subreddit(sub))

    except prawcore.NotFound:
        create_selection = input('create y/n?')
        if create_selection.lower() == 'y':
            reddit.multireddit.create(
                multireddit_name,
                generate_subreddits(subreddits, reddit, count, error, ranks))


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
