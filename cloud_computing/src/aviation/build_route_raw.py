from collections import defaultdict
from datetime import datetime
import calendar

class BuildRouteRaw:
    '''
    Each file line is composed of the following 19 fields in order as is:

        0-4: year, month, dayofmonth, dayofweek, flight_date,
        5-9: unique_carrier, flightNum, origin, dest, crs_dep_time,
        10-14: dep_delay_min, dep_del_15, crs_arr_time, arr_delay_min, arr_del_15,
        15-20: cancelled, diverted
    '''

    DATE_FORMAT = '%Y-%m-%d'

    @classmethod
    def delta(cls, day1, day2):
        day1 = datetime.strptime(day1, cls.DATE_FORMAT)
        day2 = datetime.strptime(day2, cls.DATE_FORMAT)
        return (day2 - day1).days

    def build(self, input_file, output_file, month_to_process):

        day = calendar.monthrange(2008, int(month_to_process))[1]
        airport_to_details = defaultdict(list)
        airport_to_legs = {}

        print 'reading', input_file
        print 'stage 0'
        count = 0

        with open(input_file, 'r') as fp:
            for line in fp:
                fields = line.strip().split('|')
                if fields[0] != '2008': # only process year 2008's flights.
                    return
                year, date, flight_no, departure_time = fields[0], fields[4], fields[6], fields[9]
                origin, destination, dep_delay_min = fields[7], fields[8], fields[10]

                airport_to_details[origin].append( (1, origin, destination, date, flight_no, int(departure_time), float(dep_delay_min)) )
                airport_to_details[destination].append( (0, origin, destination, date, flight_no, int(departure_time), float(dep_delay_min)) )

                count += 1
                if count % 100000 == 0:
                    print count, 'processed'

        print 'stage 1', len(airport_to_details), 'to process'
        for airport, details in airport_to_details.iteritems():
            # print airport, details
            for detail in details:
                if detail[0] == 0:
                    if detail[5] < 1200:
                        if airport not in airport_to_legs:
                            airport_to_legs[airport] = defaultdict(list)
                        airport_to_legs[airport][0].append(detail)
                else:
                    if detail[5] > 1200:
                        if airport not in airport_to_legs:
                            airport_to_legs[airport] = defaultdict(list)
                        airport_to_legs[airport][1].append(detail)

        del airport_to_details
        pairs = []

        print 'stage 2', len(airport_to_legs), 'to process'
        for airport, leg_pairs in airport_to_legs.iteritems():
            leg1s, leg2s = leg_pairs[0], leg_pairs[1]

            for leg1 in leg1s:
                for leg2 in leg2s:
                    if self.delta(leg1[3], leg2[3]) == 2:
                        # add
                        pairs.append([leg1, leg2])

        del airport_to_legs
        # print pairs
        route_to_details = defaultdict(list)

        print 'stage 3', len(pairs), 'to process'
        for pair in pairs:
            leg1, leg2 = pair[0], pair[1]
            full_route_date = '{A},{B},{C},{Date}'.format(A=leg1[1], B=leg1[2], C=leg2[2], Date=leg1[3])
            route_to_details[full_route_date].append( ( sum([leg1[-1], leg2[-1]] ), (leg1, leg2) ) )

        del pairs

        full_route_to_details = {}
        line = '{frd},{fno1},{dep1},{fno2},{dep2},{delay}\n'

        # print route_to_details
        print 'start stage 4 writing file..', len(route_to_details), 'to process.'
        with open(name=output_file, mode='w+') as fd:
            for route, details in route_to_details.iteritems():
                # print route, details
                sorted_leg_pairs = sorted(details, reverse=True)
                leg_pair = sorted_leg_pairs[0]
                leg1, leg2 = leg_pair[1][0], leg_pair[1][1]
                # write each file line here..
                fd.write(line.format(frd=route, fno1=leg1[4], dep1=leg1[5], fno2=leg2[4], dep2=leg2[5], delay=leg_pair[0]))

if __name__ == '__main__':
    import sys
    input_file, output_file, month = sys.argv[1], sys.argv[2], sys.argv[3]
    builder = BuildRouteRaw()
    builder.build(input_file, output_file, month)