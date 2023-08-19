##
## This file is part of the libsigrokdecode project.
##
## Copyright (C) 2023 Mario Smit <sourceror@neximus.com>
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, see <http://www.gnu.org/licenses/>.
##

import sigrokdecode as srd
from collections import namedtuple

class Decoder(srd.Decoder):
    api_version = 3
    id = 'zdi'
    name = 'ZDI'
    longname = 'Zilog Debug Interface'
    desc = 'ZDI debugging EZ80 processors'
    license = 'gplv2+'
    inputs = ['logic']
    outputs = ['spi']
    tags = ['Embedded/industrial']
    channels = (
        {'id': 'zda', 'name': 'ZDA', 'desc': 'Data'},
        {'id': 'zcl', 'name': 'ZCL', 'desc': 'Clock'},
    )
    options = (
    )
    annotations = (
        ('start', 'START'),
        ('bit', 'Bit'),
        ('separator', 'Separator bit'),
        ('rw', 'RW bit'),
        ('register', 'Register'),
        ('value', 'Value'),
        ('action','Action'),
    )
    annotation_rows = (
        ('bits', 'Bits', (0,1,2,3)),
        ('command', 'Command', (4,5)),
        ('action', 'Action', (6,)),
    )
    binary = (
    )

    def __init__(self):
        self.reset()

    def start(self):
        self.out_ann = self.register(srd.OUTPUT_ANN)

    def reset(self):
         #reset inner states 
         reset = True

    def metadata(self, key, value):
       if key == srd.SRD_CONF_SAMPLERATE:
            self.samplerate = value

    def decode(self):
        state_regwr_value = 0
        state_read = False
        state_reg = 0
        while True:
            # wait for start bit
            (zda,zcl) = self.wait([{0:'f',1:'h'}])#,{'skip':10,1:'f'}])
            state_start_command = self.samplenum
            if self.matched[0]:
                self.put (self.samplenum,self.samplenum+1,self.out_ann,[0,['START','S']])
                # get register bits
                state_reg = 0
                state_start_reg_sample = self.samplenum
                for b in range (0,7):
                    (zda,zcl) = self.wait([{1:'r'}])
                    self.put (self.samplenum,self.samplenum+1,self.out_ann,[1,[str(zda)]])
                    state_reg = state_reg << 1
                    state_reg = state_reg + zda
                # wait for R/W bit
                (zda,zcl) = self.wait([{1:'r'}])
                self.put (state_start_reg_sample,self.samplenum,self.out_ann,[4,[hex(state_reg)]])
                state_read = False
                if zda==1:
                    state_read = True
                    self.put (self.samplenum,self.samplenum+1,self.out_ann,[3,['R']])
                else:
                    self.put (self.samplenum,self.samplenum+1,self.out_ann,[3,['W']])
                # wait for separator
                (zda,zcl) = self.wait([{1:'r'}])
                self.put (self.samplenum,self.samplenum+1,self.out_ann,[2,[str(zda)]])
            # get value bits
            state_val = 0
            state_start_val_sample = self.samplenum+1
            for b in range (0,8):
                if state_read:
                    (zda,zcl) = self.wait([{1:'f'}])
                    (zda,zcl) = self.wait([{'skip':1}])
                    self.put (self.samplenum-1,self.samplenum,self.out_ann,[1,[str(zda)]])
                else:
                    (zda,zcl) = self.wait([{1:'r'}])
                    self.put (self.samplenum,self.samplenum+1,self.out_ann,[1,[str(zda)]])
                state_val = state_val << 1
                state_val = state_val + zda
            # wait for separator
            (zda,zcl) = self.wait([{1:'r'}])
            self.put (state_start_val_sample,self.samplenum,self.out_ann,[5,[hex(state_val)]])
            self.put (self.samplenum,self.samplenum+1,self.out_ann,[2,[str(zda)]])
            # show result of operation
            if state_read==False:
                #######################################
                # WRITE OPERATIONS
                #
                if state_reg==0x00:
                    self.put (state_start_command,self.samplenum,self.out_ann,[6,["ZDI_ADDR0_L="+hex(state_val),hex(state_val)]])
                if state_reg==0x01:
                    self.put (state_start_command,self.samplenum,self.out_ann,[6,["ZDI_ADDR0_H="+hex(state_val),hex(state_val)]])
                if state_reg==0x02:
                    self.put (state_start_command,self.samplenum,self.out_ann,[6,["ZDI_ADDR0_U="+hex(state_val),hex(state_val)]])
                if state_reg==0x04:
                    self.put (state_start_command,self.samplenum,self.out_ann,[6,["ZDI_ADDR1_L="+hex(state_val),hex(state_val)]])
                if state_reg==0x05:
                    self.put (state_start_command,self.samplenum,self.out_ann,[6,["ZDI_ADDR1_H="+hex(state_val),hex(state_val)]])
                if state_reg==0x06:
                    self.put (state_start_command,self.samplenum,self.out_ann,[6,["ZDI_ADDR1_U="+hex(state_val),hex(state_val)]])
                if state_reg==0x08:
                    self.put (state_start_command,self.samplenum,self.out_ann,[6,["ZDI_ADDR2_L="+hex(state_val),hex(state_val)]])
                if state_reg==0x09:
                    self.put (state_start_command,self.samplenum,self.out_ann,[6,["ZDI_ADDR2_H="+hex(state_val),hex(state_val)]])
                if state_reg==0x0a:
                    self.put (state_start_command,self.samplenum,self.out_ann,[6,["ZDI_ADDR2_U="+hex(state_val),hex(state_val)]])
                if state_reg==0x0c:
                    self.put (state_start_command,self.samplenum,self.out_ann,[6,["ZDI_ADDR3_L="+hex(state_val),hex(state_val)]])
                if state_reg==0x0d:
                    self.put (state_start_command,self.samplenum,self.out_ann,[6,["ZDI_ADDR3_H="+hex(state_val),hex(state_val)]])
                if state_reg==0x0e:
                    self.put (state_start_command,self.samplenum,self.out_ann,[6,["ZDI_ADDR3_U="+hex(state_val),hex(state_val)]])
                if state_reg==0x10:
                    break_flags = ""
                    if state_val & 0b1000_0000:
                        break_flags = break_flags + "BN"
                    if state_val & 0b0100_0000:
                        break_flags = break_flags + "B3"
                    if state_val & 0b0010_0000:
                        break_flags = break_flags + "B2"
                    if state_val & 0b0001_0000:
                        break_flags = break_flags + "B1"
                    if state_val & 0b0000_1000:
                        break_flags = break_flags + "B0"
                    if state_val & 0b0000_0100:
                        break_flags = break_flags + "I1"
                    if state_val & 0b0000_0010:
                        break_flags = break_flags + "I0"
                    if state_val & 0b0000_0001:
                        break_flags = break_flags + "S"
                    self.put (state_start_command,self.samplenum,self.out_ann,[6,["ZDI_BRK_CTL="+break_flags,break_flags]])            
                if state_reg==0x13:
                    # write ZDI_WR_L
                    state_regwr_value = state_regwr_value & 0xffff00
                    state_regwr_value = state_regwr_value | state_val
                    self.put (state_start_command,self.samplenum,self.out_ann,[6,["ZDI_WR_L="+hex(state_val),hex(state_val)]])
                if state_reg==0x14:
                    # write ZDI_WR_H
                    state_regwr_value = state_regwr_value & 0xff00ff
                    state_regwr_value = state_regwr_value | (state_val&0xff)<<8
                    self.put (state_start_command,self.samplenum,self.out_ann,[6,["ZDI_WR_H="+hex(state_val),hex(state_val)]])
                if state_reg==0x15:
                    # write ZDI_WR_U
                    state_regwr_value = state_regwr_value & 0x00ffff
                    state_regwr_value = state_regwr_value | (state_val&0xff)<<16
                    self.put (state_start_command,self.samplenum,self.out_ann,[6,["ZDI_WR_U="+hex(state_val),hex(state_val)]])  
                if state_reg==0x16:
                    state_read_reg = state_val
                    if state_val == 0:
                        rw_ctl = "Read {MBASE, A, F}"
                    if state_val == 1:
                        rw_ctl = "Read BC"
                    if state_val == 2:
                        rw_ctl = "Read DE"
                    if state_val == 3:
                        rw_ctl = "Read HL"
                    if state_val == 4:
                        rw_ctl = "Read IX"
                    if state_val == 5:
                        rw_ctl = "Read IY"
                    if state_val == 6:
                        rw_ctl = "Read SP"
                    if state_val == 7:
                        rw_ctl = "Read PC"
                    if state_val == 8:
                        rw_ctl = "Set ADL"
                    if state_val == 9:
                        rw_ctl = "Reset ADL"
                    if state_val == 0x80:
                        rw_ctl = "Write {MBASE, A, F}="+hex(state_regwr_value)
                    if state_val == 0x81:
                        rw_ctl = "Write BC="+hex(state_regwr_value)
                    if state_val == 0x82:
                        rw_ctl = "Write DE="+hex(state_regwr_value)
                    if state_val == 0x83:
                        rw_ctl = "Write HL="+hex(state_regwr_value)
                    if state_val == 0x84:
                        rw_ctl = "Write IX="+hex(state_regwr_value)
                    if state_val == 0x85:
                        rw_ctl = "Write IY="+hex(state_regwr_value)
                    if state_val == 0x86:
                        rw_ctl = "Write SP="+hex(state_regwr_value)
                    if state_val == 0x87:
                        rw_ctl = "Write PC="+hex(state_regwr_value)
                    self.put (state_start_command,self.samplenum,self.out_ann,[6,["ZDI_RW_CTL:"+rw_ctl,rw_ctl]])                          
                if state_reg==0x21:
                    # ZDI_IS4
                    self.put (state_start_command,self.samplenum,self.out_ann,[6,["ZDI_IS4="+hex(state_val),hex(state_val)]])
                if state_reg==0x22:
                    # ZDI_IS3
                    self.put (state_start_command,self.samplenum,self.out_ann,[6,["ZDI_IS3="+hex(state_val),hex(state_val)]])
                if state_reg==0x23:
                    # ZDI_IS2
                    self.put (state_start_command,self.samplenum,self.out_ann,[6,["ZDI_IS2="+hex(state_val),hex(state_val)]])
                if state_reg==0x24:
                    # ZDI_IS1
                    self.put (state_start_command,self.samplenum,self.out_ann,[6,["ZDI_IS1="+hex(state_val),hex(state_val)]])
                if state_reg==0x25:
                    # ZDI_IS0
                    self.put (state_start_command,self.samplenum,self.out_ann,[6,["ZDI_IS0="+hex(state_val),hex(state_val)]])
            else:
                # READ OPERATIONS
                #
                if state_reg==0x03:
                    state_flags = ""
                    if state_val & 0b10000000:
                        state_flags = state_flags + "Z"
                    else:
                        state_flags = state_flags + "z"
                    if state_val & 0b00100000:
                        state_flags = state_flags + "H"
                    else:
                        state_flags = state_flags + "h"
                    if state_val & 0b00010000:
                        state_flags = state_flags + "A"
                    else:
                        state_flags = state_flags + "a"
                    if state_val & 0b00001000:
                        state_flags = state_flags + "M"
                    else:
                        state_flags = state_flags + "m"
                    if state_val & 0b00000100:
                        state_flags = state_flags + "I"
                    else:
                        state_flags = state_flags + "i"
                    self.put (state_start_command,self.samplenum,self.out_ann,[6,["ZDI_STAT="+state_flags,state_flags]]) 
                if state_reg==0x10:
                    # read ZDI_RD_L
                    if state_read_reg==0:
                        state_reg_A = state_val
                    if state_read_reg==1:
                        state_reg_C = state_val
                    if state_read_reg==2:
                        state_reg_E = state_val
                    if state_read_reg==3:
                        state_reg_L = state_val
                    if state_read_reg==4:
                        state_reg_IXl = state_val
                    if state_read_reg==5:
                        state_reg_IYl = state_val
                    if state_read_reg==6:
                        state_reg_SPl = state_val
                    if state_read_reg==7:
                        state_reg_PCl = state_val
                    self.put (state_start_command,self.samplenum,self.out_ann,[6,["ZDI_RD_L="+hex(state_val),hex(state_val)]])
                if state_reg==0x11:
                    # read ZDI_RD_H
                    if state_read_reg==0:
                        state_reg_F = state_val
                    if state_read_reg==1:
                        state_reg_B = state_val
                    if state_read_reg==2:
                        state_reg_D = state_val
                    if state_read_reg==3:
                        state_reg_H = state_val
                    if state_read_reg==4:
                        state_reg_IXh = state_val
                    if state_read_reg==5:
                        state_reg_IYh = state_val
                    if state_read_reg==6:
                        state_reg_SPh = state_val
                    if state_read_reg==7:
                        state_reg_PCh = state_val
                    self.put (state_start_command,self.samplenum,self.out_ann,[6,["ZDI_RD_H="+hex(state_val),hex(state_val)]])
                if state_reg==0x12:
                    # read ZDI_RD_U
                    if state_read_reg==0:
                        state_reg_MBASE = state_val
                    if state_read_reg==1:
                        state_reg_BCU = state_val
                    if state_read_reg==2:
                        state_reg_DEU = state_val
                    if state_read_reg==3:
                        state_reg_HLU = state_val
                    if state_read_reg==4:
                        state_reg_IXU = state_val
                    if state_read_reg==5:
                        state_reg_IYU = state_val
                    if state_read_reg==6:
                        state_reg_SPU = state_val
                    if state_read_reg==7:
                        state_reg_PCU = state_val
                    self.put (state_start_command,self.samplenum,self.out_ann,[6,["ZDI_RD_U="+hex(state_val),hex(state_val)]])
                if state_reg==0x20:
                    # ZDI_RD_MEM
                    self.put (state_start_command,self.samplenum,self.out_ann,[6,["ZDI_RD_MEM="+hex(state_val),hex(state_val)]])
                