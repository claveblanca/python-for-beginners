"""
pipeline/pipeline.py
Scheduled end-to-end SOCMINT pipeline with SQLite storage and alerting.

Assembles all prior modules into a single class that can run once
(for research) or continuously on a schedule (for production monitoring).
"""

import json
import logging
import sqlite3
import time
from datetime import datetime, timezone

from collectors.reddit import RedditPost, fetch_subreddit_posts
from processing.cleaning import clean_text
from processing.sentiment import score_sentiment_textblob
from processing.ner import extract_entities

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
)
log = logging.getLogger('socmint')


class SocmintPipeline:
    """
    End-to-end SOCMINT collection and analysis pipeline.

    On each run:
        1. Fetch posts from a target subreddit via PRAW
        2. Run TextBlob sentiment on title + body
        3. Run spaCy NER on title + body
        4. Upsert results into a local SQLite database
        5. Emit a WARNING log for any high-score, highly-negative post

    Usage:
        pipeline = SocmintPipeline('socmint.db')
        pipeline.run_once('worldnews', limit=100)
        # or, to loop forever every 5 minutes:
        pipeline.run_scheduled('worldnews', interval_s=300)
    """

    def __init__(self, db_path: str = 'socmint.db'):
        self.db_path = db_path
        self._init_db()

    # ── Database ──────────────────────────────────────────────────────────────

    def _init_db(self) -> None:
        """Create the posts table if it does not already exist."""
        conn = sqlite3.connect(self.db_path)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                post_id       TEXT PRIMARY KEY,
                subreddit     TEXT,
                title         TEXT,
                selftext      TEXT,
                score         INTEGER,
                num_comments  INTEGER,
                author        TEXT,
                created_utc   TEXT,
                sentiment     TEXT,
                entities      TEXT,
                collected_at  TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def _upsert_post(
        self,
        p: RedditPost,
        sentiment: dict,
        entities: list,
    ) -> None:
        """Insert or replace a post row in the database."""
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            'INSERT OR REPLACE INTO posts VALUES (?,?,?,?,?,?,?,?,?,?,?)',
            (
                p.post_id, p.subreddit, p.title, p.selftext,
                p.score, p.num_comments, p.author,
                p.created_utc.isoformat(),
                json.dumps(sentiment),
                json.dumps(entities),
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        conn.commit()
        conn.close()

    # ── Alerting ──────────────────────────────────────────────────────────────

    def _check_alerts(self, p: RedditPost, sentiment: dict) -> None:
        """
        Emit a WARNING log when a post is both highly negative and viral.

        Threshold: polarity < -0.5 AND score > 5000.
        Extend this method to send email, Slack, or webhook alerts.
        """
        if sentiment['polarity'] < -0.5 and p.score > 5000:
            log.warning(
                f"ALERT high-negative viral post — "
                f"id={p.post_id} score={p.score} "
                f"polarity={sentiment['polarity']} "
                f"title={p.title[:60]!r}"
            )

    # ── Public API ────────────────────────────────────────────────────────────

    def run_once(self, subreddit: str, limit: int = 50) -> int:
        """
        Collect, analyse, and store one batch of posts.

        Args:
            subreddit: Subreddit name, e.g. 'worldnews'.
            limit:     Number of posts to fetch (max 1000).

        Returns:
            Number of posts stored.
        """
        log.info(f"Collecting {limit} posts from r/{subreddit}")
        posts = fetch_subreddit_posts(subreddit, limit=limit)

        for p in posts:
            text      = p.title + ' ' + p.selftext
            sentiment = score_sentiment_textblob(text)
            entities  = extract_entities(text)
            self._upsert_post(p, sentiment, entities)
            self._check_alerts(p, sentiment)

        log.info(f"Stored {len(posts)} posts → {self.db_path}")
        return len(posts)

    def run_scheduled(
        self,
        subreddit: str,
        interval_s: int = 300,
    ) -> None:
        """
        Run collection in an infinite loop, every interval_s seconds.

        Exceptions are caught and logged so a transient API error does
        not terminate the process. Interrupt with Ctrl+C.

        Args:
            subreddit:  Subreddit name to monitor.
            interval_s: Seconds to sleep between runs (default: 300 = 5 min).
        """
        log.info(
            f"Starting scheduled pipeline — "
            f"r/{subreddit} every {interval_s}s"
        )
        while True:
            try:
                self.run_once(subreddit)
            except Exception as exc:
                log.error(f"Collection error: {exc}")
            time.sleep(interval_s)


if __name__ == "__main__":
    pipeline = SocmintPipeline('socmint.db')
    pipeline.run_once('worldnews', limit=25)
    # Uncomment to run continuously:
    # pipeline.run_scheduled('worldnews', interval_s=300)
