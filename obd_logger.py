'''
Created on Jul 7, 2017

@author: broihier
'''

import time
import math
import os
import re
import sys
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
                try:
                    self.connection = obd.OBD()
                    keep_commands = set(self.connection.supported_commands)
                    for i in self.connection.supported_commands:
                        try:
                            if i.mode != 1: # keep only mode 1 commands
                                keep_commands.remove(i)
                                print("Removing command list index {}".format(i))
                        except ValueError as error:
                            print("while pruning supported command list, got: {}".format(error))
                            keep_commands.remove(i)
                    self.connection.supported_commands = set(keep_commands)
                    self.connection.print_commands()  # all supported commands
                    if len(self.connection.supported_commands) == 0:
                        print("Error - OBD interface claims there are no supported commands")
                        self.connection.close()
                        no_ports = True
                        time.sleep(5.0) # try again
                except obd.utils.serial.SerialException:
                    print("Error - serial connection received nothing")
                    sys.exit(-1)
            else:
                print("no ports yet, waiting ...")
                time.sleep(5.0)
        self.log_file = open("./log." + str(self.log_count), "w")

    def _build_header(self, commands):
        '''
        Create header with currently active commands
        '''
        return_header = "Time"
        for command in commands:
            return_header += "| " + command.desc
        return return_header

    def _log_entry(self, line, first_time, header):
        if first_time: # write only header - suppress line
            self.log_file.write(header + "\n")
            self.first_line = False
        else: # write line
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
                if len(updated_commands) == 0:
                    print("Error - due to errors in transmission, there are no valid OBD commands")
                    self._terminate()
                    sys.exit(-1)
                for i in updated_commands:  # log all supported data
                    try:
                        result = self.connection.query(i)
                        if str(result) != "None":
                            line += "| " + str(result)
                        else: # prune out commands that are failing
                            if self.first_line:
                                print("removing {} because response was None".format(i))
                                supported_commands.remove(i)
                                if supported_commands == updated_commands:
                                    print("!!supported/updated_commands should no longer match")
                    except (ValueError, TypeError, NameError) as error_information:
                        print("Exception {} caught, continuing: {}".format(type(error_information),
                                                                           error_information))
                        supported_commands.remove(i) # prune out commands that are failing
                        if supported_commands == updated_commands:
                            print("!!supported_command should no longer match updated_commands")
                        self.first_line = True # reprint header
                updated_commands = set(supported_commands)
                header = self._build_header(updated_commands)
                self._log_entry(line, self.first_line, header)
                print("*****" + line)
        except KeyboardInterrupt:
            self._terminate()

if __name__ == '__main__':
    ObdTools().obd_logger()
