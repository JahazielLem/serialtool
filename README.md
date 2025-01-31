# serialtool
Serial tool for communication with serial devices

## Usage
Start connection with default baudrate (115200)
```bash
python3 sercom.py /dev/tty.usbmode1000
```
Start connection with custom baudrate
```bash
python3 sercom.py /dev/tty.usbmode1000 -b 9600
```

To exit use the key binding `Ctrl + C` to clean screen `Ctrl + l`

## Features
[x] Read serial port
[x] Write commands
[x] Show time
[x] Show Hex data

## TODO
- Add more complex serial configuration
- Error handlers
- Configuration of formats information
- Export history
- Show commands history on tab
- Autobaudrate
- Send files ?
- Scripting