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

    def advance_logs(self):
        '''
        Log file advancer
        '''
        names = os.listdir("./")
        logfile_pattern = re.compile(r"^log\.\d+")
        for name in names:
            if logfile_pattern.match(name):
                self.log_count = self.log_count + 1


    def obd_logger(self):
        '''
        Connect to OBD device and begin logging RPM.
        '''
        obd.logger.setLevel(obd.logging.DEBUG)
        no_ports = True
        log_file = None
        connection = None
        first_line = True
        self.advance_logs()
        try:
            while no_ports:
                ports = obd.scan_serial()
                if ports:
                    no_ports = False
                else:
                    print("no ports yet, waiting ...")
                time.sleep(5.0)
            connection = obd.OBD()
            connection.print_commands() # all supported commands
            log_file = open("./log." + str(self.log_count), "w")
            while True:
                line = ''
                header = ''
                for i in connection.supported_commands:  # log all supported data
                    try:
                        result = connection.query(i)
                        #if result.command == obd.commands['STATUS']:
                        #    line += " " + str(result.value.MIL)
                        #    line += " " + str(result.value.DTC_count)
                        #else:
                        if str(result) != "None":
                            line += ", " + str(result)
                            if header == '':
                                header = "Time, " + str(result.command)
                            else:
                                header += ", " + str(result.command)
                    except (ValueError, TypeError, NameError) as error_information:
                        print("Exception caught, continuing: {}".format(error_information))
                time_stamp = math.floor(time.time())
                print("*****" + line)
                if first_line:
                    log_file.write(header + "\n")
                    first_line = False
                log_file.write(str(time_stamp) + " " + line + "\n")
        except KeyboardInterrupt:
            if log_file != None:
                print("Closing log file")
                log_file.close()
            print("Controlled Shutdown....")
            if connection != None:
                connection.close()

if __name__ == '__main__':
    ObdTools().obd_logger()
