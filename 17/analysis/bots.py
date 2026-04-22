"""
analysis/bots.py
Heuristic detection of automated accounts and coordinated posting behaviour.

No single signal is definitive — this module combines several behavioural
indicators into a composite suspicion score.
"""

import statistics
from dataclasses import dataclass
from datetime import datetime


@dataclass
class AccountProfile:
    """
    Snapshot of a Reddit account's public metadata.

    All fields are available from the PRAW Redditor object:
        account_age_days = (time.time() - redditor.created_utc) / 86400
        post_count       = redditor.link_karma  (approximate)
        comment_count    = redditor.comment_karma (approximate)
        karma            = redditor.link_karma + redditor.comment_karma
        has_avatar       = redditor.icon_img != ''
        verified_email   = redditor.has_verified_email
    """
    username:         str
    account_age_days: float
    post_count:       int
    comment_count:    int
    karma:            int
    has_avatar:       bool
    verified_email:   bool


def bot_score(profile: AccountProfile) -> dict:
    """
    Compute a bot suspicion score in [0.0, 1.0] from account heuristics.

    Scoring breakdown:
        posts_per_day > 50      +0.30  HIGH_ACTIVITY_RATE
        posts_per_day > 20      +0.15  ELEVATED_ACTIVITY
        account_age_days < 7    +0.25  VERY_NEW_ACCOUNT
        account_age_days < 30   +0.10  NEW_ACCOUNT
        no avatar               +0.10  NO_AVATAR
        unverified email        +0.05  UNVERIFIED_EMAIL
        zero karma + high posts +0.20  ZERO_KARMA_HIGH_POSTS

    Args:
        profile: AccountProfile dataclass with account metadata.

    Returns:
        Dict with keys:
            username   str
            bot_score  float in [0.0, 1.0]  — higher = more suspicious
            flags      list[str]             — triggered heuristics
    """
    flags = []
    score = 0.0

    posts_per_day = (profile.post_count + profile.comment_count) \
                    / max(profile.account_age_days, 1)

    if posts_per_day > 50:
        score += 0.30; flags.append('HIGH_ACTIVITY_RATE')
    elif posts_per_day > 20:
        score += 0.15; flags.append('ELEVATED_ACTIVITY')

    if profile.account_age_days < 7:
        score += 0.25; flags.append('VERY_NEW_ACCOUNT')
    elif profile.account_age_days < 30:
        score += 0.10; flags.append('NEW_ACCOUNT')

    if not profile.has_avatar:
        score += 0.10; flags.append('NO_AVATAR')
    if not profile.verified_email:
        score += 0.05; flags.append('UNVERIFIED_EMAIL')

    if profile.karma <= 0 and profile.post_count > 10:
        score += 0.20; flags.append('ZERO_KARMA_HIGH_POSTS')

    return {
        "username":  profile.username,
        "bot_score": round(min(score, 1.0), 3),
        "flags":     flags,
    }


def posting_regularity(timestamps: list[datetime]) -> dict:
    """
    Detect suspiciously regular posting intervals.

    Organic users post at irregular intervals; coordinated networks or
    bots post in tight, synchronised bursts with very low variance.
    This function measures the coefficient of variation (CV) of inter-post
    gaps: a low CV indicates automated, clock-driven behaviour.

    Args:
        timestamps: List of datetime objects representing post times.
                    Requires at least 3 timestamps.

    Returns:
        Dict with keys:
            mean_interval_s   float   — average seconds between posts
            std_interval_s    float   — standard deviation of intervals
            regularity_score  float   — 0.0 (human) to 1.0 (bot-like)
            verdict           str     — 'SUSPICIOUS' | 'NORMAL' | 'INSUFFICIENT_DATA'
    """
    if len(timestamps) < 3:
        return {
            'regularity_score': 0.0,
            'verdict':          'INSUFFICIENT_DATA',
        }

    sorted_ts = sorted(timestamps)
    gaps = [
        (sorted_ts[i + 1] - sorted_ts[i]).total_seconds()
        for i in range(len(sorted_ts) - 1)
    ]
    mean_gap = statistics.mean(gaps)
    std_gap  = statistics.stdev(gaps)
    cv       = std_gap / mean_gap if mean_gap > 0 else 0

    # Low CV → suspiciously regular; high CV → human-like variation
    regularity = round(max(0.0, 1.0 - cv), 3)

    return {
        "mean_interval_s":  round(mean_gap, 1),
        "std_interval_s":   round(std_gap, 1),
        "regularity_score": regularity,
        "verdict":          'SUSPICIOUS' if regularity > 0.7 else 'NORMAL',
    }


if __name__ == "__main__":
    # Account heuristics
    test = AccountProfile('u/news_alert_247', 3, 412, 88, 1, False, False)
    print("--- Bot score ---")
    print(bot_score(test))

    # Posting regularity
    from datetime import timedelta, timezone
    base      = datetime(2024, 6, 1, 12, 0, tzinfo=timezone.utc)
    bot_times = [base + timedelta(seconds=60 * i + (i % 3)) for i in range(20)]
    print("\n--- Posting regularity (simulated bot) ---")
    print(posting_regularity(bot_times))
