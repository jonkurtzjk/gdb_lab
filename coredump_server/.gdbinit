set history filename ~/.gdb_history
set history size unlimited
set history save on

set print pretty on
file ../files/lab.axf
target remote localhost:1234

define xxd
  dump binary memory /tmp/dump.bin $arg0 ((char *)$arg0)+$arg1
  shell xxd /tmp/dump.bin
end
document xxd
  Runs xxd on a memory ADDR and LENGTH

  xxd ADDR LENTH
end
