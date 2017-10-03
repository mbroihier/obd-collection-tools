#!/usr/bin/python3
'''
Created on Oct 1, 2017

@author: broihier
'''
import json
import re
import sys

class ObdLogToJson:
    '''
    Class to convert OBD log file to JSON
    '''
    def __init__(self, file_name):
        '''
        Constructor
        '''
        self.file_handle = open(file_name, "r")
        self.json_handle = open(file_name + ".json", "w")
        self.is_float = re.compile(r"( *-*\d+\.\d*)")
        self.is_int = re.compile(r"( *-*\d+)")
        self.obd_object = None

    def parse_log(self):
        '''
        Parser
        '''
        header = self.file_handle.readline().strip()
        labels = header.split("|")
        line = self.file_handle.readline().strip()
        series = {}
        labels.pop(0)
        for label in labels:
            series[label] = []
        while line != "":
            data_points = line.split("|")
            if len(data_points) != len(labels) + 1:
                line = self.file_handle.readline().strip()
                print("Error - Dropping line: " + line)
                continue
            time = int(data_points.pop(0))
            for label in labels:
                value = data_points.pop(0)
                match = self.is_float.search(value)
                if match:
                    value = float(match.group(0))
                else:
                    match = self.is_int.search(value)
                    if match:
                        value = int(match.group(0))
                    else:
                        value = 0 # not a numeric value - can't plot
                series[label].append([time, value])
            line = self.file_handle.readline().strip()
        self.obd_object = series

    def write_as_json(self):
        '''
        Write series object as JSON to disk
        '''
        json.dump(self.obd_object, self.json_handle)
        self.json_handle.close()


def main():
    '''
    main program
    '''
    utility = ObdLogToJson(sys.argv[1])
    utility.parse_log()
    utility.write_as_json()

if __name__ == '__main__':
    main()
    