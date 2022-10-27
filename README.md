# LAB Instructions

This is a ReadMe to guide you through GDB Lab demo. The customer_coredump folder is not necessary for this lab, but is provided as it is used to generate the coredump file for DA145xx family.  

## Tools Setup 

- Make sure Python 3 is installed (If you have SmartSnippets Studio, then python 3v5 is installed under the Smart Snippets directory.  For Windows:  C:/Diasemi/SmartSnippetsStudio2.x.x/Python35)
- To make it easier, make sure that your Python location is on the PATH variable.  
- Verify by opening command prompt and entering 
```
python --version
```
- Next make sure pip is installed.  [Windows Pip Installer Guide](https://www.geeksforgeeks.org/how-to-install-pip-on-windows/)
- via terminal, navigate to your coredump_server folder and run the following command:
```
pip install -r requirements.txt
```
- Verify that arm-none-eabi-gdb | arm-non-eabi-gdb.exe is recognized on the path.  

## Getting the lab started
1. Navigate to the coredump_server with two seperate terminals.  **It's necessary that gdb is run from within the coredump folder.**
2. In Terminal # 1, type the following:

**For Ubuntu | MAC**
```
python3 coredump_gdbserver.py ../files/lab.axf ../files/coredump_lab.bin  --debug
```

**For Windows**
```
python coredump_gdbserver.py ../files/lab.axf ../files/coredump_lab.bin  --debug
```

3. In Terminal #2 type the following (if you get an error and don't see this output skip to step 4)
```
arm-none-eabi-gdb
```

You should see the following on Terminal #1
```
[INFO][gdbstub] Log file: ../files/coredump_lab.bin
[INFO][gdbstub] ELF file: ../files/lab.axf
[INFO][parser] Reason: K_ERR_SPURIOUS_IRQ
[INFO][parser] Pointer size 32
[INFO][parser] Memory: 0x7fc0000 to 0x7fcbfff of size 49151
[INFO][parser] ELF Section: 0x7fc0000 to 0x7fc009f of size 160 (read-only data)
[INFO][parser] ELF Section: 0x7fc00a0 to 0x7fc4cfb of size 19548 (text)
[INFO][gdbstub] Waiting GDB connection on port 1234...

```

You should see the following on Terminal #2:

```
GNU gdb (GNU Tools for Arm Embedded Processors 7-2018-q2-update) 8.1.0.20180315-git
Copyright (C) 2018 Free Software Foundation, Inc.
License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.  Type "show copying"
and "show warranty" for details.
This GDB was configured as "--host=x86_64-linux-gnu --target=arm-none-eabi".
Type "show configuration" for configuration details.
For bug reporting instructions, please see:
<http://www.gnu.org/software/gdb/bugs/>.
Find the GDB manual and other documentation resources online at:
<http://www.gnu.org/software/gdb/documentation/>.
For help, type "help".
Type "apropos word" to search for commands related to "word".
HardFault_HandlerC (hardfault_args=<optimized out>) at ..\..\..\..\..\sdk\platform\arch\main\/hardfault_handler.c:158
158	..\..\..\..\..\sdk\platform\arch\main\/hardfault_handler.c: No such file or directory.
(gdb) 

```

4.  With Windows or Ubuntu, you could get an error about the .gdbinit file.   A quick work around is to call arm-none-eabi-gdb with additional parameters that point to your .gdbinit file.  For example (Replace C:\MY_DIRECTORY with your folder location):

```
arm-none-eabi-gdb -iex "set auto-load safe-path C:\MY_DIRECTORY\gdb_lab\coredump_server\.gdbinit"
```

## Lab Instructions

1. Initially we see we are in a Hardfault on the original display and we can verify this on (gdb) by issueing a backtrace command.
```
(gdb)bt
```

2.  We can also look at all of the registers with:

```
(gdb) info registers
```

3. GDB Struggles with Exception Frames, so we must manually pop off the stack.  We know we can find the stack frame memory address by looking for the STATUS_BASE in the Hardfault_Handler:

```
(gdb)x /4x 0x7fc9000
```

4.  Let's visually see the stack frame by copying the address from the previous command, using the following command:

```
(gdb)x /32a 0x07fc5208
```

5. We know that a stack frame on the M0+ will look like this:  r0, r1, r2, r3, r12, lr, pc, cpsr.  So let's set all of the registers to the values on the stack, effectively popping off the exception frame.

```
(gdb) set $r0 = 0x0
(gdb) set $r1 = 0x0
(gdb) set $r2 = 0x7fc8d30
(gdb) set $r3 = 0x2
(gdb) set $r12 = 0x4c
(gdb) set $lr = 0x7fc2cc5
(gdb) set $pc = 0x0
(gdb) set $cpsr = 0x60000000
```

We also have to 'pop' off the stack manually.  The stack frame is always a standard stack frame on M0+, so we know its 32 bytes.

```
(gdb) set $sp += 32
```

6.  Now let's run a backtrace again:

```
(gdb)bt
```

7.  We now know where it faulted, function wise, but notice that GDB can't unroll the call trace? It's because there was a null pointer in the PC, we need to understand how this happened:

```
#0  0x00000000 in ?? ()
#1  0x07fc2cc4 in user_on_connection (connection_idx=0 '\000', param=0x7fc5208) at ..\src\/user_empty_peripheral_template.c:67
#2  0x00000000 in ?? ()
Backtrace stopped: previous frame identical to this frame (corrupt stack?)
```

8.  We see that the user_on_connection was in the LR and the PC was changed to zero, let's look at the disassembly of user_on_connection:

```
(gdb)disassemble user_on_connection
```

9.  You should see the disassembly of the function printout.  Let's see where in the function we linked to (subtract one from the link register):

```
   0x07fc2ca2 <+0>:	push	{r4, r5, r6, lr}
   0x07fc2ca4 <+2>:	mov	r4, r1
   0x07fc2ca6 <+4>:	mov	r5, r0
   0x07fc2ca8 <+6>:	bl	0x7fc1e76 <default_app_on_connection>
   0x07fc2cac <+10>:	ldr	r1, [pc, #56]	; (0x7fc2ce8)
   0x07fc2cae <+12>:	ldrh	r0, [r4, #0]
   0x07fc2cb0 <+14>:	strh	r0, [r1, #2]
   0x07fc2cb2 <+16>:	ldrh	r0, [r4, #2]
   0x07fc2cb4 <+18>:	strh	r0, [r1, #4]
   0x07fc2cb6 <+20>:	ldrh	r0, [r4, #4]
   0x07fc2cb8 <+22>:	strh	r0, [r1, #6]
   0x07fc2cba <+24>:	ldrh	r0, [r4, #6]
   0x07fc2cbc <+26>:	strh	r0, [r1, #8]
   0x07fc2cbe <+28>:	ldr	r1, [r1, #12]
   0x07fc2cc0 <+30>:	mov	r0, r5
   0x07fc2cc2 <+32>:	blx	r1
   0x07fc2cc4 <+34>:	pop	{r4, r5, r6, pc}
```

10.  Looking at the LR-1 we can see that return address was on 0x07fc2cc4:

```
pop	{r4, r5, r6, pc}
```

This means that the following line of code is where the null pointer was passed:

```
blx	r1
```

11. Let's figure out why r1 is null and what we are trying to link perform a branch instruction on. Looking at the disassembly, we see two instructions that affect r1:

```
ldr	r1, [pc, #56]	; (0x7fc2ce8)
....
ldr	r1, [r1, #12]
```

The first instruction is what is referred to as PC relative addressing.  This takes the relative PC value (next instruction + 8) and adds 56 to it.  It takes the address at this location and loads it into R1.  

The second instruction then takes the value in R1, adds 12 and stores it back into R1. 

12. We are adding 12, to 0x7fc8e70, we can use a 'convenience variable' to store this for later:

```
(gdb)set $bad_ptr_address = 0x7fc8e70 + 12
```

13.  Let's take a look to see what the first instruction is loading:

```
(gdb)x /1a 0x7fc2ce8
```
This appears to be a variable:

```
0x7fc2ce8:	0x7fc8e70 <user_app_env>
```

14.  Let's inpsect this variable:

```
(gdb)p user_app_env
```

We should see the following:

```
(gdb) p user_app_env
$1 = {
  con_id = 0 '\000', 
  conhdl = 0, 
  con_intvl = 7, 
  con_latency = 0, 
  con_sup_to = 10, 
  con_cb = 0x0
}
```

15.  This seems reasonable, the second instruction we add 12 to the first address and pass this value into the pc.  So let's make sure we are referencing this variable by checking the size of the variable:

```
(gdb)print sizeof(user_app_env)
```

We should see a value of 16, so this tells us that we are, in fact, passing one of these variables into the pc.


16. To gain further insight into this variable let's inspect the type:

```
(gdb) ptype user_app_env
```

Which produces the following output:

```
type = struct {
    uint8_t con_id;
    uint16_t conhdl;
    uint16_t con_intvl;
    uint16_t con_latency;
    uint16_t con_sup_to;
    my_connection_cb_t con_cb;
}
```

17.  con_cb seems to a function callback, which could potentially point to a null pointer, let's inspect this type and value:

```
(gdb)ptype user_app_env.con_cb
```

Which produces the following output:

```
type = void (*)(uint8_t)
```

This type is a function pointer, and from above we see that it is a null variable.  This is looking like the culprit, but let's verify.

18.  Let's inspect the address of the callback first, and print the address we saved off previously:

```
(gdb) p /x &user_app_env.con_cb
(gdb) p /x $bad_ptr_address
```

The output provides confirmation that the PC is trying to load 
the address pointed to by user_app_env.con_cb, which is a null
pointer.
