# OBD Collection Tools 

This repository contains python programs that collect and process diagnostic information collected from OBD interfaces.

To run:
```

python3 obd_logger.py

```
This will connect to an OBD device, discover what PIDs are available in the vehicle, and continuously poll the vehicle and output the collected values to a file called log.n (where n is advanced automatically by the utility).  Control C or kill -2 can be used to cleanly terminate the utility.

```

python3 obd_log_to_json.py [--js] <log file name>

```
This utility will process an OBD log processed by the obd_logger.py utility and create a JSON file or a JavaScript snippit (when executed with the --js option).

The OBD device I'm using is a Foseal Bluetooth device that implements the ELM 327 interface.

The logger requires obd.

```
pip3 obd
```

Files I've collected are available at https://obd-display-server.herokuapp.com.

