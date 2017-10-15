#!/usr/bin/python3
'''
Created on Oct 1, 2017

@author: broihier
'''
import getopt
import json
import os
import re
import sys
import time

class ObdLogToJson:
    '''
    Class to convert OBD log file to JSON
    '''
    def __init__(self, file_name, file_type):
        '''
        Constructor
        '''
        self.file_handle = open(file_name, "r")
        self.file_type = file_type
        if file_type == "javascript":
            self.output_handle = open("plot_data_", "w")
        else:
            self.output_handle = open(file_name + ".json", "w")
        self.is_float = re.compile(r"( *-*\d+\.\d*)")
        self.is_int = re.compile(r"( *-*\d+)")
        self.obd_object = None
        self.time_of_series = None

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
        last_time = 0
        while line != "":
            data_points = line.split("|")
            if len(data_points) != len(labels) + 1:
                line = self.file_handle.readline().strip()
                print("Error - Dropping line: " + line)
                continue
            time_of_sample = int(data_points.pop(0))
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
                series[label].append([time_of_sample, value])
            line = self.file_handle.readline().strip()
            last_time = time_of_sample
        self.obd_object = series
        self.time_of_series = time.gmtime(last_time)

    def write(self):
        '''
        Public write method
        '''
        if self.file_type == "json":
            self._write_as_json()
        else:
            self._write_as_javascript()

    def _write_as_json(self):
        '''
        Write series object as JSON to disk
        '''
        json.dump(self.obd_object, self.output_handle)
        self.output_handle.close()

    def _write_as_javascript(self):
        '''
        Write series object as JavaScript snippit to disk
        '''
        json_string = "var reviver = function(name, value) {"
        json_string += " if (name === \"0\") {"
        json_string += "   value = new Date(value * 1000);"
        json_string += " }"
        json_string += " return value;"
        json_string += "};"
        json_string += "var collectedData = JSON.parse('"
        json_string += json.dumps(self.obd_object)
        json_string += "');"
        self.output_handle.write(json_string)
        self.output_handle.close()

        names = os.listdir("./")
        date_stamp = time.strftime("%m_%d_%Y", self.time_of_series)
        plot_data_file_pattern = re.compile(r"^plot_data_" + date_stamp +".*")
        log_count = 0
        for name in names:
            if plot_data_file_pattern.match(name):
                log_count = log_count + 1
        new_file_name = "plot_data_" + date_stamp
        if log_count > 0:
            new_file_name += "_" + str(log_count)
        new_file_name += ".js"
        os.rename("plot_data_", new_file_name)

def main():
    '''
    main program
    '''
    file_name = ""
    file_type = "json"
    help_string = "python3 obd_log_to_json [--js] <file to convert>"
    try:
        opts, args = getopt.getopt(sys.argv[1:], "", ["js"])
        for opt, arg in opts:
            if opt == "--js":
                file_type = "javascript"
            else:
                print(help_string)
                sys.exit(-1)
            #print("option={}, argument={}".format(opt, arg))
        for arg in args:
            if file_name == "":
                file_name = arg
            else:
                print(help_string)
                sys.exit(-1)
            #print("argument={}".format(arg))
        if file_name == "":
            print(help_string)
            sys.exit(-1)
    except getopt.GetoptError:
        print(help_string)
        sys.exit(-1)

    utility = ObdLogToJson(file_name, file_type)
    utility.parse_log()
    utility.write()

if __name__ == '__main__':
    main()
    