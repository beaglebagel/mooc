from mrjob.job import MRJob, MRStep


class RankAirlinePerRoute(MRJob):
    """
    Group 2.3
    For each route(origin -> destination), rank the airline by on-time arrival performance.
    Capstone: Top 10 airlines per routes based on on-time arrival performance.

    Each file line is composed of the following 19 fields in order as is:

        0-4: year, month, dayofmonth, dayofweek, flight_date,
        5-9: unique_carrier, flightNum, origin, dest, crs_dep_time,
        10-14: dep_delay_min, dep_del_15, crs_arr_time, arr_delay_min, arr_del_15,
        15-20: cancelled, diverted

    """

    def mapper(self, _, line):
        # @NOTE: for departure delay, try using dep_delay_min first..
        fields = line.strip().split('|')
        origin, destination, airline = fields[7], fields[8], fields[5]
        delay = fields[-4]

        # [origin, destination, airline] -> ( Delay, 1 ) ]
        yield (origin, destination, airline), (float(delay), 1)

    def combiner(self, route, delays_counts):
        # [origin, destination, airline] -> ( delay_min, 1 )
        yield route, map(sum, zip(*delays_counts))

    def reducer(self, route, delays_counts):
        # [origin, destination, airline] -> tuple ( delay_min, 1 )
        total_delay, count = map(sum, zip(*delays_counts))

        # [origin, destination, airline] -> average delay_min
        yield route, total_delay / count

    def mapper2(self, route, avg_delay):
        origin, destination, airline = route[0], route[1], route[2]
        yield (origin,destination), (avg_delay, airline)

    def reducer2(self, route, pair):
        sorted_pairs = sorted(pair, reverse=False)
        yield route, sorted_pairs

    def mapper3(self, route, sorted_pairs):
        reverse_pairs = [(airline, avg_delay) for avg_delay, airline in sorted_pairs]
        yield route, reverse_pairs

    def steps(self):
        return [
            MRStep(mapper=self.mapper, combiner=self.combiner, reducer=self.reducer),
            MRStep(mapper=self.mapper2, reducer=self.reducer2),
            MRStep(mapper=self.mapper3)
        ]

if __name__ == '__main__':
    RankAirlinePerRoute.run()
