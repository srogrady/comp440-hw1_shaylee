"""
Part 2: what tags best describe a movie?

    uv run python part2_tags.py

Steps 1 to 4 of the handout's Part 2 live here, plus the scores and the rankings that steps 5
and 6 need. The judge itself runs through `/judge`, and its answer is read through
`agreement.py` and `results_viewer.py`. What this script must print, under the labels shown,
and what it must write:

    == (1) the obvious answer ==
        Your chosen movie's title, its rating count and its tag-application count, then
        every tag applied to it with how many times it was applied, most-applied first.
        Pick a movie with at least 500 ratings and 30 tag applications. The most misleading
        entry in that list is your sentence in `WRITEUP.md`, not this script's.

    == (2) up close ==
        The numbers behind the one required figure and the two tables, so that everything
        shown here has printed output a reader can check it against. Write, to `figures/`:

            figures/part2_when.png          when the tags arrived: tag applications over
                                            time, with the movie's ratings over time behind
                                            them.

        The figure has labeled axes and a caption naming the question it answers. Claude
        may draw and label it; the sentence in `WRITEUP.md` about what it shows is yours.

        Then two tables, each printed under its own label:

            who added each tag              the movie's heaviest taggers, how many tag
                                            applications each made, and what share of the
                                            movie's applications that is.
            how the taggers rated it        for each of the movie's top tags, how the
                                            people who applied it rated the movie, beside
                                            how everyone else rated it.

        Claude prints the tables and says what the columns are. What they show is your two
        interesting details in `WRITEUP.md`, not this script's.

    == (3) my definition ==
        Your `score` over the whole set. Write it in this file as

            score(tags_df, ratings_df, movies_df) -> DataFrame[movieId, tag, score]

        one row per movie-tag pair, higher score meaning the tag describes the movie better.
        Print its top 15 rows for your chosen movie, and the number of rows and distinct
        movies it returned over the whole set. Families you could use, none of them
        preferred: distinct users who applied the tag; a rarity weight, the count times how
        few movies carry the tag; a damped version of either; something of your own. Whatever
        you choose, `WRITEUP.md` gets what you chose, what you rejected, and why.

    == (4) cleaning ==
        Whatever cleaning your `score()` does, and its size: how many raw tag strings went
        in, how many distinct tags came out, and the five mergers that absorbed the most
        applications. If you clean nothing, print that and say why in `WRITEUP.md`.
        Merging `Sci-Fi`, `sci-fi` and `scifi` is a decision, and so is not merging them.

    == (5) scores.csv ==
        `scores.csv` in the repo root, columns `movieId,tag,score`, holding a score for every
        movie and tag the judge will be asked about. That is two sets put together:

            every movie and tag in `judge/movies.csv`, which has one row per movie and a
            `tags` column of tags joined by `|`;
            plus, for each of the ten movies in your "My ten movies" slot, every tag from
            `judge/vocabulary.txt` that appears on it, matched after stripping and
            lowercasing, which is the same rule `judge/movies.csv` used.

        The second set matters because the judge adds your ten movies to its list, and
        `agreement.py` compares exactly what the two files share: a tag you never scored is
        dropped without a number. Print how many were asked for and how many you wrote.

    == (6) the four rankings ==
        For each of the ten movies in your "My ten movies" slot, four rankings of the same tags,
        printed one after another and never in one table:

            the counts: the ten most-used tags, by how many times each was applied;
            your own order, from the `WRITEUP.md` slot you filled before seeing any data;
            the judge's order, from `judge/ratings_movies.csv`;
            your `score()`'s order.

        Print each list under its own heading, best first. `results_viewer.py` builds the same
        four lists as a page you can read. Which tag is the artifact, and what the
        disagreements mean, is your paragraph in `WRITEUP.md`.
"""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

from load_data import load_all

MY_MOVIE = 104  # Happy Gilmore (1996), the movie I claimed for Part 2


def clean_tag(tag):
    """My merge rule: two strings are one tag when they match after lowercasing and
    stripping leading and trailing spaces. Nothing else changes; inner punctuation and
    prefixes like `sport:` stay as typed."""
    return tag.strip().lower()


def score(tags_df, ratings_df, movies_df):
    """My score(movie, tag), on case-merged tags with their counts summed.

    Step A: a tag passes for a movie if its count on that movie is at least that movie's
    mean count per (merged) tag.
    Step B: a passing tag scores the number of distinct movies in the whole set carrying it.
    A tag that fails step A is kept and scores 0, so it ranks below every passing tag.
    """
    counts = (tags_df.assign(tag=tags_df["tag"].map(clean_tag))
              .groupby(["movieId", "tag"]).size().rename("count").reset_index())
    movie_mean = counts.groupby("movieId")["count"].transform("mean")
    n_movies = counts.groupby("tag")["movieId"].transform("nunique")
    counts["score"] = n_movies.where(counts["count"] >= movie_mean, 0)
    return counts[["movieId", "tag", "score"]]


def my_ten_movies():
    """movieIds from the "My ten movies" slot in WRITEUP.md, one `movieId, title` per line."""
    slot = Path("WRITEUP.md").read_text(encoding="utf-8").split("**My ten movies:**")[1]
    slot = slot.split("**My own order")[0]
    return [int(line.split(",")[0]) for line in slot.splitlines() if line[:1].isdigit()]


def part2_tags(ratings, tags, movies, links):
    print("== (1) the obvious answer ==")
    title = movies.set_index("movieId").loc[MY_MOVIE, "title"]
    my_tags = tags[tags["movieId"] == MY_MOVIE]
    print(f"{title}: {(ratings['movieId'] == MY_MOVIE).sum():,} ratings, "
          f"{len(my_tags):,} tag applications")
    # raw strings, exactly as typed: `Underdog` and `underdog` are separate rows here
    for tag, n in my_tags["tag"].value_counts().items():
        print(f"{n:4d}  {tag!r}")

    print("== (2) up close ==")
    # the figure: tag applications and ratings per year, two panels on a shared year axis
    my_ratings = ratings[ratings["movieId"] == MY_MOVIE]
    tag_years = pd.to_datetime(my_tags["timestamp"], unit="s").dt.year.value_counts().sort_index()
    rating_years = pd.to_datetime(my_ratings["timestamp"], unit="s").dt.year.value_counts().sort_index()
    years = range(min(tag_years.index.min(), rating_years.index.min()),
                  max(tag_years.index.max(), rating_years.index.max()) + 1)
    per_year = pd.DataFrame({"tag_applications": tag_years, "ratings": rating_years}).reindex(years, fill_value=0)
    per_year = per_year.fillna(0).astype(int)
    print("-- per year, the numbers behind figures/part2_when.png --")
    print(per_year.to_string())

    fig, (ax_t, ax_r) = plt.subplots(2, 1, sharex=True, figsize=(9, 6))
    ax_t.bar(per_year.index, per_year["tag_applications"], color="#2a78d6", width=0.8)
    ax_t.set_ylabel("tag applications per year")
    ax_r.bar(per_year.index, per_year["ratings"], color="#eb6834", width=0.8)
    ax_r.set_ylabel("ratings per year")
    ax_r.set_xlabel("year")
    for ax in (ax_t, ax_r):
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis="y", color="#e0dfdb", linewidth=0.8)
        ax.set_axisbelow(True)
    fig.suptitle(f"{title}: when did its tags and its ratings arrive?")
    fig.text(0.5, 0.005, "Top: tag applications per year. Bottom: ratings per year. "
             "Separate y-scales, shared year axis.", ha="center", fontsize=9, color="#52514e")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    Path("figures").mkdir(exist_ok=True)
    fig.savefig("figures/part2_when.png", dpi=150)
    plt.close(fig)
    print("wrote figures/part2_when.png")

    # table 1: who added each tag. Every tagger of the movie, most applications first,
    # with their own rating of the movie (blank if they tagged it without rating it)
    my_rating_by_user = my_ratings.groupby("userId")["rating"].last()
    taggers = my_tags.groupby("userId").agg(tag_applications=("tag", "size"),
                                             distinct_tags=("tag", "nunique"))
    taggers["share_of_movie"] = (taggers["tag_applications"] / len(my_tags)).round(3)
    taggers["their_rating"] = my_rating_by_user.reindex(taggers.index)
    taggers = taggers.sort_values("tag_applications", ascending=False)
    print(f"-- who added each tag: {len(taggers):,} taggers, most applications first --")
    print(taggers.to_string())

    # table 2: how the taggers rated it. For each of the ten most-used raw tag strings,
    # the ratings of the movie by people who applied that tag vs by every other rater
    top_ten = my_tags["tag"].value_counts().head(10).index
    rows = []
    for tag in top_ten:
        appliers = my_tags.loc[my_tags["tag"] == tag, "userId"].unique()
        rated = my_rating_by_user.index.isin(appliers)
        rows.append({"tag": tag, "appliers": len(appliers),
                     "appliers_who_rated": int(rated.sum()),
                     "appliers_mean_rating": round(my_rating_by_user[rated].mean(), 2),
                     "everyone_else_n": int((~rated).sum()),
                     "everyone_else_mean_rating": round(my_rating_by_user[~rated].mean(), 2)})
    print("-- how the taggers rated it: ten most-used raw tag strings --")
    print(pd.DataFrame(rows).to_string(index=False))

    print("== (3) my definition ==")
    scores = score(tags, ratings, movies)
    mine = scores[scores["movieId"] == MY_MOVIE].sort_values("score", ascending=False)
    print(f"-- top 15 for {title} --")
    print(mine.head(15).to_string(index=False))
    print(f"score() returned {len(scores):,} rows over {scores['movieId'].nunique():,} movies")

    print("== (4) cleaning ==")
    raw_in = tags["tag"].nunique()
    cleaned = tags["tag"].map(clean_tag)
    print("rule: lowercase + strip leading/trailing spaces, counts summed; nothing else changed")
    print(f"raw tag strings in: {raw_in:,}; distinct tags out: {cleaned.nunique():,}")
    groups = (tags.assign(clean=cleaned).groupby("clean")
              .agg(variants=("tag", "nunique"), applications=("tag", "size"),
                   spellings=("tag", lambda x: sorted(x.unique()))))
    merged = groups[groups["variants"] > 1].sort_values("applications", ascending=False)
    print(f"{len(merged):,} tags were formed by merging two or more raw strings; "
          "the five that absorbed the most applications:")
    for clean, row in merged.head(5).iterrows():
        print(f"  {clean!r}: {row['applications']:,} applications from {row['spellings']}")

    print("== (5) scores.csv ==")
    # what the judge will be asked about: every movie and tag in judge/movies.csv, plus
    # every vocabulary tag on each of my ten movies, matched after strip + lowercase
    judge_movies = pd.read_csv("judge/movies.csv", keep_default_na=False)
    asked = (judge_movies.assign(tag=judge_movies["tags"].str.split("|"))
             .explode("tag")[["id", "tag"]].rename(columns={"id": "movieId"}))
    vocab = set(Path("judge/vocabulary.txt").read_text(encoding="utf-8").split("\n")) - {""}
    ten = my_ten_movies()
    on_ten = tags[tags["movieId"].isin(ten)].assign(tag=lambda d: d["tag"].str.strip().str.lower())
    on_ten = on_ten[on_ten["tag"].isin(vocab)][["movieId", "tag"]].drop_duplicates()
    asked = pd.concat([asked, on_ten]).drop_duplicates().reset_index(drop=True)
    out = asked.merge(scores, on=["movieId", "tag"], how="left")
    missing = out["score"].isna()
    out = out[~missing]
    out.to_csv("scores.csv", index=False)
    print(f"pairs asked for: {len(asked):,} ({judge_movies['id'].nunique()} judge movies + "
          f"{len(ten)} of mine); scores written: {len(out):,}; no score found: {int(missing.sum()):,}")
    if missing.any():
        print(asked[missing.values].to_string(index=False))

    print("== (6) the four rankings ==")


if __name__ == "__main__":
    ratings, tags, movies, links = load_all()
    part2_tags(ratings, tags, movies, links)
