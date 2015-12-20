import A
import nltk

from collections import Counter
from nltk.corpus import stopwords
from sklearn import neighbors, svm
from sklearn.feature_extraction import DictVectorizer



# You might change the window size
window_size = 42

# B.1.a,b,c,d
def extract_features(data):
    '''
    :param data: list of instances for a given lexelt with the following structure:
        {
			[(instance_id, left_context, head, right_context, sense_id), ...]
        }
    :return: features: A dictionary with the following structure
             { instance_id: {f1:count, f2:count,...}
            ...
            }
            labels: A dictionary with the following structure
            { instance_id : sense_id }
    '''
    # implement your code here
    features, labels, sws = {}, {}, set()
    # sws.update(stopwords.words('english'))
    sws.update(stopwords.words('spanish'))
    # sws.update(stopwords.words('catalan'))

    for instance in data:
        wcounter = Counter()
        # tokenize, filter out stopwords from context.
        # left_context = [word for word in nltk.word_tokenize(instance[1]) if word.lower() not in sws]
        # right_context = [word for word in nltk.word_tokenize(instance[3]) if word.lower() not in sws]
        # wcounter.update(left_context[-window_size:])
        # wcounter.update(right_context[:window_size])

        left_context = nltk.word_tokenize(instance[1])[-window_size:]
        right_context = nltk.word_tokenize(instance[3])[:window_size]
        wcounter.update([word for word in left_context if word.lower() not in sws])
        wcounter.update([word for word in right_context if word.lower() not in sws])

        features[instance[0]] = dict(wcounter)
        labels[instance[0]] = instance[4]

    return features, labels

# implemented for you
def vectorize(train_features,test_features):
    '''
    convert set of features to vector representation
    :param train_features: A dictionary with the following structure
             { instance_id: {f1:count, f2:count,...}
            ...
            }
    :param test_features: A dictionary with the following structure
             { instance_id: {f1:count, f2:count,...}
            ...
            }
    :return: X_train: A dictionary with the following structure
             { instance_id: [f1_count,f2_count, ...]}
            ...
            }
            X_test: A dictionary with the following structure
             { instance_id: [f1_count,f2_count, ...]}
            ...
            }
    '''
    X_train, X_test = {}, {}

    vec = DictVectorizer()
    vec.fit(train_features.values())
    for instance_id in train_features:
        X_train[instance_id] = vec.transform(train_features[instance_id]).toarray()[0]

    for instance_id in test_features:
        X_test[instance_id] = vec.transform(test_features[instance_id]).toarray()[0]

    return X_train, X_test

#B.1.e
def feature_selection(X_train,X_test,y_train):
    '''
    Try to select best features using good feature selection methods (chi-square or PMI)
    or simply you can return train, test if you want to select all features
    :param X_train: A dictionary with the following structure
             { instance_id: [f1_count,f2_count, ...]}
            ...
            }
    :param X_test: A dictionary with the following structure
             { instance_id: [f1_count,f2_count, ...]}
            ...
            }
    :param y_train: A dictionary with the following structure
            { instance_id : sense_id }
    :return:
    '''

    # implement your code here

    #return X_train_new, X_test_new
    # or return all feature (no feature selection):
    return X_train, X_test

# B.2
def classify(X_train, X_test, y_train):
    '''
    Train the best classifier on (X_train, and y_train) then predict X_test labels

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

    :return: results: a list of tuples (instance_id, label) where labels are predicted by the best classifier
    '''

    results = []
    # implement your code here
    svm_clf = svm.LinearSVC()
    # svm_clf.fit(X_train.values(), y_train.values())
    realigned_y_train = [y_train[k] for k in X_train]
    svm_clf.fit(X_train.values(), realigned_y_train)
    svm_predicted = svm_clf.predict(X_test.values())
    svm_results = [ (instance_id, label) for instance_id, label in zip(X_test.keys(), svm_predicted) ]

    knn_clf = neighbors.KNeighborsClassifier()
    # knn_clf.fit(X_train.values(), y_train.values())
    knn_clf.fit(X_train.values(), realigned_y_train)
    knn_predicted = knn_clf.predict(X_test.values())
    knn_results = [ (instance_id, label) for instance_id, label in zip(X_test.keys(), knn_predicted) ]

    return svm_results
    # return knn_results
    # return results

# run part B
def run(train, test, language, answer):
    results = {}

    for lexelt in train:

        train_features, y_train = extract_features(train[lexelt])
        test_features, _ = extract_features(test[lexelt])

        X_train, X_test = vectorize(train_features,test_features)
        X_train_new, X_test_new = feature_selection(X_train, X_test,y_train)
        results[lexelt] = classify(X_train_new, X_test_new,y_train)

    A.print_results(results, answer)