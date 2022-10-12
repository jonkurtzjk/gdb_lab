#!/usr/bin/env python3
#
# Copyright (c) 2020 Intel Corporation
#
# SPDX-License-Identifier: Apache-2.0

import binascii
import logging
import struct
import socket

from gdbstubs.gdbstub import GdbStub

logger = logging.getLogger("gdbstub")


class RegNum():
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
    NUM_REGISTERS = 19


class GdbStub_ARM_CortexM(GdbStub):
    ARCH_DATA_BLK_STRUCT = "<IIIIIIIIIIIIIIIIIII"

    GDB_SIGNAL_DEFAULT = 7

    GDB_G_PKT_NUM_REGS = RegNum.NUM_REGISTERS

    def __init__(self, logfile, elffile):
        super().__init__(logfile=logfile, elffile=elffile)
        self.registers = None
        self.gdb_signal = self.GDB_SIGNAL_DEFAULT

        self.parse_arch_data_block()

    def parse_arch_data_block(self):
        arch_data_blk = self.logfile.get_arch_data()['data']
        tu = struct.unpack(self.ARCH_DATA_BLK_STRUCT, arch_data_blk)

        self.registers = dict()

        self.registers[RegNum.R0] = tu[0]
        self.registers[RegNum.R1] = tu[1]
        self.registers[RegNum.R2] = tu[2]
        self.registers[RegNum.R3] = tu[3]
        self.registers[RegNum.R4] = tu[4]
        self.registers[RegNum.R5] = tu[5]
        self.registers[RegNum.R6] = tu[6]
        self.registers[RegNum.R7] = tu[7]
        self.registers[RegNum.R8] = tu[8]
        self.registers[RegNum.R9] = tu[9]
        self.registers[RegNum.R10] = tu[10]
        self.registers[RegNum.R11] = tu[11]
        self.registers[RegNum.R12] = tu[12]
        self.registers[RegNum.SP] = tu[13]  # +32 # + 4
        self.registers[RegNum.LR] = tu[14]
        self.registers[RegNum.PC] = tu[15]
        self.registers[RegNum.XPSR] = tu[16]
        self.registers[RegNum.MSP] = tu[17]  # +32 # + 4
        self.registers[RegNum.PSP] = tu[18]  # +32 # + 4
        # TODO: Figure out why we need an offset of 4 sometimes and 32 othertimes? Something with MSP and PSP?

        # self.registers[RegNum.MSP] = tu[6]

    def handle_register_group_read_packet(self):
        reg_fmt = "<I"

        idx = 0
        pkt = b''

        while idx < self.GDB_G_PKT_NUM_REGS:
            if idx in self.registers:
                bval = struct.pack(reg_fmt, self.registers[idx])
                pkt += binascii.hexlify(bval)
            else:
                # Register not in coredump -> unknown value
                # Send in "xxxxxxxx"
                pkt += b'x' * 8
            idx += 1

        self.put_gdb_packet(pkt)

    def handle_register_single_read_packet(self, pkt):
        # Mark registers as "<unavailable>".
        # 'p' packets are usually used for registers
        # other than the general ones (e.g. eax, ebx)
        # so we can safely reply "xxxxxxxx" here.
        ret = b''
        if pkt == b'p19':
            reg_fmt = "<I"
            bval = struct.pack(reg_fmt, self.registers[16])
            ret += binascii.hexlify(bval)
            self.put_gdb_packet(ret)
        else:
            self.put_gdb_packet(b'x' * 8)
        # reg_fmt = "<I"
        # bval = struct.pack(reg_fmt, self.registers[16])
        # pkt += binascii.hexlify(bval)
        # self.put_gdb_packet(pkt)

    def handle_register_single_write_packet(self, pkt):
        ascii_to_int = {
            '0': 0,
            '1': 1,
            '2': 2,
            '3': 3,
            '4': 4,
            '5': 5,
            '6': 6,
            '7': 7,
            '8': 8,
            '9': 9,
            'a': 10,
            'b': 11,
            'c': 12,
            'd': 13,
            'e': 14,
            'f': 15,
        }
        if len(pkt) == 12:
            reg = 16
            value = 0
            for i in range(8):
                value = (value << 4) + ascii_to_int[chr(pkt[4 + i])]
        else:
            assert len(pkt) == 11
            reg = ascii_to_int[chr(pkt[1])]
            value = 0
            for i in range(8):
                value = (value << 4) + ascii_to_int[chr(pkt[3 + i])]
        self.registers[reg] = socket.htonl(value)
        self.put_gdb_packet(bytes('OK', 'utf-8'))
