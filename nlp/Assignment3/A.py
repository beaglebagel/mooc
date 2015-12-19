from main import replace_accented
from sklearn import svm
from sklearn import neighbors
from collections import defaultdict, Counter
import nltk
import numpy as np

from sklearn.feature_extraction import DictVectorizer
from sklearn.preprocessing import LabelEncoder

# don't change the window size
window_size = 10

# A.1
def build_s(data):
    '''
    Compute the context vector for each lexelt(word.postag)
    :param data: dic with the following structure:
        lexelt(word.postag): [(instance_id, left_context, head, right_context, sense_id), ...]
    :return: dic s with the following structure:
        lexelt(word.postag): [w1,w2,w3, ...],
    '''
    s = {}

    # implement your code here
    # for each of lexelt(word.postag)'s attribute context,
    #   collect all unique left,right occurring words within window_size.
    for lexelt, attributes in data.iteritems():
        word_set = set()
        for attribute in attributes:
            word_set.update(nltk.word_tokenize(attribute[1][-10:]))
            word_set.update(nltk.word_tokenize(attribute[3][:10]))
        s[lexelt] = list(word_set)
    return s


# A.1
def vectorize(data, s):
    '''
    :param data: list of attribute for a given lexelt(word.postag) with the following structure:
            [(instance_id, left_context, head, right_context, sense_id), ...]
    :param s: list of words (features) for a given lexelt(word.postag): [w1,w2,w3, ...]
    :return: vectors: A dictionary with the following structure
            { instance_id: [w_1 count, w_2 count, ...], ... }
            labels: A dictionary with the following structure
            { instance_id: sense_id }
    '''
    vectors, labels = {}, {}
    # for each attribute tuples, see how many words in s occur within left + right context / vectorize counts.
    for attributes in data:
        word_counter = Counter()
        word_counter.update(nltk.word_tokenize(attributes[1])[-10:])
        word_counter.update(nltk.word_tokenize(attributes[3])[:10])

        # create bit vector with each word count of s within surrounding context.
        vector = [word_counter[word] for word in s]
        vectors[attributes[0]] = vector
        labels[attributes[0]] = attributes[4]
        word_counter.clear()
    # print vectors, labels
    return vectors, labels


# A.2
def classify(X_train, X_test, y_train):
    '''
    Train two classifiers on (X_train, and y_train) then predict X_test labels

    :param X_train: A dictionary with the following structure
            { instance_id: [w_1 count, w_2 count, ...],
            ...
            }

    :param X_test: A dictionary with the following structure
            { instance_id: [w_1 count, w_2 count, ...],
            ...
            }

    :param y_train: A dictionary with the following structure
            { instance_id : sense_id }

    :return: svm_results: a list of tuples (instance_id, label) where labels are predicted by LinearSVC
             knn_results: a list of tuples (instance_id, label) where labels are predicted by KNeighborsClassifier
    '''

    # implement your code here
    dv, le = DictVectorizer(sparse=False), LabelEncoder()

    # SVM Section
    svm_clf = svm.LinearSVC()
    # x_train_np = np.array(X_train.values())
    y_train_encoded = le.fit_transform(y_train.values())

    svm_clf.fit(X_train.values(), y_train.values())
    svm_predicted = svm_clf.predict(X_test.values())
    svm_results = [ (instance_id, label) for instance_id, label in zip(X_test.keys(), svm_predicted) ]

    # x_train_np = np.array(X_train.values())
    # y_train_encoded = le.fit_transform(y_train.values())
    # svm_clf.fit(x_train_np, y_train_encoded)
    # svm_predicted = svm_clf.predict(X_test.values())
    # svm_predicted_decoded = list(le.inverse_transform(svm_predicted))
    # svm_results = [ (instance_id, label) for instance_id, label in zip(X_test.keys(), svm_predicted_decoded) ]

    knn_clf = neighbors.KNeighborsClassifier()

    knn_clf.fit(X_train.values(), y_train.values())
    knn_predicted = knn_clf.predict(X_test.values())
    knn_results = [ (instance_id, label) for instance_id, label in zip(X_test.keys(), knn_predicted) ]

    # knn_clf.fit(X_train.values(), y_train_encoded)
    # knn_predicted = knn_clf.predict(X_test.values())
    # knn_predicted_decoded = list(le.inverse_transform(knn_predicted))
    # knn_results = [ (instance_id, label) for instance_id, label in zip(X_test.keys(), knn_predicted_decoded) ]

    return svm_results, knn_results

# A.3, A.4 output
def print_results(results ,output_file):
    '''
    Output the predicted result.
    :param results: A dictionary with key = lexelt and value = a list of tuples (instance_id, label)
    :param output_file: file to write output
    '''

    # implement your code here
    # don't forget to remove the accent of characters using main.replace_accented(input_str)
    # you should sort results on instance_id before printing
    outfile = open(output_file, 'wb')
    for lexelt in sorted(results.keys()):
        tuple_list = results[lexelt]
        for tup in sorted(tuple_list):
            # print tup
            outfile.write('{0} {1} {2} \n'.format(
                replace_accented(lexelt),
                replace_accented(tup[0]),
                replace_accented(unicode(tup[1])),
                )
            )
    outfile.close()


# run part A
def run(train, test, language, knn_file, svm_file):
    s = build_s(train)
    svm_results = {}
    knn_results = {}
    for lexelt in s:
        X_train, y_train = vectorize(train[lexelt], s[lexelt])
        X_test, _ = vectorize(test[lexelt], s[lexelt])
        svm_results[lexelt], knn_results[lexelt] = classify(X_train, X_test, y_train)

    print_results(svm_results, svm_file)
    print_results(knn_results, knn_file)