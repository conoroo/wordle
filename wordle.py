#!/usr/bin/env python
# coding: utf-8

# Author: Conor O'Rourke
# Date: January 26, 2022

import random
from string import ascii_lowercase

class Wordle(object):

    def __init__(self, random_seed=None, target_word=None):
        """
        Object that creates a Wordle game that creates a target word and evaluates your guesses.

        :param random_seed: Set the random seed in order to ensure the same state is used across tests.
        :param target_word: Option to set the target word.
        """
        self.guesses = 0
        self.max_guesses = 6
        self.random_seed=random_seed
        
        self.create_dictionary()
        self.set_target(target_word)


    def create_dictionary(self):
        """
        Sets the dictionary of 5 letter words taken from the Wordle site code.
        :return: None
        """
        with open('words.txt', 'r') as f:
            words_base = f.read()
            self.words_base = words_base.split("\n")
        
    def set_target(self, target_word):
        """
        Sets the target word for the game. Random if target is not provided.
        :param target_word: Set a specific target word.
        :return: None
        """
        if target_word is None:
            if self.random_seed is not None:
                random.seed(self.random_seed)
            self.target = random.choice(self.words_base)
        else:
            assert target_word in self.words_base, "Invalid target word. Not in dictionary."
            self.target = target_word
            
            
    def try_word(self, word):
        """
        Grades a sample word based on Wordle rules.
        :param word: The word you want to submit.
        :return: A list with one tuple for each letter along with it's match status.

            0 = No Match
            1 = Letter in Word
            2 = Letter in Correct Place

            Example for target word 'whack' testing the word 'crank':
                [('c', 1), ('r', 0), ('a', 2), ('n', 0), ('k', 2)]
        """
        assert len(word) == 5, "Word must be 5 letters"
        assert word in self.words_base, "Word not in dictionary"
        
        res = []
        for i in range(0,5):
            if word[i] == self.target[i]:
                res.append((word[i], 2))
            elif word[i] in self.target:
                res.append((word[i], 1))
            else:
                res.append((word[i], 0))
        
        win = all([l[1] == 2 for l in res])
        return res, win



class WordleBotBase(object):
    """Base Wordle bot class to handle gameplay, stat aggregation.

     The base version randomly guesses words with no memory or accounting for information from the game.
     """
    
    def __init__(self, random_seed=0):

        self.max_guesses = 6
        self.create_dictionary()
        self.random_seed=random_seed
        
        self.test_results = None
    
    def reset_state(self):
        """Resets object variables if necessary"""
        pass

    def create_dictionary(self):
        """
        Sets the dictionary of 5 letter words taken from the Wordle site code.
        :return: None
        """
        with open('words.txt', 'r') as f:
            words_base = f.read()
            self.words_base = words_base.split("\n")
        
    def next_guess(self, past_guesses):
        """Returns the bot's next best guess."""
        return random.choice(self.words_base)
            
    def play_game(self, game_instance):
        """
        Given a game instance, this function comes up with its best guess, runs it
        through the game, and continues until it wins or loses.

        :param game_instance: Wordle game object instance.
        :return: (bool win_status, int guess_count, list list_of_guesses_and_results)
        """
        guesses = 0
        past_guesses = []
        
        self.reset_state()
        
        while True:
            word = self.next_guess(past_guesses)
            res = game_instance.try_word(word)

            guesses += 1
            past_guesses.append(res[0])

            if res[1]:
                break
                
            if guesses == self.max_guesses:
                guesses += 1
                break

        return res[1], guesses, past_guesses
            
        
    def test_bot(self, run_ct=10):
        """
        Runs {run_ct} number of Wordle games sequentially to evaluate bot performance.
        :param run_ct: # runs
        :return: test_results = {run_count, win_rate, avg_guesses, guess_counts}
        """
        bot_results = []
        
        for r in range(0, run_ct):
            w = Wordle(random_seed=self.random_seed + len(bot_results))
            
            res = self.play_game(w)
            
            bot_results.append({
                'win': res[0],
                'guesses': res[1],
                'word': w.target
            })
        
        guess_cts = {}
        for r in bot_results:
            guess_cts[r['guesses']] = guess_cts.get(r['guesses'], 0) + 1
            
        win_rate = sum([1 for r in bot_results if r['win']]) / len(bot_results)
        avg_guesses = sum([k * v for k, v in guess_cts.items() if not k==7]) / sum([1 for r in bot_results if r['win']])
        
        self.test_results = {
            'run_count': run_ct,
            'win_rate': win_rate,
            'avg_guesses': avg_guesses,
            'guess_counts': guess_cts  
        }
        
        print (f"Iterations: {run_ct}")
        print ("Win Rate: " + "{:.2%}".format(win_rate))
        print (f"Avg Guesses: {str(avg_guesses)[:4]}")
        print ("Win guess counts (7=loss): " + str(guess_cts))




class FilterBot(WordleBotBase):
    """FilterBot simply makes a random guess, cuts down the list of possible remaining
    words, then makes another random guess."""

    def __init__(self, random_seed=0):
        super().__init__(random_seed=random_seed) # Set random seed so tests are consistent across bots

        self.reset_state()

    def reset_state(self):
        """Resets object variables if necessary"""
        self.working_dict = self.words_base.copy()
        
    def next_guess(self, past_guesses=[]):
        """Returns the bot's next best guess."""
        
        # Filter dictionary for known properties
        if len(past_guesses) > 0:
            self.working_dict = [
                w for w in self.working_dict if
                   not any([any([
                       (t[1] == 0) & (t[0] in w),      # Letter is not in target but is in word
                       (t[1] == 1) & (t[0] not in w),  # Letter is in target but not in word
                       (t[1] == 1) & (t[0] == w[i]),   # Letter is in target, but not this position
                       (t[1] == 2) & (t[0] != w[i])    # Letter is in word, and in this position
                   ]) for i, t in enumerate(past_guesses[-1])])
            ]        
                
        guess = random.choice(self.working_dict)
        return guess
            


class FreqFilterBot(WordleBotBase):
    """FreqFilterBot prioritizes guessing words that contain high frequency characters
    to improve its rate of information collection."""

    def __init__(self, random_seed=0):
        super().__init__(random_seed=random_seed) # Set random seed so tests are consistent across bots

        self.reset_state()
        
    def reset_state(self):
        """Resets object variables if necessary"""
        self.working_dict = self.words_base.copy()
        
    def next_guess(self, past_guesses=[]):
        """Returns the bot's next best guess."""
        
        # Filter dictionary for known properties
        if len(past_guesses) > 0:
            self.working_dict = [
                w for w in self.working_dict if
                   not any([any([
                       (t[1] == 0) & (t[0] in w),      # Letter is not in target but is in word
                       (t[1] == 1) & (t[0] not in w),  # Letter is in target but not in word
                       (t[1] == 1) & (t[0] == w[i]),   # Letter is in target, but not this position
                       (t[1] == 2) & (t[0] != w[i])    # Letter is in word, and in this position
                   ]) for i, t in enumerate(past_guesses[-1])])
            ]

        # Get character frequency from remaining word set
        j = "".join(self.working_dict)
        char_freq = {l: j.count(l) / len(self.working_dict) for l in ascii_lowercase}

        # Score words based on their character frequency. Note that repeat letters don't get double points.
        scores = [(w, sum([char_freq[c] for c in set(w)])) for w in self.working_dict]
        scores = sorted(scores, key=lambda x: x[1], reverse=True)

        # Guess the highest scoring word
        guess = scores[0][0]

        return guess


class FreqFilterBot2(WordleBotBase):
    """FreqFilterBot2 prioritizes words with high frequency characters and gives a slight
    advantage to characters based on their position in a word."""

    def __init__(self, random_seed=0, pos_wgt=2):
        super().__init__(random_seed=random_seed) # Set random seed so tests are consistent across bots
        
        self.pos_wgt=pos_wgt
        
        self.reset_state()
        
    def reset_state(self):
        """Resets object variables if necessary"""
        self.working_dict = self.words_base.copy()
        
    def next_guess(self, past_guesses=[]):
        """Returns the bot's next best guess."""
        
        # Filter dictionary for known properties
        if len(past_guesses) > 0:
            # Filter remaining words in the list based on findings
            self.working_dict = [
                w for w in self.working_dict if
                   not any([any([
                       (t[1] == 0) & (t[0] in w),      # Letter is not in target but is in word
                       (t[1] == 1) & (t[0] not in w),  # Letter is in target but not in word
                       (t[1] == 1) & (t[0] == w[i]),   # Letter is in target, but not this position
                       (t[1] == 2) & (t[0] != w[i])    # Letter is in word, and in this position
                   ]) for i, t in enumerate(past_guesses[-1])])
            ]

        # Derive letter and letter position frequencies
        j = "".join(self.working_dict)
        char_freq = {l: j.count(l) / len(self.working_dict) for l in ascii_lowercase}
        cpos_freq = {l: {i: sum([1 for w in self.working_dict if l == w[i]])
                         for i in range(0,5)} for l in ascii_lowercase}

        # Word score is a function of how prevalent its letters are in the remaining
        # word set and if its letters share the same position of many other words.
        scores = [(w,
                   sum([char_freq[l] / w.count(l) * (1 + (cpos_freq[l][i] / sum(cpos_freq[l].values()) / self.pos_wgt))
                        for i, l in enumerate(w)])) for w in self.working_dict]
        
        scores = sorted(scores, key=lambda x: x[1], reverse=True)

        guess = scores[0][0]

        return guess


# Run tests for each of the bots.
print ("Testing Wordle Bots")
start_seed = 12

print("\nBotBase: Randomly chooses words")
wb1 = WordleBotBase(random_seed=start_seed)
wb1.test_bot(1000)

print("\nFilters down based on rules, then randomly chooses")
wb2 = FilterBot(random_seed=start_seed)
wb2.test_bot(1000)

print("\nPrioritize words with high letter frequencies.")
wb3 = FreqFilterBot(random_seed=start_seed)
wb3.test_bot(1000)

print("\nAccount for letter positional frequency")
wb4 = FreqFilterBot2(random_seed=start_seed, pos_wgt=1)
wb4.test_bot(1000)



# How would the bot have played a known game?
print ("\n\nFreqFilterBot2 simulation for word 'whack'")
w = Wordle(target_word='whack')
wb = FreqFilterBot2(random_seed=start_seed, pos_wgt=1)
res = wb.play_game(w)
print (f"Win: {res[0]}  \nGuesses: {res[1]}  \nGameplay:")
for r in res[2]:
    print(r)



