from mrjob.job import MRJob, MRStep

class RankAirline(MRJob):
    """
    Group 1.2
    Rank the airline by on-time arrival performance.
    Capstone: Top 10 airlines based on on-time arrival performance.

    Each file line is composed of the following 19 fields in order as is:

        0-4: year, month, dayofmonth, dayofweek, flight_date,
        5-9: unique_carrier, flightNum, origin, dest, crs_dep_time,
        10-14: dep_delay_min, dep_del_15, crs_arr_time, arr_delay_min, arr_del_15,
        15-20: cancelled, diverted

    """

    # def configure_options(self):
    #     super(RankAirline, self).configure_options()
    #
    # def load_options(self, args):
    #     super(RankAirline, self).load_options(args)
    #     print 'Loading Options: %s' % self.options

    def mapper(self, _, line):

        fields = line.strip().split('|')
        # @NOTE: for arrival delay, try using arr_delay_min first..
        airline, delay = fields[5], fields[10]
        try:
            yield airline, (int(float(delay)), 1)
        except Exception as e:
            print airline, delay, e


    def combiner(self, airline, delays):

        yield airline, map(sum, zip(*delays))

    def reducer(self, airline, delays):
        # @TODO: how to sort the output from max to min - reverse order?

        total_delay, count = map(sum, zip(*delays))
        yield airline, total_delay / float(count)

    def mapper2(self, airline, delay):
        yield delay, airline

    def reducer2(self, delay, airlines):
        for airline in airlines:
            yield airline, float(delay)

    def steps(self):
        return [
            MRStep(mapper=self.mapper, combiner=self.combiner, reducer=self.reducer),
            MRStep(mapper=self.mapper2, reducer=self.reducer2),
            # MRStep(reducer_cmd='tac')
        ]

if __name__ == '__main__':
    RankAirline.run()
