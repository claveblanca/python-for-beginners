"""
collectors/reddit.py
Reddit data collection using PRAW.

Setup:
    pip install praw requests
    Create a Reddit app at https://www.reddit.com/prefs/apps (type: script)
    Set redirect URI to http://localhost:8080

Environment variables required:
    REDDIT_CLIENT_ID
    REDDIT_CLIENT_SECRET
    REDDIT_USER_AGENT   e.g. 'socmint-book/1.0 by u/your_username'
"""

import os
import praw
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class RedditPost:
    post_id:      str
    subreddit:    str
    title:        str
    selftext:     str
    score:        int
    num_comments: int
    author:       str
    created_utc:  datetime
    url:          str
    flair:        str = ''


def get_reddit_client() -> praw.Reddit:
    """Return an authenticated PRAW Reddit client from environment variables."""
    return praw.Reddit(
        client_id     = os.environ["REDDIT_CLIENT_ID"],
        client_secret = os.environ["REDDIT_CLIENT_SECRET"],
        user_agent    = os.environ["REDDIT_USER_AGENT"],
    )


def fetch_subreddit_posts(
    subreddit_name: str,
    mode: str = "hot",
    limit: int = 25,
) -> list[RedditPost]:
    """
    Fetch posts from a subreddit.

    Args:
        subreddit_name: e.g. 'worldnews'
        mode:           'hot' | 'new' | 'top' | 'rising'
        limit:          number of posts to fetch (max 1000)

    Returns:
        List of RedditPost dataclasses.
    """
    reddit = get_reddit_client()
    sub    = reddit.subreddit(subreddit_name)
    feed   = getattr(sub, mode)(limit=limit)
    posts  = []
    for p in feed:
        posts.append(RedditPost(
            post_id      = p.id,
            subreddit    = subreddit_name,
            title        = p.title,
            selftext     = p.selftext,
            score        = p.score,
            num_comments = p.num_comments,
            author       = str(p.author) if p.author else "[deleted]",
            created_utc  = datetime.fromtimestamp(
                               p.created_utc, tz=timezone.utc),
            url          = p.url,
            flair        = p.link_flair_text or "",
        ))
    return posts


def fetch_post_comments(
    post_id: str,
    limit: int = 200,
) -> list[dict]:
    """
    Return a flat list of comment dicts for a Reddit post ID.

    Args:
        post_id: Reddit post ID string (e.g. '1abc23')
        limit:   maximum number of comments to return

    Returns:
        List of dicts with keys: comment_id, post_id, author,
        body, score, depth, created_utc.
    """
    reddit     = get_reddit_client()
    submission = reddit.submission(id=post_id)
    submission.comments.replace_more(limit=5)   # expand 'load more' up to 5×
    comments   = []
    for c in submission.comments.list()[:limit]:
        if not hasattr(c, 'body'):
            continue
        comments.append({
            "comment_id":  c.id,
            "post_id":     post_id,
            "author":      str(c.author) if c.author else "[deleted]",
            "body":        c.body,
            "score":       c.score,
            "depth":       c.depth,
            "created_utc": datetime.fromtimestamp(
                               c.created_utc, tz=timezone.utc),
        })
    return comments


if __name__ == "__main__":
    posts = fetch_subreddit_posts("worldnews", mode="hot", limit=5)
    for p in posts:
        print(f"[{p.score:>6}] {p.title[:70]}")
