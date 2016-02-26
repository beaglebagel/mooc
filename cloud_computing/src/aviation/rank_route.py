from mrjob.job import MRJob, MRStep


class RankRoute(MRJob):
    '''
    Group 2.4
    For each route(origin -> destination), rank by mean on-time arrival performance.
    Capstone: Rank all the routes based on mean on-time arrival performance.

    Each file line is composed of the following 19 fields in order as is:

        0-4: year, month, dayofmonth, dayofweek, flight_date,
        5-9: unique_carrier, flightNum, origin, dest, crs_dep_time,
        10-14: dep_delay_min, dep_del_15, crs_arr_time, arr_delay_min, arr_del_15,
        15-20: cancelled, diverted

    '''

    def mapper(self, _, line):
        # @NOTE: for departure delay, try using dep_delay_min first..
        fields = line.strip().split('|')
        origin, destination, arr_delay_min = fields[7], fields[8], fields[13]
        route = '{o},{d}'.format(o=origin, d=destination)
        # [origin, destination] -> ( Delay, 1 ) ]
        try:
            yield route, (float(arr_delay_min), 1)
        except Exception as e:
            print route, arr_delay_min, e

    def combiner(self, route, delays_counts):
        # [origin, destination] -> ( delay_min, 1 )
        yield route, map(sum, zip(*delays_counts))

    def reducer(self, route, delays_counts):
        # [origin, destination] -> tuple ( delay_min, 1 )
        # @TODO: how to sort the output in reverse order?
        total_delay, count = map(sum, zip(*delays_counts))

        # [origin, destination] -> average delay_min
        yield route, total_delay / count

    def mapper2(self, route, delay):
        yield delay, route

    def reducer2(self, delay, routes):
        for route in routes:
            yield route, float(delay)

    def steps(self):
        return [
            MRStep(mapper=self.mapper, combiner=self.combiner, reducer=self.reducer),
            MRStep(mapper=self.mapper2, reducer=self.reducer2),
        ]

if __name__ == '__main__':
    RankRoute.run()
