# Define variables
ARDUINO_CLI := arduino-cli
BOARD := arduino:avr:mega
PORT := /dev/ttyACM0
SKETCH := ./main/main.ino
LIBRARIES :=

# Default target
all: compile upload

# Compile the sketch
compile:
	$(ARDUINO_CLI) compile --fqbn $(BOARD) $(SKETCH) $(LIBRARIES)

# Upload the sketch to the Arduino
upload: compile
	$(ARDUINO_CLI) upload -p $(PORT) --fqbn $(BOARD) $(SKETCH)

# Clean up compiled files
clean:
	rm -rf .arduino*

# Install a library
install-lib:
	$(ARDUINO_CLI) lib install $(LIBRARY_NAME)

# List available boards
list-boards:
	$(ARDUINO_CLI) board listall

# Update the Arduino core index
update-index:
	$(ARDUINO_CLI) core update-index

# Install the Arduino core for the board
install-core:
	$(ARDUINO_CLI) core install arduino:avr
	$(ARDUINO_CLI) core install $(BOARD)
