create keyspace aviation with replication = {'class':'SimpleStrategy', 'replication_factor':3};
describe keyspaces

create table airport (
	id int,
	airport text, 
	traffic int, 
	primary key(id, traffic, airport)
) 
with clustering order by (traffic desc, airport asc);

"insert into airport (id, airport, traffic) values (%d, '%s', %d);"

create table airline (
	id int,
	airline text,
	mean_arrival_delay double,
	primary key(id, mean_arrival_delay, airline)
)
with clustering order by (mean_arrival_delay asc, airline asc);

"insert into airline (airline, mean_arrival_delay) values ('%s', %d);"

create table weekday (
	weekday string PRIMARY_KEY,
	mean_arrival_delay double
);

"insert into weekday (weekday, mean_arrival_delay) values ('%s', %d);"

CREATE TABLE route (
    origin text,
    destination text,
    mean_arrival_delay double,
    PRIMARY KEY ((origin, destination), mean_arrival_delay)
) WITH CLUSTERING ORDER BY (mean_arrival_delay ASC);

create table route2 (
	origin text,
	destination text,
	mean_arrival_delay double,
	primary key( origin, destination, mean_arrival_delay)
)
with clustering order by (airline asc);

create table rank_airport_per_airport (
	airport text,
	airports list<text> ,
	mean_departure_delays list<double>,
	primary key(airport)
);

create table rank_airline_per_airport (
	airport text,
	airlines list<text> ,
	mean_departure_delays list<double>,	
	primary key(airport)
);

create table optimal_route (
	origin text,
	overlay text,
	destination text,
	date text,
	leg1_flight_no int,
	leg1_departure_time int,
	leg2_flight_no int,
	leg2_departure_time int,
	mean_arrival_delay double,
	primary key( origin, overlay, destination, date)
);