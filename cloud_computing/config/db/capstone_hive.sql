create external table ontime (
  year smallint, 
  month tinyint, 
  dayofweek tinyint, 
  unique_carrier string, 
  airline_id smallint, 
  origin string, 
  origin_city string, 
  dest string, 
  dest_city string, 
  crs_dep_time smallint, 
  dep_time smallint, 
  dep_delay smallint, 
  dep_delay_min smallint, 
  dep_delay15 tinyint,
  crs_arr_time smallint, 
  arr_time smallint, 
  arr_delay smallint, 
  arr_delay_min smallint, 
  arr_delay15 tinyint,
  cancelled boolean, 
  diverted boolean )
comment 'aviation ontime data'
row format delimited
fields terminated by '|'
lines terminated by '\n'
stored as textfile
-- tblproperties ("skip.header.line.count"="1");
-- location '/input/ontime_aggregate.psv';

load data inpath '/input/ontime_aggregate.psv' into table ontime;
-- 'load data local inpath' means to load from local file system.
-- overwrite into table ontime; - reload the table.
-- hdfs://<NAMENODE>:<PORT>/user/pdi/weblogs/parse 

exit;