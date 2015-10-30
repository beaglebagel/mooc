import sys

from featureextractor import FeatureExtractor
from providedcode.dependencygraph import DependencyGraph
from providedcode.transitionparser import TransitionParser
from transition import Transition

if __name__ == '__main__':
    # print 'NLP Parse Program..'

    try:
        model_path = sys.argv[1]
        # print 'ModelPath', model_path
    except IndexError as ie:
        print 'Model Path Not Specified! Exiting...', ie
        sys.exit(-1)

    try:
        tp = TransitionParser(Transition, FeatureExtractor)
        tp = TransitionParser.load(model_path)   # load the trained model for parsing.

        for line in sys.stdin:
            # print 'Processing:', line
            sentence = DependencyGraph.from_sentence(line)
            parsed = tp.parse([sentence]) # parse the input line
            print parsed[0].to_conll(10).encode('utf-8')

        # with open('test.conll', 'w') as f:
        #     for p in parsed:
        #         f.write(p.to_conll(10).encode('utf-8'))
        #         f.write('\n')

        # parsing arbitrary sentences (english):
        # sentence = DependencyGraph.from_sentence('Hi, this is a test')

        # tp = TransitionParser.load('english.model')
        # parsed = tp.parse([sentence])
        # print parsed[0].to_conll(10).encode('utf-8')

    except Exception as e:
        print 'Exiting with exception..', e
        sys.exit(-1)
