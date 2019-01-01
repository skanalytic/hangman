import re
import operator
import json
import math
from collections import Counter

# Load english word dictonary
def open_and_clean_english_dict(text_file = 'words.txt'):
    with open(text_file) as f:
        english_dict = f.read().splitlines()
    english_dict = list(set([x.lower() for x in english_dict]))
    english_dict = [re.sub(r'[^\w\s]','',x) for x in english_dict]
    return english_dict

def reset_game_metrics():
    guesses_list = []
    num_guesses = 0
    num_misses = 0
    correct_guess_dict = {}
    game_over = False
    return guesses_list, num_guesses, num_misses, correct_guess_dict, game_over

def pre_process_input(inputword):
    outputword = str(inputword).lower()
    return outputword

## more sophisticated might weight distribution by actual use/commonly known words
def get_words_with_len(word_length):
    start_words = [word for word in english_dict if len(word) == word_length]
    return start_words

def get_letter_dist_from_word_list(list_of_words):
    all_letters = [list(w) for w in list_of_words]
    all_letters_flat = [item for sublist in all_letters for item in sublist]
    letter_count = Counter(all_letters_flat)
    return letter_count

def get_word_so_far(correct_guess_dict):
    word_so_far = []
    for i in range(0,input_word_length):
        if i in correct_guess_dict.keys():
            word_so_far.append(correct_guess_dict[i])
        else:
            word_so_far.append("_")
    word_so_far = str(word_so_far)
    return word_so_far


## SEARCH BY DISTRIBUTION TO FIND FIRST LETTER
def guess_using_dist(dist):
    global guesses_list
    global num_misses
    global num_guesses
    global correct_guess_dict
    global dists_used

    dist = [x for x in ordered_letter_dist if x[0] not in guesses_list]  # remove guesses already made
    letter_freq_tuple = dist[0]  # get the largest letter frequency
    letter = letter_freq_tuple[0]  # get letter only
    # print("LETTER GUESSED: ", letter)
    guesses_list.append(letter)
    num_guesses += 1
    match_found = False
    for index, position in enumerate(inputword):
        if letter == position:
            correct_guess_dict[index] = letter
            match_found = True
            # print("MATCH FOUND")
            # print("NUMBER OF MISSES", num_misses)
            # print("WORD SO FAR", get_word_so_far(correct_guess_dict))
            # print(" ")
    if match_found == False:
        # print("NO MATCH FOUND")
        num_misses += 1
        # print("NUMBER OF MISSES:", num_misses)
        # print("WORD SO FAR", get_word_so_far(correct_guess_dict))
        # print(" ")
    return correct_guess_dict, guesses_list, num_guesses, num_misses


## RECALC DISTRIBUTION WITH NEW WORD INFO
def get_remaining_words(word_list_in, correct_guess_dict, guesses_list):
    remain_words = word_list_in

    # remove words with letters guessed which are wrong and therefore not in it
    wrong_letters = [letter for letter in guesses_list if letter not in list(correct_guess_dict.values())]
    remain_words_out1 = remain_words
    for guess_letter in wrong_letters:
        remain_words_out1 = [word for word in remain_words if guess_letter not in word]

    # keep only words with correctly guessed letters in the same position
    remain_words_out2 = remain_words_out1
    for i in correct_guess_dict.keys():
        correct_letter = correct_guess_dict[i]
        remain_words_out2 = [word for word in remain_words_out1 if correct_letter == word[i]]

    # print("NUMBER OF WORDS REMAINING", len(remain_words_out2))
    # if len(remain_words_out2) < 11:
    # print(remain_words_out2)
    return remain_words_out2

###### SERVER RUN

guesses_list, num_guesses, num_misses, correct_guess_dict, game_over = reset_game_metrics()
english_dict = open_and_clean_english_dict()

words_to_search = english_dict

number_of_batches = 100

batch_size = len(words_to_search) / number_of_batches
batch_size = math.ceil(batch_size)

results = {}
batch_number = 0
batch_amount = 0
run_size = 0

for search_word in words_to_search:
    inputword = search_word
    inputword = pre_process_input(inputword)
    input_word_length = len(inputword)
    start_words = get_words_with_len(input_word_length)

    while len(correct_guess_dict.keys()) < input_word_length:
        letter_dist = get_letter_dist_from_word_list(start_words)
        ordered_letter_dist = letter_dist.most_common()

        correct_guess_dict, guesses_list, num_guesses, num_misses = guess_using_dist(ordered_letter_dist)
        start_words = get_remaining_words(start_words, correct_guess_dict, guesses_list)
    else:
        final_word = str([correct_guess_dict[x] for x in range(0, len(correct_guess_dict.keys()))])

        results[search_word] = num_misses

        guesses_list, num_guesses, num_misses, correct_guess_dict, game_over = reset_game_metrics()

        batch_amount += 1
        run_size += 1
        if batch_amount == batch_size:
            results_file = str('results{}'.format(str(batch_number))) + '.json'
            print("batch number", str(batch_number))
            with open(results_file, 'a') as fp:
                json.dump(results, fp)
            print("records complete... ", str(run_size))
            batch_amount = 0
            batch_number += 1
            results = {}

# to flush the final batch
results_file = str('results{}'.format(str(batch_number))) + '.json'
print("batch number", str(batch_number))
with open(results_file, 'a') as fp:
    json.dump(results, fp)
print("records complete... ", str(run_size))