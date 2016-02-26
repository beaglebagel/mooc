from mrjob.job import MRJob, MRStep
from mrjob.protocol import JSONProtocol

import re
import sys

WORD_RE = re.compile(r"[\w']+")

class WordCounter(MRJob):

    OUTPUT_PROTOCOL = JSONProtocol

    def task_init(self):
        print 'mode', self.options.mode
        self.mode = self.options.mode

    def configure_options(self):
        super(WordCounter, self).configure_options()
        self.add_passthrough_option(
            '--mode', type='str', default='from', help='my argument description')

    def load_options(self, args):
        super(WordCounter, self).load_options(args)
        print 'Loading args: %s' % self.options
        self.mode = self.options.mode

    def mapper(self, _, line):
        for word in WORD_RE.findall(line):
            yield word.lower(), 1

    def mapper_reverse(self, word, count):
        yield '%010d'%int(count), word

    def combiner(self, word, counts):
        yield word, sum(counts)

    def reducer(self, word, counts):
        yield word, sum(counts)

    def reducer_reverse(self, count, words):
        for word in words:
            yield word, count

    def steps(self):
        return [
            MRStep(mapper=self.mapper, combiner=self.combiner, reducer=self.reducer),
            MRStep(mapper=self.mapper_reverse, reducer=self.reducer_reverse)
        ]


if __name__ == '__main__':
    print 'args:', sys.argv
    WordCounter.run()
