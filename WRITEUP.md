# HW1 writeup

**Name:** Shaylee
**Date:** Thursday, Sep 17, 2026

Every placeholder below gets your answer, told to Claude or typed in here yourself. Every number
you give comes from a script in this repo; say which one. Claude may format tables and figures
here; the words are yours.

## Part 0. Predictions

Give these to Claude before any analysis runs. One sentence each, plus one sentence on why you
think so.

**(1) A movie you know well, and what its three most-used tags will be:** Tangled, and its three most-used tags will be Disney, Cute, Animated

**(1) Why you think so:** those are key identifiers about the movie and how I think about it

**(2) Out of every 100 people who rated movies here, how many ever added a tag?** 23

**(2) Why you think so:** It is kind of annoying and I wouldn't expect people to go out of their way to do so

**(3) Can one person's tags take over a movie's tag list? Yes or no:** No

**(3) Why you think so:** it should be based off of tag repetition

## Part 1. Whose data is this?

Code: `part1_data.py`.

**My rule for cutting 32 million ratings to 5 million** (written before reading `data/make_compact.py`)**:** Find how the ratings (5 stars) are distributed and make sure to keep the same weights as you scale it down proportionally. Ex. If there were a lot of 5 stars or 1 stars in the original 32 mil then those should be the majority of the 5 mil too.

**One rule I considered and rejected, and why:** I considered doing top ratings, but that would'nt get very much nuance.

**One interesting thing from `data/README.md`:** the random sample of non-taggers that finishes up the count.

**How the script's rule differs from mine, and what each keeps that the other drops:** It differs because it takes a certain amount of top rated movies and then prioritizes ratings. Mine keeps the weights of ratings so the data still is representative, but the script's rule keeps the most important ratings.

**First check. Which of Claude's numbers, the different route you took, and whether it matched** (one good target: 6 tags are the literal text `NA`, which pandas drops unless told not to)**:** I checked the number of taggers by grouping them by their userids and then count the number of counts and it ended up matching which 14,019 taggers using the data from part1_data.py

**Second check. Which of Claude's numbers, the different route you took, and whether it matched:** I checked the number of tags that are NA's by search the raw text for "NA" values exactly, and it matched with finding 6 values even though I thought it may not match because of values like "na" or "N/A"

## Part 2. What tags best describe a movie?

Code: `part2_tags.py`.

**My movie, and why I picked it:** I picked Happy Gilmore because it is a chaotic movie that can be described or tagged in many different ways, so I thought it would be an interesting example

**Its most misleading tag in the count-ordered list, and why it misleads:** the underdog and Underdog was misleading. It is misleading because the only difference between the two is that the first letter is capitalized in one case and not in the other. So, how do you know which one to tag when it is only a writing style difference.

**What I learned about how MovieLens collects ratings and tags, from rating and tagging my movie myself (about 100 words):** It's very easy to add a tag once you click into a movie so that is accessible, and then it keeps your tag in a "your tags" section, and then you can say if you like thats attribute (the tag) about the movie or if that tag was a bad thing, and as for ratings it very easy and fun to hover over and rate the movie in seconds, and it gives a word adjective with the number.

### Up close

One sentence on the figure written before you saw it and one after. The two tables are where the
details below come from. Say which script made them.

**The figure, when the tags and the ratings arrived. What I expected:** i think the higher the ratings the more the tags
**The figure, what it shows:** The figure shows that it took about 10 years of ratings to get it to start being tagged into categories. It also shows that tagging may have been trending during 2011 or so when number of new ratings was lower. After 2010 both ratings and tagging is happening pretty consistantly.

**Two interesting details I learned up close that the counts did not show:** One interesting detail is that the top two tag contributors have two really high movie ratings, and also the mean ratings of taggers are around 3 and 4

**Anything up close that contradicted something I had already written down. Which one, what the data showed, and what you now think. Or "nothing yet":** From my original prediction the data didn't completely prove that high ratings are given by highly active taggers. Instead I now think that the ratings are pretty randomly distributed throughout, and the number of tags don't directly correlate to the movie rating.

### My definition

**My `score(movie, tag)`** (one or two sentences, precise enough that a classmate could code it)**:** Take the specific tags for one individual movie and the mean count per tag for that movie is the floor for what tags are important then, compare to the most popular tags of all the movies and you want the tags that are most common amoung all the movies, so that it can help you find movies you should watch next or avoid next

**One definition I considered and rejected, and why:** I considered scoring based on unique tags because those tell you more about a movie, but I decided against it because sometimes they are hard to understand and there are too many unique ones to really show anything about the quality of the tag

**Which tags I merged as the same tag, which I kept apart, and why:** I merged the tags that were the same just with different letter cases only because then they were saying the same thing. Although there were some weird cases I decided to let those be because there were too many one off cases to track. I also striped leading and trailing spaces.

**Why my definition, in about 150 words. Name one thing it gains and one thing it loses:**

I choose my definition, because I feel like the reason for tagging movies is to describe in short what that movies main characteristics are, and that helps you decide whether or not you want to watch it. A good tag is helpful when you are able to look at a movie that you know you like and read it's tags, and then use those tags to search for a movie with similar ones so that you can find another movie you will like. My score gains ability to help users find their next movie, but it looses the unique tags that truly explain what a movie uniquely is about.

### The judge

The two slots below are read by scripts, so write them as bare lines: one item to a line, the
movieId first, no bullets and no numbering. A movie line looks like `296, Pulp Fiction (1994)`.
An order line looks like `296: nonlinear, hit men, dark comedy, ...`, the tags best first.

**My ten movies:**

104, Happy Gilmore (1996)
3988, How the Grinch Stole Christmas (a.k.a. The Grinch) (2000)
93272, Dr. Seuss' The Lorax (2012)
72226, Fantastic Mr. Fox (2009)
53460, Surf's Up (2007)
45431, Over the Hedge (2006)
114180, Maze Runner, The (2014)
122906, Black Panther (2017)
106696, Frozen (2013)
81847, Tangled (2010)

**My own order of the ten most-used tags, written before looking at any data: my movie from step 1, then my nine others from step 4:**

104: comedy, Adam Sandler, funny, golf, sports, Underdog, underdog, Bob Barker, seen more than once, goofy
3988: holiday, based on a book, silly, christmas, dr. seuss, xmas theme, jim carrey, christine baranski, taylor momsen, ron howard
93272: reforestation, Dr. Seuss, nature, environmental, based on children's book, Commercialization, computer animation, Environmental Preservation, based on a book, business
72226: hilarious, Wes Anderson, animation, Bill Murray, Roald Dahl, stop motion, quirky, talking animals, visually appealing, George Clooney
53460: fun, Zooey Deschanel, Below R, mockumentary, penguin, positive, ocean, fresh story, surfing, talking animals
45431: suburbia, talking animals, William Shatner, Steve Carell, Bruce Willis, Wanda Sykes, Funny, Dreamworks, computer animation, cartoon
114180: post-apocalyptic, plot holes, dystopia, teen, survival, action, weak plot, maze, adventure, based on a book
122906: marvel, great villain, Africa, strong female characters, diverse cast, , predictable, MCU, great costumes, social commentary, superhero
106696: Disney, animation,siblings,beautiful, music, sisters, feminist, magic, musical, overrated
81847: disney, Disney,  comedy, mother daughter relationship, songs, fairy tale, visually appealing, animation, musical, singing

**One criterion I considered for the judge and rejected, and why** (the one I used is in `judge/criterion.md`)**:** One that helps you find other movies to watch and correctly describes the movie its assigned to. I rejected it because I didn't want to judge to agree with me exactly

**Agreement. The number `agreement.py` gives for your `score()`, for popularity and for your own order, and which of the three came closest to the judge:** popularity(4.26) is the closet one, while score comes in closely behind at 4.08 and then my own order is last at 3.20 meaning the judge agreed least with my order.

**How the judge skill is built: the files it is made of and what each one does (about 150 words):**

SKILL.md tells the judge what to read, README.md explains the process, system.md gives the judge its rules, judge.py runs the actual judging, and criterion.md provides the specific criterion being judged.

**What happens when I run `/judge`, from the first check to the CSV (about 150 words):**

When I run /judge, it first checks that all the needed files exist and that my criterion has been changed from the template. Then it reads the instructions and my ten movies, and tells me what it is going to ask. It sends each movie to Claude to be rated, checks that the responses have the correct tag and rating format, and re-asks any movie if the response is too short. Finally, it saves all the ratings in a CSV file and shows the cost and time it took.

**Why a skill: what a skill like this gives you that a script or a prompt alone does not, and where you would use one next (about 100 words):**

A skill like this is useful because it combines the instructions, prompts, and code into one repeatable process. A script or prompt alone would not provide the same structure and consistency for running the judge and checking the results.

I would use a skill like this when I have a repetitive task that needs the same process each time, such as evaluating multiple movies, comparing items using the same criteria, or analyzing a set of responses

### The viewer and the disagreements

**One thing `movie_results.html` showed me that was useful, and one thing about it that got in my way:** the comparison of judges order vs my order being so close was helpful, and then what got in my way was the long blocks of tags on the movie

Then three improvements. For each: what the page would not let you see, what you had Claude
change, and what the changed page shows that the first draft did not.

**Improvement 1:** The long tag blocks hurt me from seeing everything because it made it hard to scroll so the fixed page should so a preview of the table and then my collapsible. Improvement one was about allowing for a better viewing experience

**Improvement 2:** improvement 2 is a comparison edit to show the common selections between the judge and your score sections. they should be side by side and then also have a check next to them if that tag appears in both, because currently its hard to tell if the judge and my score are similar

**Improvement 3:** the last improvement is about getting to the movies you want to look at faster, and easier. there should be a glossary that allows you to click to that movie at the top, because currectly you don't know what movies you are researching, or what the order is

Then the three disagreements. A disagreement is a movie and a tag where your `score()` and the
judge are furthest apart. For each: the movie and the tag, where your `score()` put it and where
the judge put it, and what you think accounts for the gap.

**Disagreement 1:** Tangled, comedy and I think the gap is because of my mean tag score part

**Disagreement 2:** Now Fantastic Mr Fox, creepy, I think the biggest disagreement was because a lot of people disagree on what the movie experience was like

**Disagreement 3:** disagreement 3 is with how the grinch stole christmas and it is with the fantasy tag and it has only one disagreement row, so it doesn't give that muhc room for error

**One other high-level pattern in the results, and what you think is behind it:** There is a large variety of different numbers of tags for each movie, so it's hard to compare correctness between the my score and the judges score across movies because some have only three tags to go off of and some have 10

## Predictions revisited

**Which of my three predictions were wrong, and what I make of each miss:** the first two are wrong and the first miss shows how similar adjectives can be, but also that people think of similar ideas in slightly different ways. The second is showing that more people tag movies than I thought.

## Part 3. What tags best describe a user?

Code: `part3_users.py`.

The slot below is read by a script, so write it as bare lines: one rating to a line, no bullets
and no numbering, the movieId first and the rating last, as in `296, Pulp Fiction (1994), 4.5`.

**My 20 ratings:**

XXXX

**My `score(user, tag)`, in a sentence, and why I started there (about 100 words):**

XXXX

**What my score says about me: my top ten tags, and whether they describe my taste (about 100 words):**

XXXX

**What my user viewer shows and why I chose that (about 100 words):**

XXXX

**What I put in the description column for a person, and why (about 150 words):**

XXXX

**My criterion for people: what it asks the judge to do that the movie criterion did not (about 60 words):**

XXXX

**The user-tag pairs I chose to judge, how many, and why those (about 100 words):**

XXXX

**Improvement 1: what I changed in the scoring function, what the judge and the viewer showed before and after (about 150 words):**

XXXX

**Improvement 2: the same (about 150 words):**

XXXX

## Part 4. Working with Claude

Give these to Claude the way you gave it the rest. Graded on the catch and the candor, not on
making Claude look good or bad.

**A moment where Claude was wrong or overconfident, how you caught it, and where it
happened. Name the part and the step, so the moment can be found:** XXXX

**One call where you overrode Claude, and why:** XXXX

**What you would hand to Claude sooner next time:** XXXX

**Did Claude name the misleading tag in Part 2 step 1 before you did? What happened:** XXXX

**The figure. Would asking Claude "what does this show?" have produced your sentence, and what
would have been missing from it:** XXXX

**Hours spent:** XXXX

**Anyone who helped you, or "no one":** XXXX
