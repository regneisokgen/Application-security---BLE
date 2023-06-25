CPUTemp
========== 
Python GATT server example for the Raspberry Pi. It leverages the existing MQTT publisher/subscribe model to provide BLE characteristic for read/write. 

Application vulnerability 
----- 
This is to demostrate application vulnerabilities of BLE when TK is exchanged using Just Works. In Just Works, the TK is set to 0. Which makes brute-forcing STK to be very do-able. There is also no protection against MITM. 

Usage 
----- 
    python3 windmilble.py

The server should by accessable by any BLE client; I like to use
the 'nRF Connect' app on my Android phone.

The service (UUID 00000001-710e-4a5b-8d75-3e5b444b3c3f) provides 
two characteristics:

UUID 00000002-710e-4a5b-8d75-3e5b444b3c3f: a read/notify
characteristic representing the Pi's CPU temperature as a string.

UUID 00000003-710e-4a5b-8d75-3e5b444b3c3f: a read/write
characteristic indicating the units to use to display the
temperature; 'F' or 'C'.
