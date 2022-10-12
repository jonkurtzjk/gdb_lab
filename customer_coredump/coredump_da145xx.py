import datetime
from enum import IntEnum, Enum
from ezFlashCLI.ezFlash.pyjlink import pyjlink
import ctypes as ct

MEMORY_START_531 = 0x7FC0000
MEMORY_END_531 = 0x7FCBFFF

MEMORY_START_585 = 0x7FC0000
MEMORY_END_585 = 0x7FD7FFF

COREDUMP_HDR_VER = 1
COREDUMP_TGT_ARM_CORTEX_M = 3
COREDUMP_HDR_ID = 'ZE'
COREDUMP_ARCH_HDR_ID = 'A'
COREDUMP_MEM_HDR_ID = 'M'

DA14531_CHIP_ID = '2632'
DA14585_CHIP_ID = '585'


class RegNum(IntEnum):
    R0 = 0
    R1 = 1
    R2 = 2
    R3 = 3
    R4 = 4
    R5 = 5
    R6 = 6
    R7 = 7
    R8 = 8
    R9 = 9
    R10 = 10
    R11 = 11
    R12 = 12
    SP = 13
    LR = 14
    PC = 15
    XPSR = 16
    MSP = 17
    PSP = 18


class ArchRegNum(IntEnum):
    R0 = 0
    R1 = 1
    R2 = 2
    R3 = 3
    R12 = 12
    LR = 14
    PC = 15
    XPSR = 16
    SP = 13


class CoreDumpHeader(Enum):
    id0 = ord('Z')
    id1 = ord('E')
    hdr_version = COREDUMP_HDR_VER
    tgt_code = COREDUMP_TGT_ARM_CORTEX_M
    ptr_size_bits = 5
    flag = 0
    reason = 1


class CoreArchHeader(Enum):
    id = ord(COREDUMP_ARCH_HDR_ID)
    hdr_version = COREDUMP_HDR_VER
    num_bytes = len(RegNum) * 4


class CoreMemHeader(Enum):
    id = ord(COREDUMP_MEM_HDR_ID)
    hdr_version = COREDUMP_HDR_VER
    mem_start = MEMORY_START_531
    mem_end = MEMORY_END_531


def display_reg_values(reg_vals):
    for val in reg_vals:
        print(f'{val[0]}: {hex(val[1])}')


def get_register_values(jlink):
    regs = []
    for r in RegNum:
        val = jlink.jl.JLINKARM_ReadReg(ct.c_int32(r))
        if val < 0:
            val = val + (1 << 32)
        regs.append([r.name, val])

    return regs


def get_ram_dump(jlink, start_addr, end_addr):
    return jlink.rd_mem(8, start_addr, end_addr - start_addr)


def write_header(b_file):
    b_file.write(CoreDumpHeader.id0.value.to_bytes(1, 'little'))
    b_file.write(CoreDumpHeader.id1.value.to_bytes(1, 'little'))
    b_file.write(CoreDumpHeader.hdr_version.value.to_bytes(2, 'little'))
    b_file.write(CoreDumpHeader.tgt_code.value.to_bytes(2, 'little'))
    b_file.write(CoreDumpHeader.ptr_size_bits.value.to_bytes(1, 'little'))
    b_file.write(CoreDumpHeader.flag.value.to_bytes(1, 'little'))
    b_file.write(CoreDumpHeader.reason.value.to_bytes(4, 'little'))


def write_arch_header(b_file):
    b_file.write(CoreArchHeader.id.value.to_bytes(1, 'little'))
    b_file.write(CoreArchHeader.hdr_version.value.to_bytes(2, 'little'))
    b_file.write(CoreArchHeader.num_bytes.value.to_bytes(2, 'little'))


def write_mem_header(b_file, mem_start, mem_end):
    b_file.write(CoreMemHeader.id.value.to_bytes(1, 'little'))
    b_file.write(CoreMemHeader.hdr_version.value.to_bytes(2, 'little'))
    b_file.write(mem_start.to_bytes(4, 'little'))
    b_file.write(mem_end.to_bytes(4, 'little'))


def create_core_file(all_regs, memory_dump, mem_start, mem_end):
    time = datetime.datetime.now()
    file_name = f'coredump_{time.month}_{time.day}_{time.year}_{time.time().hour}_{time.time().minute}.bin'
    file = open(file_name, 'wb')

    write_header(file)
    write_arch_header(file)

    for r in all_regs:
        file.write(r[1].to_bytes(4, 'little'))

    write_mem_header(file, mem_start, mem_end)

    for x in memory_dump:
        file.write(x.to_bytes(1, 'little'))

    print('Created Core File: ' + file_name)

    file.close()


def jtag_connect_and_halt_device():
    dev = []
    i = 0
    id_chars = 4

    link = pyjlink()
    link.init()
    raw_device_list = link.browse()

    devicelist = []
    for device in raw_device_list:
        if device.SerialNumber != 0:
            devicelist.append(device)

    devicelist.sort()

    print("JLink devices:")
    for device in devicelist:
        if device.SerialNumber != 0:
            print(f'\t{device.SerialNumber}')

    print(f'\r\nUsing JLink Serial Number:{devicelist[0].SerialNumber}')

    link.connect(devicelist[0].SerialNumber)
    first_char = chr(link.rd_mem(8, 0x50003200, 1)[0])
    if first_char == DA14531_CHIP_ID[0]:
        multiplier = 4
        id_chars = 4
    elif first_char == DA14585_CHIP_ID[0]:
        multiplier = 1
        id_chars = 3
    else:
        raise Exception("Device Detected not DA14531 or DA14585")

    dev_id = ''
    while i < id_chars:
        dev_id += (chr(link.rd_mem(8, 0x50003200 + i * multiplier, 1)[0]))
        i += 1

    if dev_id == DA14531_CHIP_ID:
        print("Device Detected DA14531\r\n")
        mem_start = MEMORY_START_531
        mem_end = MEMORY_END_531
    elif dev_id == DA14585_CHIP_ID:
        print("Device Detected DA14585\r\n")
        mem_start = MEMORY_START_585
        mem_end = MEMORY_END_585
    else:
        raise Exception("Unsupported Device Connected! Exiting....")

    link.jl.JLINKARM_Halt()

    return link, mem_start, mem_end


def jtag_dump_memory():
    jlink, mem_start, mem_end = jtag_connect_and_halt_device()

    arg_regs = get_register_values(jlink)
    display_reg_values(arg_regs)
    memory_dump = get_ram_dump(jlink, mem_start, mem_end)
    create_core_file(arg_regs, memory_dump, mem_start, mem_end)

    jlink.close()


if __name__ == '__main__':
    jtag_dump_memory()
