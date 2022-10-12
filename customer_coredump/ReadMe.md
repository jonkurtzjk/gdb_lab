# CoreDump DA145xx
CoreDump DA145xx is a python script that allows for a hot attach to the Dialog DA145xx family.
This script will connect, halt the processor and dump the necessary registers and memory
required for post analylsis via GDB.  

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install requirements.
Python 3.0 or greater is required to run this script.

```bash
pip install -r requirements.txt
```

##Useage

Make sure J-Link is connected to a DA145xx target and preferably the only device connected
(This script does an autodetect but selects the lowest JLINK number if multiple are connected).


Run the python script with:

**Windows**:

````bash
python coredump_da145xx.py
````

**MAC | Linux**
````bash
python3 coredump_da145xx.py
````


The script should print out various information, including which Jlink was selected, the device
it detected, register values, and the corefile that it is created. 

Example:

````
JLink devices:
	480072641

Using JLink Serial Number:480072641
Device Detected DA14531

R0: 0x28000000
R1: 0x7fc9080
R2: 0x0
R3: 0x3800
R4: 0x7fc5038
R5: 0x50000000
R6: 0x1
R7: 0xffff
R8: 0xffffffff
R9: 0xffffffff
R10: 0xffffffff
R11: 0xffffffff
R12: 0x2c
SP: 0x7fc5028
LR: 0x7fc02d3
PC: 0x7fc034a
XPSR: 0x1000002
MSP: 0x7fc5028
PSP: 0xfffffffc
Created Core File: coredump_10_3_2022_16:25:54.581494.bin

````

***The core file and the AXF | ELF File will be needed for further anaylsis!***