from mrjob.job import MRJob, MRStep
from datetime import datetime

class BuildRoute(MRJob):
    """
    Group 3.4
    Build all possible 3-city routes (A-B-C) that are two days apart, depart A before 12PM, depart B after 12PM.
    Capstone: Analyze and build all possible routes per user's city relay inputs ordered by delay performance.

    Each file line is composed of the following 19 fields in order as is:

        0-4: year, month, dayofmonth, dayofweek, flight_date,
        5-9: unique_carrier, flightNum, origin, dest, crs_dep_time,
        10-14: dep_delay_min, dep_del_15, crs_arr_time, arr_delay_min, arr_del_15,
        15-20: cancelled, diverted

    """

    DATE_FORMAT = '%Y-%m-%d'

    @classmethod
    def delta(cls, day1, day2):
        '''
        :return: return the day difference between day1 and day2.
        '''
        day1 = datetime.strptime(day1, cls.DATE_FORMAT)
        day2 = datetime.strptime(day2, cls.DATE_FORMAT)
        return (day2 - day1).days

    def mapper(self, _, line):
        # @NOTE: for departure delay, try using dep_delay_min first..
        fields = line.strip().split('|')
        if fields[0] != '2008': # only process year 2008's flights.
            return
        year, date, flight_no, departure_time = fields[0], fields[4], fields[6], fields[9]
        origin, destination, dep_delay_min = fields[7], fields[8], fields[10]

        # each origin(A) can be final origin or layover.
        # each destination(B) can be layover or final destination.
        # Emit tuples for each case, with indicator 0: leg1, 1: leg2.
        # ex> (A-B) -> (A, (0, A-B)), (B, (1, A-B))
        route = '{o},{d}'.format(o=origin, d=destination)
        yield destination, (0, origin, destination, date, flight_no, int(departure_time), float(dep_delay_min))
        yield origin, (1, origin, destination, date, flight_no, int(departure_time), float(dep_delay_min))

    def combiner(self, airport, details):
        # [airport] -> [ [0/1], route, date, etc.. ]
        leg1s, leg2s = [], []
        for detail in details:
            if detail[0] == 0 and detail[5] < 1200: # leg1 should depart before 12:00PM.
                leg1s.append(detail)
            elif detail[0] == 1 and detail[5] > 1200: # leg2 should depart after 12:00PM.
                leg2s.append(detail)
        yield airport, (leg1s, leg2s)

    def reducer(self, airport, legs_pairs):
        # [airport] -> ( leg1s, leg2s )
        leg1s, leg2s = [], []
        for legs_pair in legs_pairs:
            leg1s.append(legs_pair[0])
            leg2s.append(legs_pair[1])

        for leg1 in leg1s:
            for leg2 in leg2s:
                # check dates are 2 days apart.
                if self.delta(leg1[3], leg2[3]) == 2:
                    yield leg1, leg2

    def mapper2(self, leg1, leg2):
        # leg1 and leg2 are valid pairs to form routes(A-B-C). So form them along with details.
        full_route_date = '{A},{B},{C},{Date}'.format(A=leg1[1], B=leg1[1], C=leg2[1], Date=leg1[3])
        yield full_route_date, ( sum(leg1[-1], leg2[-2]), (leg1, leg2) )

    def reducer2(self, full_route_date, delay_leg_pairs):
        # generate Route,Date pair -> [ leg1 flight#, leg1 dep time, leg2 flight#, leg2 dep time, mean delay ]
        sorted_leg_pairs = sorted(delay_leg_pairs, reverse=True)
        leg_pair = sorted_leg_pairs[0]
        leg1, leg2 = leg_pair[1][0], leg_pair[1][1]
        yield full_route_date, (leg1[4], leg1[5], leg2[4], leg2[5], leg_pair[0])

    def steps(self):
        return [
            MRStep(mapper=self.mapper, combiner=self.combiner, reducer=self.reducer),
            MRStep(mapper=self.mapper2, reducer=self.reducer2)
        ]

if __name__ == '__main__':
    BuildRoute.run()
