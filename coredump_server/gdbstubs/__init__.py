#!/usr/bin/env python3
#
# Copyright (c) 2020 Intel Corporation
#
# SPDX-License-Identifier: Apache-2.0

from gdbstubs.arch.arm_cortex_m import GdbStub_ARM_CortexM


class TgtCode:
    UNKNOWN = 0
    X86 = 1
    X86_64 = 2
    ARM_CORTEX_M = 3
    RISC_V = 4
    XTENSA = 5


def get_gdbstub(logfile, elffile):
    tgt_code = logfile.log_hdr['tgt_code']
    assert tgt_code == TgtCode.ARM_CORTEX_M
    return GdbStub_ARM_CortexM(logfile=logfile, elffile=elffile)



