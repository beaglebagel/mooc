'''
    Coursera Cloud Computing Capstone

    prepare_data.py created by Jaebin Lee on 1/20/2016.
    Data preparation script.
    Extracts the necessary fields from the mounted raw AWS EBS transportation data.
    Each input file(csv) is in zip format each residing in corresponding year directory.
    The script will recursively read all zip files, extract, filter and aggregate results into one output file(csv).
    This output file is to be copied into AWS S3 storage eventually to be loaded into AWS EMR for data analysis.
'''
import os
import csv
import natsort
import numpy as np
import pandas as pd
import zipfile

SOURCE_COLUMNS = ['Year', 'Month', 'DayofMonth', 'DayOfWeek', 'FlightDate',
                  'UniqueCarrier', 'AirlineID', 'FlightNum', 'Origin', 'OriginCityName',
                  'Dest', 'DestCityName', 'CRSDepTime', 'DepTime', 'DepDelay',
                  'DepDelayMinutes', 'DepDel15', 'CRSArrTime', 'ArrTime', 'ArrDelay',
                  'ArrDelayMinutes', 'ArrDel15', 'Cancelled', 'Diverted']
DEST_COLUMNS = ['year', 'month', 'dayofmonth', 'dayofweek', 'flight_date',
                'unique_carrier', 'airline_id', 'flight_num', 'origin', 'origin_city',
                'dest', 'dest_city', 'crs_dep_time', 'dep_time', 'dep_delay',
                'dep_delay_min', 'dep_del_15', 'crs_arr_time', 'arr_time', 'arr_delay',
                'arr_delay_min', 'arr_del_15', 'cancelled', 'diverted']

FILE_NAME = 'ontime_aggregate_sample.psv'
ZIP_FILE_NAME = 'ontime_aggregate_sample.zip'

def zipit(output_file, input_file):
    # gzip the file, remove the source file.
    if not os.path.isfile(input_file):
        raise ValueError('input file {0} does not exist!'.format(input_file))

    with zipfile.ZipFile(file=output_file, mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
        zf.write(input_file)


def extract(zip_files, output_root):
    output_root = output_root or './'
    output_file = os.path.join(output_root, FILE_NAME)

    # create new file here with header only.
    # with open(name=output_file, mode='wb') as fd:
    #     print 'Created new aggregate file: {0}'.format(output_file)
    #     csv.DictWriter(f=fd, fieldnames=DEST_COLUMNS).writeheader()

    with open(name=output_file, mode='a+b') as fd:

        for fpath in zip_files:
            print 'Reading file: %s' % fpath
            # read each zip files, extract/aggregate contents in one csv.
            try:
                zip_file = zipfile.ZipFile(fpath)
                for zip_obj in zip_file.infolist():
                    # we're only interested in csv file..
                    if zip_obj.filename.endswith('.csv'):
                        table = pd.read_csv(
                                zip_file.open(zip_obj)
                                # dtype={ 'Cancelled' : np.bool, 'Diverted' : np.bool }
                        )

                        # csv_file['OriginCityName'] = csv_file['OriginCityName'].map(lambda x: x.replace('"', '') if type(x) is str else '')
                        # filter out cancelled/diverted rows.
                        table = table[ (table.Cancelled == 0) & (table.Diverted == 0) ]
                        # export column subset as pipe separated lines.
                        table[SOURCE_COLUMNS].to_csv(fd, header=False, index=False, sep='|')
            except zipfile.BadZipfile as bzf:
                print 'Skipping {0} due to {1}'.format(fpath, bzf)


def walk(root):
    if not root:
        raise ValueError('Root directory(root arg) cannot be empty!')

    file_paths = []

    # iterate through all data dir/subdirs and extract/aggregate necessary file contents.
    for root, dirs, files in os.walk(root):
        for fname in natsort.natsorted(files):
            if fname.endswith('.zip'):
                path = '{root}/{file}'.format(root=root, file=fname)
                print 'Attaching file path: {0}'.format(path)
                file_paths.append(path)
                # print root, dirs, files
    return file_paths


def main():
    # Consider adding getopt in future.
    # ex > source_root = '/data/aviation/airline_ontime'

    source_root = '../data/airline_ontime'
    output_root = '../input/aviation'

    file_paths = walk(root=source_root)
    # aggregates = extract(['../data/1988/On_Time_On_Time_Performance_1988_1.zip'], output_root='../data')
    extract(file_paths, output_root=output_root)

if __name__ == '__main__':
    main()
