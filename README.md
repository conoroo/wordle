Conor O'Rourke
January 26, 2022

For fun, I wrote a program to simulate the recently popular game Wordle along with a few iterations of bots to solve the game. Each one gets progressively more advanced but none are particularly complicated.

There are four programs that get increasingly better:

1. Random guessing (0.2% win rate)
2. Filter the word list by the known rules (97.8% win rate)
3. Account for letter frequency (99.5% win rate)
4. Account for letter positional frquency (99.6% win rate)

 

This is the output of the testing across 1000 games in each bot:

~~~~
BotBase: Randomly chooses words
Iterations: 1000
Win Rate: 0.20%
Avg Guesses: 5.0
Win guess counts (7=loss): {7: 998, 5: 2}

Filters down based on rules, then randomly chooses
Iterations: 1000
Win Rate: 97.80%
Avg Guesses: 4.03
Win guess counts (7=loss): {5: 243, 3: 233, 4: 420, 7: 22, 2: 34, 6: 48}

Prioritize words with high letter frequencies.
Iterations: 1000
Win Rate: 99.50%
Avg Guesses: 3.67
Win guess counts (7=loss): {6: 26, 4: 403, 3: 391, 5: 121, 7: 5, 2: 52, 1: 2}

Account for letter positional frequency
Iterations: 1000
Win Rate: 99.60%
Avg Guesses: 3.59
Win guess counts (7=loss): {6: 21, 3: 414, 4: 394, 5: 102, 2: 64, 7: 4, 1: 1}
~~~~


The next iteration would probably bet to look into two things:

1. Strategies involving repeat letters
2. Test if it is advantageous to use early guesses to get more information regarding unknown letters rather than only getting information using unknown (grey) slots. What I mean by this is if you know 4 of 5 letters, but there are 6 words that share the same 4 letters, it may be advantageous to guess a word with most of those 6 letters so you know which one to pair with the 4 known ones.
