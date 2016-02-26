from mrjob.job import MRJob, MRStep


class RankAirportPerAirport(MRJob):
    """
    Group 2.2
    For each airport, rank the airport by on-time departure performance.
    Capstone: Top 10 airports per airport based on on-time departure performance.

    Each file line is composed of the following 19 fields in order as is:

        0-4: year, month, dayofmonth, dayofweek, flight_date,
        5-9: unique_carrier, flightNum, origin, dest, crs_dep_time,
        10-14: dep_delay_min, dep_del_15, crs_arr_time, arr_delay_min, arr_del_15,
        15-20: cancelled, diverted

    """

    # def configure_options(self):
    #     super(RankAirportPerAirport, self).configure_options()
    #     self.add_passthrough_option(
    #         '--mode', type='str', default='departure', help='rank [arrival/departure] performance')
    #
    # def load_options(self, args):
    #     super(RankAirportPerAirport, self).load_options(args)
    #     print 'Loading Options: %s' % self.options
    #     self.mode = self.options.mode

    def mapper(self, _, line):
        # @NOTE: for departure delay, try using dep_delay_min first..
        fields = line.strip().split('|')
        origin, destination = fields[7], fields[8]
        # delay = fields[-4] if self.mode == 'arrival' else fields[14]
        delay = fields[10]

        # [ origin, destination -> ( Delay, 1 ) ]
        yield (origin, destination), (float(delay), 1)

    def combiner(self, route, delays_counts):
        # [origin, destination] -> ( delay_min, 1 )
        yield route, map(sum, zip(*delays_counts))

    def reducer(self, route, delays_counts):
        # [origin, destination] -> tuple ( delay_min, 1 )
        # @TODO: how to sort the output in reverse order?
        total_delay, count = map(sum, zip(*delays_counts))

        # [origin,destination] -> average delay_min
        yield route, total_delay / count

    def mapper2(self, route, avg_delay):
        origin, destination = route[0], route[1]
        yield origin, (avg_delay, destination)

    def reducer2(self, origin, pair):
        sorted_pairs = sorted(pair, reverse=False)
        yield origin, sorted_pairs

    def mapper3(self, origin, sorted_pairs):
        reverse_pairs = [(destination, avg_delay) for avg_delay, destination in sorted_pairs]
        yield origin, reverse_pairs

    def steps(self):
        return [
            MRStep(mapper=self.mapper, combiner=self.combiner, reducer=self.reducer),
            MRStep(mapper=self.mapper2, reducer=self.reducer2),
            MRStep(mapper=self.mapper3)
        ]

if __name__ == '__main__':
    RankAirportPerAirport.run()
