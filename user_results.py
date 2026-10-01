"""User viewer for Part 3.

    uv run python user_results.py            # writes user_results.html
    uv run python user_results.py --text     # the same content as plain text

For me and nine users drawn at random under seed 440, it shows what I chose to see about a person:

    * their top tag under my score(user, tag), ties broken alphabetically;
    * their top 5 movies, highest rating first, ties broken alphabetically by title.

My score and my ratings come from part3_users.py, so the page and the script never disagree.
"""

import argparse
import html
from pathlib import Path

import pandas as pd

from load_data import load_all
from part3_users import ME, add_me, read_my_ratings, score

SEED = 440    # the other nine are drawn at random from every real user, under this seed
TOP_MOVIES = 5

CSS = """body { font-family: Helvetica, Arial, sans-serif; margin: 20px; }
h2 { margin-bottom: 4px; }"""


def build():
    ratings, tags, movies, links = load_all()
    mine, _ = read_my_ratings()
    ratings = add_me(ratings, mine)
    scores = score(ratings, tags, movies)
    others = (pd.Series(sorted(ratings.loc[ratings["userId"] != ME, "userId"].unique()))
              .sample(9, random_state=SEED).tolist())
    users = [ME] + others
    titles = movies.set_index("movieId")["title"]
    out = []
    for user in users:
        theirs = scores[scores["userId"] == user].sort_values(["score", "tag"],
                                                              ascending=[False, True])
        top_tag = (theirs.iloc[0]["tag"], float(theirs.iloc[0]["score"])) if len(theirs) else None
        rated = ratings[ratings["userId"] == user].assign(
            title=lambda d: d["movieId"].map(titles))
        rated = rated.sort_values(["rating", "title"], ascending=[False, True])
        out.append({"user": user, "n_ratings": len(rated), "top_tag": top_tag,
                    "movies": list(zip(rated["title"].head(TOP_MOVIES),
                                       rated["rating"].head(TOP_MOVIES)))})
    return out


def render(users):
    body = ["<h1>User viewer</h1>"]
    for u in users:
        label = "me" if u["user"] == ME else "user %d" % u["user"]
        tag = ("%s (score %.5f)" % (html.escape(u["top_tag"][0]), u["top_tag"][1])
               if u["top_tag"] else "no tag scored")
        body += ["<h2>%s</h2>" % label,
                 "<p>%d ratings. Top tag under my score: <b>%s</b></p>" % (u["n_ratings"], tag),
                 "<ol>%s</ol>" % "".join("<li>%s, %s</li>" % (html.escape(t), r)
                                         for t, r in u["movies"])]
    return ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            "<title>User viewer</title>\n<style>\n%s\n</style>\n</head>\n<body>\n%s\n"
            "</body>\n</html>\n" % (CSS, "\n".join(body)))


def render_text(users):
    lines = []
    for u in users:
        label = "me" if u["user"] == ME else "user %d" % u["user"]
        tag = "%s (score %.5f)" % u["top_tag"] if u["top_tag"] else "no tag scored"
        lines += ["%s, %d ratings. Top tag: %s" % (label, u["n_ratings"], tag)]
        lines += ["  %d. %s, %s" % (i, t, r) for i, (t, r) in enumerate(u["movies"], 1)]
        lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--text", action="store_true")
    args = parser.parse_args()
    users = build()
    if args.text:
        print(render_text(users))
    else:
        path = Path(__file__).resolve().parent / "user_results.html"
        path.write_text(render(users), encoding="utf-8")
        print("wrote", path)


if __name__ == "__main__":
    main()
