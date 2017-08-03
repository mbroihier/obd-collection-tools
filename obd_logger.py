'''
Created on Jul 7, 2017

@author: broihier
'''

import time
import math
import os
import re
import obd


class ObdTools:
    '''
    Python tools for collecting OBD information
    '''
    def __init__(self):
        '''
        Constructor
        '''
        self.log_count = 0
        self.log_file = None
        self.connection = None
        self.first_line = True

    def _advance_logs(self):
        '''
        Log file advancer
        '''
        names = os.listdir("./")
        logfile_pattern = re.compile(r"^log\.\d+")
        for name in names:
            if logfile_pattern.match(name):
                self.log_count = self.log_count + 1

    def _initialize(self):
        '''
        Initialize connection and log file
        '''
        no_ports = True
        while no_ports:
            ports = obd.scan_serial()
            if ports:
                no_ports = False
            else:
                print("no ports yet, waiting ...")
                time.sleep(5.0)
        self.connection = obd.OBD()
        self.connection.print_commands()  # all supported commands
        self.log_file = open("./log." + str(self.log_count), "w")

    def _build_header(self, header, command):
        '''
        Updates header with new title
        '''
        return_header = header
        if self.first_line:
            if return_header == '':
                return_header = "Time, " + command
            else:
                return_header += ", " + command
        return return_header

    def _log_entry(self, line, first_time):
        if first_time:
            self.log_file.write(line + "\n")
            self.first_line = False
        else:
            if line != '':
                time_stamp = math.floor(time.time())
                self.log_file.write(str(time_stamp) + line + "\n")

    def _terminate(self):
        '''
        Terminate connection and close log file
        '''
        if self.log_file != None:
            print("Closing log file")
            self.log_file.close()
        print("Controlled Shutdown....")
        if self.connection != None:
            self.connection.close()

    def obd_logger(self):
        '''
        Connect to OBD device and begin logging RPM.
        '''
        #obd.logger.setLevel(obd.logging.DEBUG)
        self._advance_logs()
        try:
            self._initialize()
            supported_commands = set(self.connection.supported_commands)
            updated_commands = set(supported_commands)
            while True:
                line = ''
                header = ''
                for i in updated_commands:  # log all supported data
                    try:
                        result = self.connection.query(i)
                        if str(result) != "None":
                            line += ", " + str(result)
                            header = self._build_header(header, result.command.desc)
                    except (ValueError, TypeError, NameError) as error_information:
                        print("Exception caught, continuing: {}".format(error_information))
                        supported_commands.remove(i) # prune out commands that are failing
                updated_commands = set(supported_commands)
                self._log_entry(header, self.first_line)
                self._log_entry(line, self.first_line)
                print("*****" + line)
        except KeyboardInterrupt:
            self._terminate()

if __name__ == '__main__':
    ObdTools().obd_logger()
