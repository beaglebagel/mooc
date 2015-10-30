import random
from providedcode import dataset
from providedcode.transitionparser import TransitionParser
from providedcode.evaluate import DependencyEvaluator
from featureextractor import FeatureExtractor
from transition import Transition

if __name__ == '__main__':
    # 'data' is parsed sentences converted into Dependency Graph objects.
    model_dict = {
            'english' : ('english.model', dataset.get_english_train_corpus, dataset.get_english_test_corpus),
            'danish' : ('danish.model', dataset.get_danish_train_corpus, dataset.get_danish_test_corpus),
            'swedish' : ('swedish.model', dataset.get_swedish_train_corpus, dataset.get_swedish_test_corpus)
    }
    for model_type, model_tuple in model_dict.iteritems():
        model, data, testdata = model_tuple[0], model_tuple[1]().parsed_sents(), model_tuple[2]().parsed_sents()

        random.seed(1234)
        subdata = random.sample(data, 200)  # 200 randomly selected DependencyGraphs(sentences) for model training.

        try:
            tp = TransitionParser(Transition, FeatureExtractor)
            tp.train(subdata)   # train with 200 randomly selected dependency graphs(sentences).
            tp.save(model)  # save the trained model.

            tp = TransitionParser.load(model)   # load the trained model for parsing.

            parsed = tp.parse(testdata) # parse the test data

            with open('test.conll', 'w') as f:
                for p in parsed:
                    f.write(p.to_conll(10).encode('utf-8'))
                    f.write('\n')

            # evaluate the test parse result here...
            ev = DependencyEvaluator(testdata, parsed)
            print 'Model: {}'.format(model_type)
            # LAS: labeled attachment score - percentage of scoring tokens for which the parsing system has predicted the
            #    correct head and dependency label.
            # UAS:
            print "LAS: {} \nUAS: {}".format(*ev.eval())

            # parsing arbitrary sentences (english):
            # sentence = DependencyGraph.from_sentence('Hi, this is a test')

            # tp = TransitionParser.load('english.model')
            # parsed = tp.parse([sentence])
            # print parsed[0].to_conll(10).encode('utf-8')

        except NotImplementedError:
            print """
            This file is currently broken! We removed the implementation of Transition
            (in transition.py), which tells the transitionparser how to go from one
            Configuration to another Configuration. This is an essential part of the
            arc-eager dependency parsing algorithm, so you should probably fix that :)

            The algorithm is described in great detail here:
                http://aclweb.org/anthology//C/C12/C12-1059.pdf

            We also haven't actually implemented most of the features for for the
            support vector machine (in featureextractor.py), so as you might expect the
            evaluator is going to give you somewhat bad results...

            Your output should look something like this:

                LAS: 0.23023302131
                UAS: 0.125273849831

            Not this:

                Traceback (most recent call last):
                    File "test.py", line 41, in <module>
                        ...
                        NotImplementedError: Please implement shift!


            """
