import praw
import re
from bs4 import BeautifulSoup as bs


def main():
    header_tags = ('h1', 'h2', 'h3')
    user_agent = 'script:substrial:v1.0 (by u/)'
    reddit = praw.Reddit(user_agent, user_agent=user_agent)
    animal = reddit.subreddit('animalreddits')
    content = animal.wiki['faq'].content_html
    parser = bs(content, 'html.parser')
    headers = [
        header for tag in header_tags for header in parser.find_all(tag)
    ]
    tables = list({header.find_next('table') for header in headers})
    subreddits = list({
        match
        for table in tables
        for match in re.findall(r'r\/[A-Za-z0-9-_]+', str(table))
    })
    print(subreddits)


if __name__ == '__main__':
    main()
