"""
analysis/network.py
Reply-network construction, centrality analysis, and community detection.

Dependencies:
    pip install networkx python-louvain
"""

import networkx as nx
from collections import Counter

try:
    import community as community_louvain
    LOUVAIN_AVAILABLE = True
except ImportError:
    LOUVAIN_AVAILABLE = False


def build_reply_network(comments: list[dict]) -> nx.DiGraph:
    """
    Build a directed graph from a list of Reddit comment dicts.

    An edge  A → B  means user A replied to user B.
    Edge weight is incremented for each additional reply between the
    same pair. Depth-0 comments are treated as replies to 'OP'.

    Args:
        comments: List of dicts as returned by fetch_post_comments().
                  Required keys: comment_id, author, depth.

    Returns:
        nx.DiGraph with node = username, edge weight = reply count.
    """
    G = nx.DiGraph()
    for c in comments:
        author = c['author']
        if author != '[deleted]':
            G.add_node(author)

    for c in comments:
        src = c['author']
        if src == '[deleted]':
            continue
        dst = 'OP' if c['depth'] == 0 else 'thread'
        if G.has_edge(src, dst):
            G[src][dst]['weight'] += 1
        else:
            G.add_edge(src, dst, weight=1)
    return G


def top_accounts_by_centrality(
    G: nx.DiGraph,
    top_n: int = 5,
) -> dict:
    """
    Rank accounts by in-degree centrality and PageRank.

    In-degree centrality: fraction of nodes that reply to this account.
    High in-degree = conversation driver.

    PageRank: propagates importance through the graph.
    High PageRank = cited by other highly-cited accounts.

    Args:
        G:     Directed reply network from build_reply_network().
        top_n: Number of top accounts to return per metric.

    Returns:
        Dict with keys 'in_degree' and 'pagerank', each a list of
        (username, score) tuples sorted descending.
    """
    in_deg   = nx.in_degree_centrality(G)
    pagerank = nx.pagerank(G, weight='weight')
    return {
        'in_degree': sorted(
            in_deg.items(), key=lambda x: x[1], reverse=True
        )[:top_n],
        'pagerank': sorted(
            pagerank.items(), key=lambda x: x[1], reverse=True
        )[:top_n],
    }


def detect_communities(G: nx.DiGraph) -> dict[str, int]:
    """
    Partition the network into communities using the Louvain algorithm.

    Requires the python-louvain package. Communities often correspond to
    ideological camps, geographic groups, or coordinated influence clusters.

    Args:
        G: Directed reply network (converted internally to undirected).

    Returns:
        Dict mapping {username: community_id}.

    Raises:
        ImportError: if python-louvain is not installed.
    """
    if not LOUVAIN_AVAILABLE:
        raise ImportError(
            "python-louvain is required for community detection. "
            "Install it with: pip install python-louvain"
        )
    U         = G.to_undirected()
    partition = community_louvain.best_partition(U)
    return partition


if __name__ == "__main__":
    # Minimal smoke-test with synthetic data
    fake_comments = [
        {"comment_id": "1", "author": "alice", "depth": 0},
        {"comment_id": "2", "author": "bob",   "depth": 1},
        {"comment_id": "3", "author": "alice", "depth": 1},
        {"comment_id": "4", "author": "carol", "depth": 0},
        {"comment_id": "5", "author": "bob",   "depth": 0},
    ]
    G = build_reply_network(fake_comments)
    print(f"Nodes: {G.number_of_nodes()}  Edges: {G.number_of_edges()}")

    result = top_accounts_by_centrality(G)
    print("Top by in-degree:")
    for name, score in result['in_degree']:
        print(f"  {name:<20s} {score:.4f}")
