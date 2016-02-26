from mrjob.job import MRJob, MRStep
from mrjob.util import bash_wrap
import time

class RankAirport(MRJob):
    """
    Group 1.1
    Rank the airport by 'numbers of flights' from/to the airport.
    Capstone: Top 10 airports of each category.

    Each file line is composed of the following 19 fields in order as is:

    ['Year', 'Month', 'DayofMonth', 'DayOfWeek', 'FlightDate', 'UniqueCarrier', 'FlightNum', 'Origin', 'Dest',
    'CRSDepTime', 'DepDelayMinutes', 'DepDel15', 'CRSArrTime', 'ArrDelayMinutes', 'ArrDel15', 'Cancelled', 'Diverted']

        0-4: year, month, dayofmonth, dayofweek, flight_date,
        5-9: unique_carrier, flightNum, origin, dest, crs_dep_time,
        10-14: dep_delay_min, dep_del_15, crs_arr_time, arr_delay_min, arr_del_15,
        15-20: cancelled, diverted

    """

    # def configure_options(self):
    #     super(RankAirport, self).configure_options()
    #     self.add_passthrough_option(
    #         '--mode', type='str', default='from', help='rank airport popularity based on [from/to] flights #')
    #
    # def load_options(self, args):
    #     super(RankAirport, self).load_options(args)
    #     print 'Loading Options: %s' % self.options
    #     self.mode = self.options.mode

    def reverse(self):
        # return bash_wrap("tail -r")
        return 'tac'

    def mapper(self, _, line):

        fields = line.strip().split('|')
        origin, destination = fields[7], fields[8]

        yield origin, 1
        yield destination, 1

    def combiner(self, airport, counts):
        yield airport, sum(counts)

    def reducer(self, airport, counts):
        # how to sort the output from max to min.
        yield airport, sum(counts)

    def mapper2(self, airport, count):
        yield '%012d' % int(count), airport

    def reducer2(self, count, airports):
        for airport in airports:
            yield airport, int(count)

    def steps(self):
        return [
            MRStep(mapper=self.mapper, combiner=self.combiner, reducer=self.reducer),
            MRStep(mapper=self.mapper2, reducer=self.reducer2),
            # MRStep(reducer_cmd=self.reverse())
        ]

if __name__ == '__main__':
    start = time.time()
    RankAirport.run()
    end = time.time()
    print '%s seconds' % (end - start)
