Random Words
==============


A simple random language generator.  When fed a corpus one document at a time, this program will collect the frequencies with which words follow each other.  Then, given a random word, or a random seed, will generate language in the fashion of a simple markov chain.

The original inspiration was from an episode of the Linear Digressions podcast about markov chains and making a Kanye West generator, so special thanks to Udacity and Linear Digressions.


**Disclaimer:**
The lyrics in the test files are not my property and are being used only for research.


### Example Use:

```python
from random_words.random_words import *
import os

# Get com data
kanye_dir = os.path.join("tests", "data", "kanye")

# Build a model that attaches newlines to tokens
# and doesn't read in duplicate lines
rw = RandomWords(corpus_dir=kanye_dir, newlines=True, uniq_lines=True)

# Build a second model that gets rid of newlines
rw2 = RandomWords(corpus_dir=kanye_dir, newlines=False, uniq_lines=True)

```

#### Output from rw1

`print rw.make_words(100)`

<pre>
we had packed the presidito
ovito
game getting foul so offended
am so you haters and hot girl
go through too much is like to be compared to that sometimes, man ridiculous
wishes, thirty mill in here, baby
bright, I can't study war
no I know what I talk to do now?
the bar up
touched on Appolonia
OJ had Isotoners
act reckless.
whom much bullshit- to her
always be
never mess with his face
I do? Act more I late?
know what you right now
likey
don't know what he got the shit's ridiculous
for a world tour with
</pre>


#### Output from rw2

```python
lines = []
prev = None

for i in range(20):
#     print prev
    lines.append(rw2.make_words(8, init_token=prev))
    prev = lines[i].split(" ")[-1]

for line in lines:
    print line
```

<pre>
parked that tuxedo might have to his face
I want y'all to see this time for
her, but all of no's? he is what
we become a distance everything you I'm just
got the law, aspire for me now and
some math minors Woods don't really wasn't keep
bitches mean the crowd, spark you but when
it's you left your friends back home again
oyeee oh, loyee oyeee oh, loyee oyeee oh,
that's if you wave em straighten up now
how the way this is oh tried to
be the lights lights, spot lights cars, shooting
stars of no's? he got D's mother fucker,
D's, Rosie Perez yes, barely pass any and
I up't it a necklace. told Jay brown
of gold. What's you right now I grew
up their britches their britches their little whisky)
go- through too much I raised the lights
order visitation met this time and we dreamed
of me only live I dismiss her off,
</pre>
