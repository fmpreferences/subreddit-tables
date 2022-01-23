import praw
import prawcore
from argparse import ArgumentParser
import re
from bs4 import BeautifulSoup as bs
import random
import sys
from datetime import datetime, timezone


def main():
    # declaration for important global variables
    namespace = reddits_parser()
    headings = [sub.strip().lower() for sub in namespace.headings.split(',')]
    multireddit_name = namespace.multi
    subreddit_name, wiki_page = [
        part.strip() for part in namespace.source.split(',')
    ][:2]
    ranks = [int(num.strip()) for num in namespace.range.split(',')][:2]
    count = namespace.count
    error = namespace.error
    try:
        active_time = float(namespace.active)
    except ValueError:
        time, date_format = [
            part.strip() for part in namespace.active.split(',')
        ][:2]
        active_time = datetime.strptime(
            time, date_format).replace(tzinfo=timezone.utc).timestamp()

    header_tags = 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'
    user_agent = 'script:substrial:v1.0 (by u/Animal_Subs_Trial)'
    reddit = praw.Reddit(user_agent, user_agent=user_agent)

    # declaration for global methods

    def generate_subreddits(sub_pool):
        '''generates subreddits based on argparser'''
        excluded = []

        def handle_errors(sub, errormsg):
            if error is not None:
                with open(error, 'w') as error_file:
                    error_file.write(errormsg + '\n')
            print(errormsg, file=sys.stderr)
            excluded.append(sub)

        def subscribers_least_to_greatest(sub):
            subreddit = reddit.subreddit(sub)
            try:
                if active_time is not None:
                    last_post = [m for m in subreddit.new(limit=1)][0]
                    if last_post.created_utc < active_time:
                        print(f'{sub} excluded for inactivity')
                        excluded.append(sub)

                return subreddit.subscribers
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
            if top > 0 and bottom > 0:
                top = max(1, top)
                bottom = min(100, bottom)
            elif top < 0 and bottom < 0:
                top = max(-100, top) + 101
                bottom = min(-1, bottom) + 101
            if count is not None and count != 0:
                new_count = min(count, bottom - top + 1)
            else:
                new_count = bottom - top + 1
            subset = random.sample(subreddits[top - 1:bottom], new_count)
        else:
            subset = random.sample(subreddits, count)
        return list(set(subset) - set(excluded))

    subreddit = reddit.subreddit(subreddit_name)
    content = subreddit.wiki[wiki_page].content_html
    parser = bs(content, 'html.parser')
    with open('content.html', 'w') as content_html:
        content_html.write(content)
    headers = [
        header for tag in header_tags for header in parser.find_all(tag)
    ]
    if headings:
        tables = list({
            header.find_next('table')
            for header in headers if header.string.lower() in headings
        })
    else:
        tables = list({header.find_next('table') for header in headers})
    subreddits = list({
        match
        for table in tables
        for match in re.findall(r'r\/([A-Za-z0-9-_]+)', str(table))
    })
    try:
        target_multi = reddit.multireddit(reddit.user.me().name,
                                          multireddit_name)
        sub_names = {
            sub.display_name.lower()
            for sub in target_multi.subreddits
        }
        generated_subs = {
            sub.lower()
            for sub in generate_subreddits(subreddits)
        }
        intersection = sub_names & generated_subs
        subs_to_remove = sub_names - intersection
        subs_to_add = generated_subs - intersection
        print(f'removing {len(subs_to_remove)} subs:\n' +
              '\n'.join(subs_to_remove) + '\n')
        print(f'adding {len(subs_to_add)} subs:\n' + '\n'.join(subs_to_add) +
              '\n')
        for sub in subs_to_remove:
            target_multi.remove(reddit.subreddit(sub))
        for sub in subs_to_add:
            target_multi.add(reddit.subreddit(sub))

    except prawcore.NotFound:
        create_selection = input('create y/n?')
        if create_selection.lower().strip() == 'y':
            subs = generate_subreddits(subreddits)
            print(f'adding {len(subs)} subs:\n' + '\n'.join(subs) + '\n')

            reddit.multireddit.create(multireddit_name, subs)


def reddits_parser():
    argparse = ArgumentParser(
        description=
        'Creates a bot which generates a multireddit from the given wikipage')
    argparse.add_argument('source',
                          type=str,
                          help='the wikipage to use: subredditname/page')
    argparse.add_argument('headings',
                          type=str,
                          help='headings to analyze, separated by spaces')
    argparse.add_argument('multi', type=str, help='the multi on your user')
    argparse.add_argument(
        '-r',
        '--range',
        type=str,
        help='ranks of the subreddits to analyze. use negative to sort backward'
    )
    argparse.add_argument('-c',
                          '--count',
                          type=int,
                          help='number of subs to choose')
    argparse.add_argument('-e',
                          '--error',
                          type=str,
                          help='write errors to this file')
    argparse.add_argument('-a',
                          '--active',
                          type=str,
                          help='''filters subs based on last activity.
                          either a unix time or send your date format''')
    #     argparse.add_argument('-s',
    #                           '--self',
    #                           type=int,
    #                           help='''filters based on if last post is self or not.
    # not work without -a. 1 for self, 0 for not self, -1 for ignore this''')

    return argparse.parse_args()


if __name__ == '__main__':
    main()
