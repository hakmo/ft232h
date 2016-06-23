# Based on following code:
# https://github.com/chiefdome/libftdi/blob/master/examples/python/complete.py
# https://github.com/adafruit/Adafruit_Python_GPIO/blob/master/Adafruit_GPIO/FT232H.py
# http://www.intra2net.com/en/developer/libftdi/documentation/

# Import standard Python libraries
import time
import os
import sys

# Import ftdi1 module
import ftdi1 as ftdi

#BAUD, = sys.argv		# command line inputs

BAUD = 400000         # 400kHz, 2xNyquist for 100kHz I2C

FT232H_VID = 0x0403   # Default FTDI FT232H vendor ID
FT232H_PID = 0x6014   # Default FTDI FT232H product ID


# Initialize new context
ftdictx = ftdi.new()
if ftdictx == 0:
    print( 'failed to create new context: %d', ret )
    os._exit( 1 )

# Try to list FT232H devices
ret, devlist = ftdi.usb_find_all( ftdictx, FT232H_VID, FT232H_PID )
if ret < 0:
    print( 'ftdi_usb_find_all failed: %d (%s)' % ( ret, ftdi.get_error_string( ftdictx ) ) )
    os._exit( 1 )

print( 'Number of FTDI devices found: %d\n' % ret )
curnode = devlist
#i = 0
#while( curnode != None ):
#    ret, manufacturer, description, serial = ftdi.usb_get_strings( ftdictx, curnode.dev )
#    if ret < 0:
#        print( 'ftdi_usb_get_strings failed: %d (%s)' % ( ret, ftdi.get_error_string( ftdictx ) ) )
#        os._exit( 1 )
#    print( 'Device #%d: manufacturer="%s" description="%s" serial="%s"\n' % ( i, manufacturer, description, serial ) )
#    curnode = curnode.next
#    i += 1

# Open USB to the first FT232H							 
# TODO: Way to select which FT232H if multiple found, using usb_open_dev() with the device instance from devlist[]
ret = ftdi.usb_open( ftdictx, FT232H_VID, FT232H_PID )
if ret < 0:
    print( 'unable to open ftdi device: %d (%s)' % ( ret, ftdi.get_error_string( ftdictx ) ) )
    os._exit( 1 )

# Reset MPSSE by sending mask = 0x00 and mode = BITMODE_RESET
ret = ftdi.set_bitmode(ftdictx, 0x00, ftdi.BITMODE_RESET)
if ret < 0:
    print( 'unable to reset bitmode: %d (%s)' % ( ret, ftdi.get_error_string( ftdictx ) ) )
    os._exit( 1 )

# Configure the mode (see http://www.ftdichip.com/Support/Documents/DataSheets/ICs/DS_FT232H.pdf, section 4
#  http://www.ftdichip.com/Support/Documents/AppNotes/AN_232R-01_Bit_Bang_Mode_Available_For_FT232R_and_Ft245R.pdf,
#  and http://www.intra2net.com/en/developer/libftdi/documentation/ftdi_8h.html#a2250f7812c87a96ada7fd4f19b82f666)
ret = ftdi.set_bitmode( ftdictx, 0x00, ftdi.BITMODE_SYNCBB )		# Synchronous BitBang, D0-D7 input
if ret < 0:
    print( 'unable to set bitmode to syncbb: %d (%s)' % ( ret, ftdi.get_error_string( ftdictx ) ) )
    os._exit( 1 )

## Configure baud rate
ret = ftdi.set_baudrate(ftdictx, BAUD)
if ret < 0:
    print( 'unable to set baud: %d (%s)' % ( ret, ftdi.get_error_string( ftdictx ) ) )
    os._exit( 1 )

## Configure read buffer if using buffer-mode reads
#ret = ftdi.read_data_set_chunksize(ftdictx, 4096)

## Loop grabbing data and storing in array
print 'Gathering data. Press Ctrl-C to quit.'
output = []
try:
    while True:
	    # Sleep based on baudrate
        time.sleep(1.0/BAUD)
	    # Read the input and store to array
        ret, pins = ftdi.read_pins(ftdictx)			# reads pins directly, needs sleep time to be exact
        output.append(pins)
        #ret, databuf = ftdi.read_data(ftdictx)		# reads the data buffer, no need for exact timing (just fast enough to keep buffer from overflowing)
        #output.extend(databuf)
except KeyboardInterrupt:
    pass

## Write captured data to file
with open("output.bin", "wb") as outfile:
    writedata = bytearray(output)
    outfile.write(writedata)

## Cleanup: free devlist, reset bitmode, close usb, etc
ftdi.list_free(devlist)
ftdi.disable_bitbang(ftdictx)
ftdi.set_bitmode(ftdictx, 0x00, ftdi.BITMODE_RESET)
ret = ftdi.usb_close( ftdictx )
if ret < 0:
    print( 'unable to close ftdi device: %d (%s)' % ( ret, ftdi.get_error_string( ftdictx ) ) )
    os._exit( 1 )
    
print ('device closed')    
ftdi.free( ftdictx )