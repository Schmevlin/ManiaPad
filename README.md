# ManiaPad
4 button macro pad for use in rhythm games, primarily for osu!/osu!Mania

### Parts List
* pcb based on the one in this repo
* raspberry pi pico
* 0.91" I2C SSD 1306 OLED Module
* 1x4 pin header
* 4 individual WS2812B leds
* (optional) 4 100nF 1206 SMD capacitors
* 4 kailh hotswap sockets
* 4 cherry mx style mechanical keyboard switches
* 2 6mm x 6mm x 4.3mm tactile switch (push button)
* 10 M3 x 16mm machine screws
* 10 M3 nuts
* 3D Printed Parts
  * 4 plate spacer
  * 2 key block
  * 10 button spacer
  * 1 bottom
  * 6 short spacer
  * 1 middle plate
  * 2 button extender

### Button modes/layout
Button modes and layouts are in the code as the "modes" variable, with a tuples of (function name, string name). The functions define what buttons are pressed and what behaviour is associated with each mode. To swap modes hold the top left button then press the top right button.
