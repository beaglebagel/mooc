from mrjob.job import MRJob, MRStep

class RankAirlinePerAirport(MRJob):
    """
    Group 2.1
    For each airport, rank the airline by on-time departure performance.
    Capstone: Top 10 airlines per airport based on on-time departure performance.

    Each file line is composed of the following 19 fields in order as is:

        0-4: year, month, dayofmonth, dayofweek, flight_date,
        5-9: unique_carrier, flightNum, origin, dest, crs_dep_time,
        10-14: dep_delay_min, dep_del_15, crs_arr_time, arr_delay_min, arr_del_15,
        15-20: cancelled, diverted

    """

    def mapper(self, _, line):
        # @NOTE: for departure delay, try using dep_delay_min first..
        fields = line.strip().split('|')
        airline, airport = fields[5], fields[7]
        # delay = fields[-4] if self.mode == 'arrival' else fields[14]
        delay = fields[10]

        # [ airport,airline -> ( Delay, 1 ) ]
        yield (airport, airline), (float(delay), 1)

    def combiner(self, key, delays_counts):
        # [airport,airline] -> ( delay_min, 1 )
        yield key, map(sum, zip(*delays_counts))

    def reducer(self, key, delays_counts):
        # [airport,airline] -> tuple ( delay_min, 1 )
        total_delay, count = map(sum, zip(*delays_counts))

        # [airport,airline] -> average delay_min
        yield key, total_delay / count

    def mapper2(self, key, avg_delay):
        airport, airline, = key[0], key[1]
        yield airport, (avg_delay, airline)

    def reducer2(self, airport, pair):
        sorted_pairs = sorted(pair, reverse=False)
        yield airport, sorted_pairs

    def mapper3(self, airport, sorted_pairs):
        reverse_pairs = [(airline, avg_delay) for avg_delay, airline in sorted_pairs]
        yield airport, reverse_pairs

    def steps(self):
        return [
            MRStep(mapper=self.mapper, combiner=self.combiner, reducer=self.reducer),
            MRStep(mapper=self.mapper2, reducer=self.reducer2),
            MRStep(mapper=self.mapper3)
        ]

if __name__ == '__main__':
    RankAirlinePerAirport.run()
