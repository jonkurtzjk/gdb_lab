# Coredump Debugging

This python script is used in conjunction with a core file generated
by coredump_da145xx.py.  It takes in the elf | axf file and the core_xx.bin
file generated previously.  This creates a remote emulation with gdbstubs
and allows for gdb debugging.

## Installation

`pip install -r requirements.txt`

## Usage

Start this python script first in Terminal 1 then open GDB in an additional terminal.
#### Terminal 1

`python coredump_gdbserver.py PATH_TO_ELF PATH_TO_BIN`

Ex:

`python coredump_gdbserver.py ../../Keil_5/out_DA14531/Objects/empty_peripheral_template.axf ~/Desktop/coredump.bin`

#### Terminal 2

`arm-none-eabi-gdb`  - The setup for this is in `.gdbinit`



## GDB Init file
The .gdbinit file is helpful and setup already in this repo. 

## Helpful GDB commands

This displays all the register values.
````
info registers

(gdb) info registers
r0             0x28000000	671088640
r1             0x7fc9080	133992576
r2             0x0	0
r3             0x3800	14336
r4             0x7fc5038	133976120
r5             0x50000000	1342177280
r6             0x1	1
r7             0xffff	65535
r8             0xffffffff	4294967295
r9             0xffffffff	4294967295
r10            0xffffffff	4294967295
r11            0xffffffff	4294967295
r12            0x2c	44
sp             0x7fc5028	0x7fc5028
lr             0x7fc02d3	133956307
pc             0x7fc034a	0x7fc034a <NMI_HandlerC+170>
cpsr           0x1000002	16777218

````

We can issue bt for a backtrace:
````
bt
````

In a fault condition, the last stack frame is pushed since we are in an exception
and in some cases GDB can't unroll the stack frames.  In this case,
we can examine the stack or STATUS_BASE registers to find the stack frame
and set the registers accordingly:

This gives us 128 bytes of memory at the STATUS_BASE FOR NMI
````
x /128a 0x7fc9050
````

We can then take the stack frame and set registers with:

````
set $pc = 0xXXXXXXXX
set $lr = 0xXXXXXXXX
set $sp = 0xXXXXXXXX
````

At this point, we can then issue a bt and get a better back trace.
GDB has limitations with back trace and it only pops the last stack frame occasionally.
In this case, we can examine the stack with symbols in this manner:

````
x /256a $sp
````

Additionally, we can example variables with the symbol or address with 'p'.


***At this point, we have full GDB functionality and can use any command for program access***





