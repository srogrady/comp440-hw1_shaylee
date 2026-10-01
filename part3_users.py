"""
Part 3: what tags best describe a user?

    uv run python part3_users.py

The handout's Part 3 is the spec. One piece is written for you, the piece that has to agree
with `WRITEUP.md` line for line: reading the 20 ratings out of your "My 20 ratings" slot and
adding you to the ratings table as a user of your own. Everything after that is yours.

You are added under userId 999999. Real userIds in `data/ratings.csv.gz` stop at 200,935, so
that number cannot be a real person's, and it is easy to pick out of a printout.

What this script must print, under the labels shown:

    == (1) my ratings ==
        How many ratings were read out of your slot, how many lines it could not read a
        rating from, and how many rows the ratings table has with yours in it. Twenty
        ratings is what the handout asks for; the script reports what it found and leaves
        the count to you.

    == (2) score(user, tag) ==
        Your `score(user, tag)` over the users you are looking at, your own row included.
        Write it in this file as

            score(ratings_df, tags_df, movies_df) -> DataFrame[userId, tag, score]

        one row per user-tag pair, higher score meaning the tag describes the user better.
        Print your own ten best tags, and the number of rows and distinct users it returned.
        What the score is, and why you started there, is yours and goes in `WRITEUP.md`.
"""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

from load_data import load_all

REPO = Path(__file__).resolve().parent
WRITEUP = REPO / "WRITEUP.md"

ME = 999999                 # your userId: above every real one, so it collides with nobody
SLOT = "My 20 ratings"      # the WRITEUP.md slot your ratings are read from


def read_my_ratings(writeup: Path = WRITEUP) -> tuple[pd.DataFrame, int]:
    """Your ratings from the "My 20 ratings" slot in WRITEUP.md, as movieId and rating.

    The same rule the judge uses for "My ten movies": every line in that slot starts with a
    movieId. The rating is the last number on the line, so the title between them is for
    people and may hold anything, the year included. Bare lines only: a bulleted or a
    numbered list reads as no ratings at all, or reads the list numbers as movieIds.

        296, Pulp Fiction (1994), 4.5

    A line whose last number is not a rating between 0.5 and 5.0 is left out and counted,
    because the year in a title is a number too: `296, Pulp Fiction (1994)` with the rating
    forgotten would otherwise be read as a rating of 1994. So is the `XXXX` an unfilled slot
    holds, which is why this is safe to run before you have written anything.

    Returns the ratings and how many lines were left out."""
    rows, skipped, inside = [], 0, False
    for line in writeup.read_text(encoding="utf-8").splitlines():
        if line.startswith("**"):            # a bold label opens the next slot
            inside = SLOT in line
            continue
        if not inside or not re.match(r"\s*\d", line):
            continue
        numbers = re.findall(r"\d+(?:\.\d+)?", line)
        rating = float(numbers[-1]) if len(numbers) > 1 else 0.0
        if not 0.5 <= rating <= 5.0:
            skipped += 1
            continue
        rows.append({"movieId": int(numbers[0].split(".")[0]), "rating": rating})
    return pd.DataFrame(rows, columns=["movieId", "rating"]), skipped


def add_me(ratings: pd.DataFrame, mine: pd.DataFrame) -> pd.DataFrame:
    """Your ratings appended to everybody else's, under userId ME.

    The timestamp is the newest one in the data: you rated these after everyone else did."""
    if mine.empty:
        return ratings
    mine = mine.assign(userId=ME, timestamp=int(ratings["timestamp"].max()))
    return pd.concat([ratings, mine[ratings.columns]], ignore_index=True)


# ------------------------------------------------------------------- yours to write ---

def clean_tag(tag):
    """My merge rule from Part 2: one tag when the strings match after stripping leading and
    trailing spaces and lowercasing."""
    return tag.strip().lower()


def score_v0(ratings: pd.DataFrame, tags: pd.DataFrame, movies: pd.DataFrame):
    """My first score(user, tag), kept for before-and-after: how many of the movies the user rated 4 or higher carry that tag
    at least 3 times, counted after my merge rule. Higher means the tag describes the user
    better. Vectorized: one merge of liked ratings onto qualifying movie-tag pairs."""
    counts = (tags.assign(tag=tags["tag"].map(clean_tag))
              .groupby(["movieId", "tag"]).size().rename("count").reset_index())
    fits = counts[counts["count"] >= 3][["movieId", "tag"]]
    liked = ratings.loc[ratings["rating"] >= 4, ["userId", "movieId"]]
    pairs = liked.merge(fits, on="movieId")
    return pairs.groupby(["userId", "tag"]).size().rename("score").reset_index()


def score_v1(ratings: pd.DataFrame, tags: pd.DataFrame, movies: pd.DataFrame):
    """Improvement 1, kept for before-and-after: broad tags are penalised gently.
    count = score_v0 (the user's 4+ movies carrying the tag 3+ times); a tag needs a count of
    at least 3; then score = count / sqrt(P), P = number of users with that tag in score_v0."""
    v0 = score_v0(ratings, tags, movies)
    popularity = v0.groupby("tag")["userId"].transform("size")
    out = v0[v0["score"] >= 3].copy()
    out["score"] = out["score"] / popularity[out.index] ** 0.5
    return out


def score(ratings: pd.DataFrame, tags: pd.DataFrame, movies: pd.DataFrame):
    """My score(user, tag), improvement 2: improvement 1 times how concentrated the tag is.
    count = score_v0; the minimum count is now 2;
    score = count / sqrt(P) * (count / M), P = users with the tag in score_v0,
    M = all movies carrying the tag 3+ times (after my merge rule)."""
    v0 = score_v0(ratings, tags, movies)
    popularity = v0.groupby("tag")["userId"].transform("size")
    counts = (tags.assign(tag=tags["tag"].map(clean_tag))
              .groupby(["movieId", "tag"]).size())
    movies_with_tag = counts[counts >= 3].reset_index().groupby("tag").size()
    out = v0[v0["score"] >= 2].copy()
    concentration = out["score"] / out["tag"].map(movies_with_tag)
    out["score"] = out["score"] / popularity[out.index] ** 0.5 * concentration
    return out


def write_users_csv(scores, tags, path=REPO / "judge" / "users.csv"):
    """judge/users.csv, as I specified it:
    people: 100 users who have tagged, drawn at random under seed 440 (I am left out);
    description: "most common tag that user uses: X", X their most-applied tag after my
        merge rule, ties broken alphabetically;
    tags: their top five vocabulary tags under my score(user, tag), ties alphabetical."""
    vocab = set((REPO / "judge" / "vocabulary.txt").read_text(encoding="utf-8").split("\n")) - {""}
    taggers = pd.Series(sorted(tags["userId"].unique())).sample(100, random_state=440)
    own = tags[tags["userId"].isin(taggers)].assign(tag=lambda d: d["tag"].map(clean_tag))
    own = own.groupby(["userId", "tag"]).size().rename("n").reset_index()
    most_used = (own.sort_values(["userId", "n", "tag"], ascending=[True, False, True])
                 .groupby("userId").head(1).set_index("userId")["tag"])
    top = scores[scores["userId"].isin(taggers) & scores["tag"].isin(vocab)]
    top = (top.sort_values(["userId", "score", "tag"], ascending=[True, False, True])
           .groupby("userId").head(5).groupby("userId")["tag"].apply("|".join))
    rows = pd.DataFrame({"id": sorted(taggers)})
    rows["description"] = "most common tag that user uses: " + rows["id"].map(most_used)
    rows["tags"] = rows["id"].map(top).fillna("")
    rows.to_csv(path, index=False)
    n_tags = rows["tags"].str.split("|").map(lambda t: len([x for x in t if x]))
    print(f"wrote judge/users.csv: {len(rows)} people, {int(n_tags.sum())} tag ratings to ask for; "
          f"people with fewer than 5 tags: {int((n_tags < 5).sum())}")
    return rows


def side_by_side(scores, new_scores=None, path=REPO / "judge" / "ratings_users.csv"):
    """My score next to the judge's rating on every pair I asked the judge about.
    A disagreement is measured, per person, as the count of their five tags the judge
    rated 4 or 5: fewer approved tags means more disagreement."""
    asked = pd.read_csv(REPO / "judge" / "users.csv", keep_default_na=False)
    asked = (asked.assign(tag=asked["tags"].str.split("|")).explode("tag")
             .query("tag != ''")[["id", "tag"]].rename(columns={"id": "userId"}))
    judged = pd.read_csv(path, keep_default_na=False).rename(columns={"id": "userId"})
    judged = judged.drop_duplicates(["userId", "tag"])  # the judge keeps the first answer too
    pairs = (asked.merge(scores, on=["userId", "tag"], how="left")
             .merge(judged, on=["userId", "tag"], how="left"))
    extra = len(judged.merge(asked, on=["userId", "tag"], how="left", indicator=True)
                .query("_merge == 'left_only'"))
    print(f"pairs asked: {len(asked)}; judged: {int(pairs['rating'].notna().sum())}; "
          f"judge rows for tags never asked: {extra}")
    pairs["approved"] = pairs["rating"] >= 4
    if new_scores is not None:
        # what moves: the same judged pairs under the current score (blank = dropped by it)
        pairs = pairs.merge(new_scores.rename(columns={"score": "new_score"}),
                            on=["userId", "tag"], how="left")
        print(f"judged pairs the current score still scores: {int(pairs['new_score'].notna().sum())} "
              f"of {len(pairs)}")
    per = pairs.groupby("userId").agg(tags=("tag", "size"), approved=("approved", "sum"))
    print(f"judge-approved tags per person, averaged: {per['approved'].mean():.2f} "
          f"of {per['tags'].mean():.2f}, over {len(per)} people")
    print("-- people by approved count, fewest first --")
    print(per.sort_values(["approved", "tags"]).head(10).to_string())
    print("-- every pair: my score beside the judge --")
    print(pairs.sort_values(["userId", "score"], ascending=[True, False]).to_string(index=False))
    return pairs


def part3_users(ratings, tags, movies, links):
    print("== (1) my ratings ==")
    mine, skipped = read_my_ratings()
    print(f'{len(mine)} rating(s) read from the "{SLOT}" slot in WRITEUP.md.')
    if not len(mine):
        print(f'Nothing was read out of the "{SLOT}" slot. It is read one rating to a line, '
              f"with no bullets and no numbering: the movieId first, then the title, then "
              f"your rating, as in `296, Pulp Fiction (1994), 4.5`.")
    if skipped:
        print(f"{skipped} line(s) in that slot had no rating between 0.5 and 5.0 at the "
              f"end and were left out.")
    ratings = add_me(ratings, mine)
    if len(mine):
        print(f"{len(ratings):,} ratings with yours in, as userId {ME}.")
    else:
        print(f"{len(ratings):,} ratings, none of them yours yet.")

    print("== (2) score(user, tag) ==")
    before = score_v0(ratings, tags, movies)
    middle = score_v1(ratings, tags, movies)
    scores = score(ratings, tags, movies)
    for label, sc in [("first (score_v0)", before), ("improvement 1 (score_v1)", middle),
                      ("now (score, improvement 2)", scores)]:
        me = sc[sc["userId"] == ME].sort_values(["score", "tag"], ascending=[False, True])
        print(f"-- my ten best tags, {label} --")
        print(me.head(10).to_string(index=False))
    print(f"score() returned {len(scores):,} rows over {scores['userId'].nunique():,} users")

    print("== (3) judge/users.csv ==")
    # written once: the judge has rated this file, so a later score() must not rewrite it
    if (REPO / "judge" / "users.csv").exists():
        print("judge/users.csv already written and judged; left as it is")
    else:
        write_users_csv(before, tags)

    print("== (4) my score beside the judge ==")
    side_by_side(before, scores)


if __name__ == "__main__":
    ratings, tags, movies, links = load_all()
    part3_users(ratings, tags, movies, links)
