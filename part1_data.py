"""
Part 1: whose data is this?

    uv run python part1_data.py

Write your own cut rule and your two checks before you run anything here. Doing it in that
order is what Part 1 is asking for. What this script must print, under the labels shown:

    == (a) how much ==
        Rows in each of the four files, distinct users, distinct movies, and the share of
        all 32,000,204 MovieLens ratings this set holds.

    == (b) spread ==
        Ratings per user and ratings per movie: median, minimum and maximum of each. Tag
        applications per user and per movie: the same three. How many of the users who
        rated anything ever applied a tag, as a count and as a share.

    == (c) top tags, two ways ==
        The 20 most-used tags by number of applications, and the 20 most-used tags by number
        of distinct users who applied them. Print the two lists one after the other, with
        both numbers on every row, so you can see where a tag's two ranks differ.

    == (d) two checks ==
        Two claims from (a) to (c) re-derived by a route that does not reuse the code that
        produced them, printed with both numbers side by side and the word MATCH or DIFFER.
        Targets that exist in this data: the share of all 32M ratings the set holds
        (`data/README.md` says 15.6 percent); the number of distinct users who applied a
        tag (14,019); the rating count of the least-rated kept movie (83); the 6 tag
        rows whose text is literally `NA`, which vanish if a reader is built without
        `keep_default_na=False`.

No figures are required in Part 1. `WRITEUP.md` takes one interesting thing from
`data/README.md`, your own cut rule and the rule you rejected, how `data/make_compact.py`'s
rule differs from yours, and your two checks.
"""

import gzip
import re

import pandas as pd

from load_data import DATA, load_all

FULL_RATINGS = 32_000_204


def part1_data(ratings, tags, movies, links):
    print("== (a) how much ==")
    print(f"ratings.csv: {len(ratings):,} rows")
    print(f"tags.csv: {len(tags):,} rows")
    print(f"movies.csv: {len(movies):,} rows")
    print(f"links.csv: {len(links):,} rows")
    print(f"distinct users: {ratings['userId'].nunique():,}")
    print(f"distinct movies: {ratings['movieId'].nunique():,}")
    share = len(ratings) / FULL_RATINGS
    print(f"share of all {FULL_RATINGS:,} MovieLens ratings: {share:.4f} ({share * 100:.1f}%)")

    print("== (b) spread ==")
    per_user_ratings = ratings.groupby("userId").size()
    per_movie_ratings = ratings.groupby("movieId").size()
    per_user_tags = tags.groupby("userId").size()
    per_movie_tags = tags.groupby("movieId").size()

    def stats(s, label):
        print(f"{label}: median {s.median():.1f}, min {s.min()}, max {s.max()}")

    stats(per_user_ratings, "ratings per user")
    stats(per_movie_ratings, "ratings per movie")
    stats(per_user_tags, "tag applications per user")
    stats(per_movie_tags, "tag applications per movie")

    raters = ratings["userId"].unique()
    taggers = tags["userId"].unique()
    n_tagging_raters = pd.Index(raters).isin(taggers).sum()
    print(f"users who rated anything and ever applied a tag: {n_tagging_raters:,} "
          f"of {len(raters):,} ({n_tagging_raters / len(raters):.4f})")

    print("== (c) top tags, two ways ==")
    by_count = tags.groupby("tag").size().rename("times_added")
    by_users = tags.groupby("tag")["userId"].nunique().rename("distinct_users")
    both = pd.concat([by_count, by_users], axis=1)

    print("-- top 20 by times added --")
    top_by_count = both.sort_values("times_added", ascending=False).head(20)
    for tag, row in top_by_count.iterrows():
        print(f"{tag!r}: times_added={row['times_added']}, distinct_users={row['distinct_users']}")

    print("-- top 20 by distinct users --")
    top_by_users = both.sort_values("distinct_users", ascending=False).head(20)
    for tag, row in top_by_users.iterrows():
        print(f"{tag!r}: times_added={row['times_added']}, distinct_users={row['distinct_users']}")

    print("== (d) two checks ==")
    # check 1: distinct users who applied a tag (data/README.md says 14,019),
    # re-derived by grouping tag rows by userId and counting the groups
    claimed_taggers = 14_019
    n_taggers_grouped = tags.groupby("userId").ngroups
    print(f"distinct tagging users: groupby groups {n_taggers_grouped:,} vs README {claimed_taggers:,} -> "
          f"{'MATCH' if n_taggers_grouped == claimed_taggers else 'DIFFER'}")

    # check 2: tag rows whose text is literally NA (load_data.py says 6),
    # re-derived by searching the raw text of the file, grep-style, with no CSV parser
    claimed_na = 6
    na_line = re.compile(r'^\d+,\d+,"?NA"?,\d+$')
    with gzip.open(DATA / "tags.csv.gz", "rt", encoding="utf-8") as f:
        n_na_raw = sum(1 for line in f if na_line.match(line.rstrip("\n")))
    print(f"tag rows that are literally NA: raw text search {n_na_raw:,} vs claimed {claimed_na:,} -> "
          f"{'MATCH' if n_na_raw == claimed_na else 'DIFFER'}")


if __name__ == "__main__":
    ratings, tags, movies, links = load_all()
    part1_data(ratings, tags, movies, links)
