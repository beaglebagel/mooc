import math
import nltk
import time
from collections import Counter

# Constants to be used by you when you fill the functions
START_SYMBOL = '*'
STOP_SYMBOL = 'STOP'
MINUS_INFINITY_SENTENCE_LOG_PROB = -1000

# TODO: IMPLEMENT THIS FUNCTION
# Calculates unigram, bigram, and trigram probabilities given a training corpus
# training_corpus: is a list of the sentences. Each sentence is a string with tokens separated by spaces, ending in a newline character.
# This function outputs three python dictionaries, where the keys are tuples expressing the ngram and the value is the log probability of that ngram
def calc_probabilities(training_corpus):
    '''
    :param training_corpus: list of sentences to process
    :return: log probability dictionary for uni/bi/tri grams.
    '''
    unigram_p, bigram_p, trigram_p = {}, {}, {}
    unigram_c, bigram_c, trigram_c = Counter(), Counter(), Counter()

    # for each sentence,
    for sentence in training_corpus:

        # Adjust tokens, Unigrams
        tokens, tokens_uni = sentence.strip().split(), sentence.strip().split()
        tokens.insert(0, START_SYMBOL)
        tokens.insert(0, START_SYMBOL)
        tokens.append(STOP_SYMBOL)

        # tokens_uni.insert(0, START_SYMBOL)
        # tokens_uni.append('.')

        unigram_c.update(tokens[1:])    # unigram
        # unigram_c.update(tokens_uni)    # unigram
        bigram_c.update(nltk.bigrams(tokens))   # bigram
        trigram_c.update(nltk.trigrams(tokens))    # trigram

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

    return unigram_p, bigram_p, trigram_p

# Prints the output for q1
# Each input is a python dictionary where keys are a tuple expressing the ngram, and the value is the log probability of that ngram
def q1_output(unigrams, bigrams, trigrams, filename):
    # output probabilities
    outfile = open(filename, 'w')

    unigrams_keys = unigrams.keys()
    unigrams_keys.sort()
    for unigram in unigrams_keys:
        outfile.write('UNIGRAM ' + unigram[0] + ' ' + str(unigrams[unigram]) + '\n')

    bigrams_keys = bigrams.keys()
    bigrams_keys.sort()
    for bigram in bigrams_keys:
        outfile.write('BIGRAM ' + bigram[0] + ' ' + bigram[1]  + ' ' + str(bigrams[bigram]) + '\n')

    trigrams_keys = trigrams.keys()
    trigrams_keys.sort()    
    for trigram in trigrams_keys:
        outfile.write('TRIGRAM ' + trigram[0] + ' ' + trigram[1] + ' ' + trigram[2] + ' ' + str(trigrams[trigram]) + '\n')

    outfile.close()


# TODO: IMPLEMENT THIS FUNCTION
# Calculates scores (log probabilities) for every sentence
# ngram_p: python dictionary of probabilities of uni-, bi- and trigrams.
# n: size of the ngram you want to use to compute probabilities
# corpus: list of sentences to score. Each sentence is a string with tokens separated by spaces, ending in a newline character.
# This function must return a python list of scores, where the first element is the score of the first sentence, etc. 
def score(ngram_p, n, corpus):
    scores = []
    for sentence in corpus:
        tokens = sentence.strip().split()

        # this is to take care of bigram/trigram cases where sentence 'A', ... should be as ('*', 'A') or ('*', '*', 'A')
        if n >= 2:
            tokens.insert(0, START_SYMBOL)
            tokens.insert(0, START_SYMBOL)
        tokens.append(STOP_SYMBOL)

        probs = 0
        for i in range(len(tokens)-n+1):
            # probs.append(ngram_p[tuple(tokens[i:i+n])])
            ngram = tuple(tokens[i:i+n])

            if ngram not in ngram_p:
                probs = MINUS_INFINITY_SENTENCE_LOG_PROB
                break

            probs += ngram_p[ngram]

        scores.append(probs)
        # scores.append(reduce(lambda x, y: x*y, probs))
    return scores

# Outputs a score to a file
# scores: list of scores
# filename: is the output file name
def score_output(scores, filename):
    outfile = open(filename, 'w')
    for score in scores:
        outfile.write(str(score) + '\n')
    outfile.close()

# TODO: IMPLEMENT THIS FUNCTION
# Calculates scores (log probabilities) for every sentence with a linearly interpolated model
# Each ngram argument is a python dictionary where the keys are tuples that express an ngram and the value is the log probability of that ngram
# Like score(), this function returns a python list of scores
def linearscore(unigrams, bigrams, trigrams, corpus):
    '''
    Interpolation combines different order N-grams by linearly interpolating all the models.
    e.g. For trigram probability P(Wn | Wn_2 Wn_1) by mixing unigram, bigram, trigram probabilities each weighted by lambda.
        -> P = lambda1 * P(Wn) + lambda2 * P(Wn | Wn-1) + lambda3 * W(Wn | Wn_2, Wn-1)
        All lambdas are Equal and sum(all lambdas) = 1.
    '''
    scores, _lambda = [], 1 / 3.

    for sentence in corpus:
        tokens = sentence.strip().split()
        # this is to take care of bigram/trigram cases where sentence 'A', ... should be as ('*', 'A') or ('*', '*', 'A')
        tokens.insert(0, START_SYMBOL)
        tokens.insert(0, START_SYMBOL)
        tokens.append(STOP_SYMBOL)

        probs = 0

        # iterate through each trigrams that we will infer unigram, bigrams for, calculate the probabilities
        for i in range(3, len(tokens)+1):

            unigram = tuple(tokens[i-1:i])
            bigram = tuple(tokens[i-2:i])
            trigram = tuple(tokens[i-3:i])

            if unigram not in unigrams or bigram not in bigrams or trigram not in trigrams:
                probs = MINUS_INFINITY_SENTENCE_LOG_PROB
                break

            probs += math.log(_lambda * ( (2 ** unigrams[unigram]) + (2 ** bigrams[bigram]) + (2 ** trigrams[trigram]) ), 2)

        scores.append(probs)

    return scores

DATA_PATH = 'data/'
OUTPUT_PATH = 'output/'

# DO NOT MODIFY THE MAIN FUNCTION
def main():
    # start timer
    time.clock()

    # get data
    infile = open(DATA_PATH + 'Brown_train.txt', 'r')
    corpus = infile.readlines()
    infile.close()

    # calculate ngram probabilities (question 1)
    unigrams, bigrams, trigrams = calc_probabilities(corpus)

    # question 1 output
    q1_output(unigrams, bigrams, trigrams, OUTPUT_PATH + 'A1.txt')

    # score sentences (question 2)
    uniscores = score(unigrams, 1, corpus)
    biscores = score(bigrams, 2, corpus)
    triscores = score(trigrams, 3, corpus)

    # question 2 output
    score_output(uniscores, OUTPUT_PATH + 'A2.uni.txt')
    score_output(biscores, OUTPUT_PATH + 'A2.bi.txt')
    score_output(triscores, OUTPUT_PATH + 'A2.tri.txt')

    # linear interpolation (question 3)
    linearscores = linearscore(unigrams, bigrams, trigrams, corpus)

    # question 3 output
    score_output(linearscores, OUTPUT_PATH + 'A3.txt')

    # open Sample1 and Sample2 (question 5)
    infile = open(DATA_PATH + 'Sample1.txt', 'r')
    sample1 = infile.readlines()
    infile.close()
    infile = open(DATA_PATH + 'Sample2.txt', 'r')
    sample2 = infile.readlines()
    infile.close()

    # score the samples
    sample1scores = linearscore(unigrams, bigrams, trigrams, sample1)
    sample2scores = linearscore(unigrams, bigrams, trigrams, sample2)

    # question 5 output
    score_output(sample1scores, OUTPUT_PATH + 'Sample1_scored.txt')
    score_output(sample2scores, OUTPUT_PATH + 'Sample2_scored.txt')

    # print total time to run Part A
    print "Part A time: " + str(time.clock()) + ' sec'

if __name__ == "__main__":
    main()
