import nltk
import math
import numpy
import time

from collections import defaultdict
from collections import Counter
from itertools import izip

START_SYMBOL = '*'
STOP_SYMBOL = 'STOP'
RARE_SYMBOL = '_RARE_'
RARE_WORD_MAX_FREQ = 5
LOG_PROB_OF_ZERO = -1000


# TODO: IMPLEMENT THIS FUNCTION
# Receives a list of tagged sentences and processes each sentence to generate a list of words and a list of tags.
# Each sentence is a string of space separated "WORD/TAG" tokens, with a newline character in the end.
# Remember to include start and stop symbols in your returned lists, as defined by the constants START_SYMBOL and STOP_SYMBOL.
# brown_words (the list of words) should be a list where every element is a list of the words of a particular sentence.
# brown_tags (the list of tags) should be a list where every element is a list of the tags of a particular sentence.
def split_wordtags(brown_train):

    brown_words = []
    brown_tags = []

    for sentence in brown_train:
        words, tags = [], []

        # mark sentence start.
        words.append(START_SYMBOL)
        words.append(START_SYMBOL)
        tags.append(START_SYMBOL)
        tags.append(START_SYMBOL)

        pairs = sentence.strip().split()

        # split on rightmost '/'
        for pair in pairs:
            word, tag = pair.rsplit('/', 1)
            words.append(word)
            tags.append(tag)

        # mark sentence end.
        words.append(STOP_SYMBOL)
        tags.append(STOP_SYMBOL)

        brown_words.append(words)
        brown_tags.append(tags)

    return brown_words, brown_tags

# TODO: IMPLEMENT THIS FUNCTION
# This function takes tags from the training data and calculates tag trigram probabilities.
# It returns a python dictionary where the keys are tuples that represent the tag trigram,
#  and the values are the log probability of that trigram
def calc_trigrams(brown_tags):
    '''
    Calculate the log-probabilities of tag trigrams.
    :param brown_tags: List of 'sentence tags List' [ [], [] .. ]
    :return: tag trigram probability dictionary
    '''
    unigram_p, bigram_p, trigram_p = {}, {}, {}
    unigram_c, bigram_c, trigram_c = Counter(), Counter(), Counter()

    # flatten brown tags since it's list of tag lists.
    brown_tags_flat = [item for sublist in brown_tags for item in sublist]

    unigram_c.update(brown_tags_flat)    # unigram
    bigram_c.update(nltk.bigrams(brown_tags_flat))   # bigram
    trigram_c.update(nltk.trigrams(brown_tags_flat))    # trigram

    unigram_len, bigram_len, trigram_len = sum(unigram_c.values()), sum(bigram_c.values()), sum(trigram_c.values())
    # prepare unigram log probabilities -> P(Wi) = c(Wi) / V
    for unigram, count in unigram_c.iteritems():
        unigram_p[(unigram,)] = math.log(count / float(unigram_len-32491), 2)

    # prepare bigram log probabilities -> P(Wi|Wi-1) = c(Wi-1,Wi)/c(Wi-1)
    for bigram, count in bigram_c.iteritems():
        bigram_p[bigram] = math.log(count / float(unigram_c[bigram[0]]), 2)

    # prepare trigram log probabilities -> P(Wi|Wi-2, Wi-1) = c(Wi-2,Wi-1,Wi)/c(Wi-2,Wi-1)
    for trigram, count in trigram_c.iteritems():
        trigram_p[trigram] = math.log(count / float(bigram_c[trigram[:2]]), 2)

    return trigram_p

# This function takes output from calc_trigrams() and outputs it in the proper format
def q2_output(q_values, filename):
    outfile = open(filename, "w")
    trigrams = q_values.keys()
    trigrams.sort()  
    for trigram in trigrams:
        output = " ".join(['TRIGRAM', trigram[0], trigram[1], trigram[2], str(q_values[trigram])])
        outfile.write(output + '\n')
    outfile.close()


# TODO: IMPLEMENT THIS FUNCTION
# Takes the words from the training data and returns a set of all of the words that occur more than 5 times (use RARE_WORD_MAX_FREQ)
# brown_words is a python list where every element is a python list of the words of a particular sentence.
# Note: words that appear exactly 5 times should be considered rare!
def calc_known(brown_words):
    '''
7    :param brown_words: List of 'sentence words List' [ [], [] .. ]
    :return:
    '''
    known_words = set([])
    brown_words_flat = [item for sublist in brown_words for item in sublist]
    word_counter = Counter(brown_words_flat)

    [known_words.add(word) for word, value in word_counter.iteritems() if value > 5]
    return known_words

# TODO: IMPLEMENT THIS FUNCTION
# Takes the words from the training data and a set of words that should not be replaced for '_RARE_'
# Returns the equivalent to brown_words but replacing the unknown words by '_RARE_' (use RARE_SYMBOL constant)
def replace_rare(brown_words, known_words):
    brown_words_rare = []

    for words in brown_words:
        filtered_words = []
        for word in words:
            if word in known_words:
                filtered_words.append(word)
            else:
                filtered_words.append(RARE_SYMBOL)
        brown_words_rare.append(filtered_words)
    return brown_words_rare

# This function takes the ouput from replace_rare and outputs it to a file
def q3_output(rare, filename):
    outfile = open(filename, 'w')
    for sentence in rare:
        outfile.write(' '.join(sentence[2:-1]) + '\n')
    outfile.close()


# TODO: IMPLEMENT THIS FUNCTION
# Calculates emission probabilities and creates a set of all possible tags
# The first return value is a python dictionary
#   where each key is a tuple in which the first element is a word and the second is a tag,
#   and the value is the log probability of the emission of the word given the tag
# The second return value is a set of all possible tags for this data set
def calc_emission(brown_words_rare, brown_tags):
    '''
    :param brown_words_rare: list of word lists with rare words(occurrence < 6) is replaced with _RARE_
    :param brown_tags: list of tag lists.
    :return: e_values -> dict(tuple(word, tag) -> log prob of (word | tag))
            taglist -> set of all possible tags for this dataset.
    '''
    brown_words_flat = [item for sublist in brown_words_rare for item in sublist]
    brown_tags_flat = [item for sublist in brown_tags for item in sublist]
    pair_counter, tag_counter = Counter(izip(brown_words_flat,brown_tags_flat)), Counter(brown_tags_flat)

    e_values = {}
    for pair in set(izip(brown_words_flat, brown_tags_flat)):
        # print pair
        e_values[pair] = math.log(pair_counter[pair] / float(tag_counter[pair[1]]), 2)
    taglist = set(brown_tags_flat)
    return e_values, taglist

# This function takes the output from calc_emissions() and outputs it
def q4_output(e_values, filename):
    outfile = open(filename, "w")
    emissions = e_values.keys()
    emissions.sort()  
    for item in emissions:
        output = " ".join([item[0], item[1], str(e_values[item])])
        outfile.write(output + '\n')
    outfile.close()


# TODO: IMPLEMENT THIS FUNCTION
# This function takes data to tag (brown_dev_words),
# and outputs a list where every element is a tagged sentence
# (in the WORD/TAG format, separated by spaces and with a newline in the end, just like our input tagged data)
# The return value is a list of tagged sentences in the format "WORD/TAG",
# separated by spaces. Each sentence is a string with a terminal newline, not a list of tokens.
# Remember also that the output should not contain the "_RARE_" symbol, but rather the original words of the sentence!
def viterbi(brown_dev_words, taglist, known_words, trigram_p, emission_p):
    '''
    Calculates the most likely tag sequences of given sentence lists using Viterbi Algorithm.
    For each sentence, keep track of maximum probabilities of each trigrams using Dynamic Programming.
    :param brown_dev_words: list of sentence 'word list'.
    :param taglist: a set of all possible tags.
    :param known_words: set of all known_words (words occurring > 5).
    :param trigram_p: trigram probabilities. dict(trigram tuple) -> transition probs - calculated based on previous bigrams.
    :param emission_p: emission probabilities. dict(tuple(word, tag) -> log prob of (word | tag))
    :return: list of tagged sentences 'WORD/TAG's separated by spaces terminated by newlines each.
    '''

    tagged = []     # will contain word/tags for each sentence.
    taglist.remove(START_SYMBOL)

    for sentence_words in brown_dev_words:

        # will store the ongoing probabilities.
        # PM[i][j] stores max path probabilities up to word j for each tag i.
        # TM[i][j] stores max possible trigram up to word j for each tag i.
        PM, TM, word_tags = numpy.zeros([len(taglist)+2, len(sentence_words)]), defaultdict(dict), []
        PM.fill(float('-inf'))
        word0 = sentence_words[0]   # initial observation.

        # populate the initial probabilities -> prob(from start state to each tag) * prob(word0 | tag)
        for idx, tag_0 in enumerate(taglist, 1):
            # filling probabilities for first column. word0=w1.
            prob, trigram, word_tag = 0, (START_SYMBOL, START_SYMBOL, tag_0), (word0, tag_0)
            TM[idx][0] = trigram
            PM[idx, 0] = trigram_p.get(trigram, LOG_PROB_OF_ZERO) + emission_p.get((word0, tag_0), 0)

        # print PM
        # take care of first word0's tag. Using argmax axis=0 for max of each PM 'columns',
        # using only first column here as this is the first word.
        word_tags.append(word0 + '/' + TM[PM.argmax(axis=0)[0]][0][2])

        # for each sentence(starting from the second word..), calculate the most likely tag sequences.
        # tag0 -> tag(t), tag1 -> tag(t-1), tag2 -> tag(t-2)
        for time, word in enumerate(sentence_words[1:], 1):     # for each matrix column...
            for tag_0_idx, tag_0 in enumerate(taglist, 1):
                # get the max out of each probability cases.
                probs = {}
                for tag_1_idx, tag_1 in enumerate(taglist, 1):
                    # accumulate probabilities from each possible previous transitions.
                    prev_bigram = list(TM[tag_1_idx][time-1][1:])
                    # prev_bigram becomes current instance of trigram.
                    prev_bigram.append(tag_0)

                    prob = PM[tag_1_idx, time-1] \
                           + trigram_p.get(tuple(prev_bigram), LOG_PROB_OF_ZERO) \
                           + emission_p.get((word, tag_0),0)
                    probs[tuple(prev_bigram)] = prob

                # find the key,value with max probability and store.
                max_trigram = max(probs, key=lambda i: probs[i])
                PM[tag_0_idx, time] = probs[max_trigram]
                TM[tag_0_idx][time] = max_trigram

            if word not in known_words: # if the word is rare(<5) then replace with _RARE_ symbol.
                word = RARE_SYMBOL
            # take care of word tags, find the trigram with max probability up to current cell and assign it's last tag
            # to the word as that is the max path.
            word_tags.append(word + '/' + TM[PM.argmax(axis=0)[time]][time][2])

        # for each sentence, generate list of max(tag/word)s for each sentence.
        tagged.append(' '.join(word_tags) + '\n')
    return tagged

# This function takes the output of viterbi() and outputs it to file
def q5_output(tagged, filename):
    outfile = open(filename, 'w')
    for sentence in tagged:
        outfile.write(sentence)
    outfile.close()

# TODO: IMPLEMENT THIS FUNCTION
# This function uses nltk to create the taggers described in question 6
# brown_words and brown_tags is the data to be used in training
# brown_dev_words is the data that should be tagged
# The return value is a list of tagged sentences in the format "WORD/TAG", separated by spaces.
# Each sentence is a string with a terminal newline, not a list of tokens.
def nltk_tagger(brown_words, brown_tags, brown_dev_words):
    # Hint: use the following line to format data to what NLTK expects for training
    training = [ zip(brown_words[i],brown_tags[i]) for i in xrange(len(brown_words)) ]
    # IMPLEMENT THE REST OF THE FUNCTION HERE
    default_tagger = nltk.DefaultTagger('NOUN')
    bigram_tagger = nltk.BigramTagger(training, backoff=default_tagger)
    trigram_tagger = nltk.TrigramTagger(training, backoff=bigram_tagger)
    tagged = []

    for sentence_tokens in brown_dev_words:
        tagged_sentence = ' '.join([ word_tag[0]+'/'+word_tag[1] for word_tag in trigram_tagger.tag(sentence_tokens)]) + '\n'
        tagged.append(tagged_sentence)

    return tagged

# This function takes the output of nltk_tagger() and outputs it to file
def q6_output(tagged, filename):
    outfile = open(filename, 'w')
    for sentence in tagged:
        outfile.write(sentence)
    outfile.close()

DATA_PATH = 'data/'
OUTPUT_PATH = 'output/'

def main():
    # start timer
    time.clock()

    # open Brown training data
    infile = open(DATA_PATH + "Brown_tagged_train.txt", "r")
    brown_train = infile.readlines()
    infile.close()

    # split words and tags, and add start and stop symbols (question 1)
    brown_words, brown_tags = split_wordtags(brown_train)

    # calculate tag trigram probabilities (question 2)
    q_values = calc_trigrams(brown_tags)

    # question 2 output
    q2_output(q_values, OUTPUT_PATH + 'B2.txt')

    # calculate list of words with count > 5 (question 3)
    known_words = calc_known(brown_words)
    # print known_words

    # get a version of brown_words with rare words replace with '_RARE_' (question 3)
    brown_words_rare = replace_rare(brown_words, known_words)

    # question 3 output
    q3_output(brown_words_rare, OUTPUT_PATH + "B3.txt")

    # calculate emission probabilities (question 4)
    e_values, taglist = calc_emission(brown_words_rare, brown_tags)

    # print taglist
    # question 4 output
    q4_output(e_values, OUTPUT_PATH + "B4.txt")

    # delete unneceessary data
    del brown_train
    del brown_words_rare

    # open Brown development data (question 5)
    infile = open(DATA_PATH + "Brown_dev.txt", "r")
    brown_dev = infile.readlines()
    infile.close()

    # format Brown development data here
    brown_dev_words = []
    for sentence in brown_dev:
        brown_dev_words.append(sentence.split(" ")[:-1])

    # print e_values
    # do viterbi on brown_dev_words (question 5)
    viterbi_tagged = viterbi(brown_dev_words, taglist, known_words, q_values, e_values)

    # question 5 output
    q5_output(viterbi_tagged, OUTPUT_PATH + 'B5.txt')

    # do nltk tagging here
    nltk_tagged = nltk_tagger(brown_words, brown_tags, brown_dev_words)

    # question 6 output
    q6_output(nltk_tagged, OUTPUT_PATH + 'B6.txt')

    # print total time to run Part B
    print "Part B time: " + str(time.clock()) + ' sec'

if __name__ == "__main__": main()
