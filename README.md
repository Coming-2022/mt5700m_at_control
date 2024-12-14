# MT5700M PHY AT ETH Control

This is a Python script that provides a command-line interface for managing and interacting with a 5G cellular module. 
It allows you to perform various operations such as viewing signal strength, locking/unlocking cells, restarting the cellular module, and executing custom AT commands.

## Change Log
2024/12/09 Version 1.0.0, Add 5G Scan Cell

2024/12/14 Version 1.0.1, Repair ats processing logic to enable reconnection,set the return result function to make the return result clearer

## Features

- View 5G NR and LTE carrier Aomponent status
- View signal strength and quality
- Check lock status and lock/unlock cells
- Restart the cellular module
- Execute custom AT commands
- Perform initial configuration for cell scanning
- Scan for available cells and display detailed information

Currently includes the following features:
1. 📈 5G NR CC Status
2. 📶 View Signal
3. 🔒 Lock Status
4. 🔍 Scan Cell
5. 🔋 Restart Cellular
6. 🖥️  Other Command
7. ⏹ Exit

## Prerequisites

1. First, make sure that the MT5700N-CN AT network port is open (need to be implemented through the serial port, type-c to serial port):

```
AT^TDPCIELANCFG=2
AT^TDPMCFG=1,0,0,0
AT+CGDCONT=8,"IPV4V6"
AT^SETAUTODIAL=1,2 # Auto dial, send in USB connection mode
```

2. The default IP address of MT5700N-CN is 192.168.8.1, and the port is 20249. Make sure that the 192.168.8.1 address can be pinged, and the corresponding network port can be accessed by telnet.

```
ATI

Response:
Manufacturer: TD Tech Ltd.
Model: Modem V100R100C20B563
Revision: 21C20B563S000C000
IMEI: 86xxxxxxxxxxxx
+GCAP: +CGSM,+DS,+ES
```

3. Install the following prerequisites:

- Python 3.x
- `tabulate` library (install with `pip3 install -r requirements.txt`)

## Usage

1. Run the at server program on the Linux host:
```
python3 ats.py
```

2. Run the at client program on the Linux host:
```
python3 at.py
```

## Configuration

The script uses the following configuration values:

- `SERVER_IP`: The IP address of the server (default: `"192.168.8.1"`)
- `SERVER_PORT`: The port number of the server (default: `20249`)
- `BUFFER_SIZE`: The buffer size for receiving data (default: `2048 * 4`)
- `RETRY_DELAY`: The delay (in seconds) between connection retry attempts (default: `3`)
- `SOCKET_FILE`: The path to the Unix Domain Socket file (default: `"/tmp/at_socket.sock"`)

You can modify these values in the script if needed.

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).
