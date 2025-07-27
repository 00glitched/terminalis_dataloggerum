# terminalis_dataloggerum
Terminal user interface datalogger in python for serial based communication

ToDo-List:

- [x] - Serial communication 
- [x] - Text Interface
- [ ] - Left button calls
	- [x] - Serial connection
	- [ ] - Config
	- [ ] - Init/Stop
	- [ ] - Plot
- [ ] - Right panel
	- [ ] - Data
    - [x] - Terminal
- [ ] - Async

## Dependencies
- Matplotlib
- Textual
- pySerial

## How to run
```sh
python3 main.py
```

## Commands structure
Order: First word that indicate the routine

Suborder: Variable/order to run the routine

Value: Input value to run the routine
```sh
order --suborder0 value00 value01 --suborder1 value10
```
Example:
```sh
set --pin5 True
```