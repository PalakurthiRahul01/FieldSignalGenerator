import socket
from queue import Queue

import serial
from pymavlink import mavutil
from PyQt5 import QtCore
import time

class TelemetryThread(QtCore.QThread):
    # altitudeChanged = QtCore.pyqtSignal(float)
    # batteryChanged = QtCore.pyqtSignal(float)

    def __init__(self, master, queue):
        super().__init__()
        self.master = master
        self.queue  = queue
        self.running = True

    def run(self):
        while self.running:
            try:
                msg = self.master.recv_match(blocking=False)
                if msg:
                    self.queue.put(msg)
            except Exception as e:
                print("Telemetry error:", e)
                # break
            # time.sleep(0.05)

    def stop(self):
        self.running = False

class PL_Serial_Handler(QtCore.QObject):
    def __init__(self):
        super(PL_Serial_Handler, self).__init__()
        self.inst = None
        self.ErrorFlag = False
        self.ErrorMsg = ""

        self.msg_queue = Queue()


    ##################################################################################################################
    def OpenInstr(self, Port = 'COM1',baudrate = 9600,timeout=1):
        self.ErrorFlag = False
        self.ErrorMsg = False
        try:
            self.inst = serial.Serial(Port, baudrate=baudrate, timeout=timeout)
        except Exception as e:
            self.ErrorFlag = True
            self.ErrorMsg = e

    ##################################################################################################################
    def CloseInstr(self):
        self.ErrorFlag = False
        self.ErrorMsg = False
        try:
            self.inst.close()
        except Exception as e:
            self.ErrorFlag = True
            self.ErrorMsg = e

    ##################################################################################################################
    def InstWrite(self, cmdstr=""):
        self.ErrorFlag = False
        self.ErrorMsg = False
        try:
            cmd = cmdstr.encode('utf-8')
            self.inst.write(cmd)
            time.sleep(0.1)
        except Exception as e:
            self.ErrorFlag = True
            self.ErrorMsg = e

    ##################################################################################################################
    def InstRead(self, BytesAtPort=3):
        self.ErrorFlag = False
        self.ErrorMsg = False
        try:
            RecvData = self.inst.recv(BytesAtPort)
            print(RecvData)
            return RecvData
        except Exception as e:
            self.ErrorFlag = True
            self.ErrorMsg = e

    ##################################################################################################################
    # def CMD_to_SetFreq(self, setfreq=500):
    #     self.ErrorFlag = False
    #     self.ErrorMsg = False
    #     try:
    #         cmd = f':F{setfreq}\r'
    #         Resp = self.InstWrite(cmd)
    #         print(Resp)
    #         if self.ErrorFlag != False:
    #             print('Failed')
    #             self.ErrorFlag = True
    #             return False, f'Set SSG Freq {setfreq}'
    #         print('cmd sent')
    #     except Exception as e:
    #         self.ErrorFlag = True
    #         self.ErrorMsg = e
    def CMD_to_SetFreq(self, setfreq=500):

        self.ErrorFlag = False
        self.ErrorMsg = None

        try:
            cmd = f':F{setfreq}\r'
            self.InstWrite(cmd)
            print("Command Sent:", cmd)
            if self.ErrorFlag:
                return False, f"Failed to Set Frequency {setfreq}"
            response = self.InstRead()
            if response:
                print("Received:", response)
                # If you have QTextEdit
                if hasattr(self, "TE_Edit"):
                    self.TE_Edit.append(f"Set Frequency → {setfreq}")
                    self.TE_Edit.append(f"Instrument Reply → {response}")
                    self.TE_Edit.append("-----------------------------")
            return True, response
        except Exception as e:
            self.ErrorFlag = True
            self.ErrorMsg = e
            if hasattr(self, "TE_Edit"):
                self.TE_Edit.append(f"Error: {str(e)}")
            return False, str(e)

    ##################################################################################################################
    def CMD_to_SetAttn(self, attn=1):
        self.ErrorFlag = False
        self.ErrorMsg = False
        try:
            cmd = f':A{attn}\r'
            Resp = self.InstWrite(cmd)
            print(Resp)
            if self.ErrorFlag != False:
                print('Failed')
                self.ErrorFlag = True
                return False, f'Set Attn failed'
            print('cmd sent')
        except Exception as e:
            self.ErrorFlag = True
            self.ErrorMsg = e

    ##################################################################################################################
    def CMD_to_SetPRI(self, pri=100):
        self.ErrorFlag = False
        self.ErrorMsg = False
        try:
            cmd = f':R{pri}\r'
            Resp = self.InstWrite(cmd)
            print(Resp)
            if self.ErrorFlag != False:
                print('Failed')
                self.ErrorFlag = True
                return False, f'Set pri failed'
            print('cmd sent')
        except Exception as e:
            self.ErrorFlag = True
            self.ErrorMsg = e

    ##################################################################################################################
    def CMD_to_SetPW(self, pw=1):
        self.ErrorFlag = False
        self.ErrorMsg = False
        try:
            cmd = f':W{pw}\r'
            Resp = self.InstWrite(cmd)
            print(Resp)
            if self.ErrorFlag != False:
                print('Failed')
                self.ErrorFlag = True
                return False, f'Set pw failed'
            print('cmd sent')
        except Exception as e:
            self.ErrorFlag = True
            self.ErrorMsg = e

    ##################################################################################################################
    def CMD_to_SetLedgeDelay(self, ledge_delay=1):
        self.ErrorFlag = False
        self.ErrorMsg = False
        try:
            cmd = f':L{ledge_delay}\r'
            Resp = self.InstWrite(cmd)
            print(Resp)
            if self.ErrorFlag != False:
                print('Failed')
                self.ErrorFlag = True
                return False, f'Set ledge_delay failed'
            print('cmd sent')
        except Exception as e:
            self.ErrorFlag = True
            self.ErrorMsg = e

    ##################################################################################################################
    def CMD_to_SetTedgeDelay(self, tedge_delay=1):
        self.ErrorFlag = False
        self.ErrorMsg = False
        try:
            cmd = f':T{tedge_delay}\r'
            Resp = self.InstWrite(cmd)
            print(Resp)
            if self.ErrorFlag != False:
                print('Failed')
                self.ErrorFlag = True
                return False, f'Set tedge_delay failed'
            print('cmd sent')
        except Exception as e:
            self.ErrorFlag = True
            self.ErrorMsg = e

    ##################################################################################################################
    def CMD_to_SetModulation(self, mod=1):
        self.ErrorFlag = False
        self.ErrorMsg = False
        try:
            cmd = f':M{mod}\r'
            Resp = self.InstWrite(cmd)
            print(Resp)
            if self.ErrorFlag != False:
                print('Failed')
                self.ErrorFlag = True
                return False, f'Set mod failed'
            print('Mod_cmd sent')
        except Exception as e:
            self.ErrorFlag = True
            self.ErrorMsg = e

    ##################################################################################################################
    def CMD_to_SetStatus(self, status=0):
        self.ErrorFlag = False
        self.ErrorMsg = False
        try:
            cmd = f':O{status}\r'
            Resp = self.InstWrite(cmd)
            print(Resp)
            if self.ErrorFlag != False:
                print('Failed')
                self.ErrorFlag = True
                return False, f'Set status failed'
            print('RF_cmd sent')
        except Exception as e:
            self.ErrorFlag = True
            self.ErrorMsg = e

    ##################################################################################################################
    def CMD_to_SetServoPos(self, servo=0):
        self.ErrorFlag = False
        self.ErrorMsg = False
        try:
            cmd = f':S{servo}\r'
            Resp = self.InstWrite(cmd)
            print(Resp)
            if self.ErrorFlag != False:
                print('Failed')
                self.ErrorFlag = True
                return False, f'Set servo failed'
            print('cmd sent')
        except Exception as e:
            self.ErrorFlag = True
            self.ErrorMsg = e
    # def SetSSG(self, freq=5000, power=-40, pri=1000, pw=0.1, signal_type='PULSE'):
    #     self.ErrorFlag = False
    #     self.ErrorMsg = False
    #     CmdStr = ''
    #     if True:
    #         status= self.SetFreq(setfreq=freq)
    #         if self.ErrorFlag != False:
    #             return False
    #
    #     if True:
    #         if signal_type == 'PULSE':
    #             # if pw >= pri:
    #             #     return False, 'PW>PRI'
    #             if True:
    #                 status, msg = self.SetPRI(setpri=pri)
    #                 if not status:
    #                     return False, msg
    #                 self.SSGSetPRI = pri
    #
    #             if True:
    #                 status, msg = self.SetPW(setpw=pw)
    #                 if not status:
    #                     return False, msg
    #                 self.SSGSetPW = pw
    #
    #             status, msg = self.SetModulation(status='ON')
    #             if not status:
    #                 return False, msg
    #             status, msg = self.SetStat(status='ON')
    #             if not status:
    #                 return False, msg
    #
    #         else:
    #             status, msg = self.SetModulation(status='OFF')
    #             if not status:
    #                 return False, msg
    #             status, msg = self.SetStat(status='OFF')
    #             if not status:
    #                 return False, msg
    #         self.SSGSetSigType = signal_type
    #
    #     # if CmdStr != '':
    #     #     Resp = self.InstWrite(CmdStr)
    #     #     if Resp['errorcode'] != NOERROR:
    #     #         return False, Resp
    #     #
    #     #     Status, Resp = self.ReadStatusByte()
    #     #     print('Status Byte = ', Resp)
    #     #     if Status == False:
    #     #         return False, Resp
    #     #     else:
    #     #         if Resp['ReadData'] != b'+0,"No error"\n':
    #     #             return False, {'errorcode': SSG_STATUS_REG_ERROR, 'id': 'SSG', 'errmsg': 'Send Error', 'ExceptionMsg': f'SSGWrite- ERROR IN SSG Parameters - Freq = {freq}, Modulation-{signal_type}, PW-{pw}, PRI-{pri}'}
    #
    #     return True, 'No Error'
        ##################################################################################################################
    def SetSSG(self, freq=500, pri=100, pw=1, attn=1, ledge_delay=1, tedge_delay=1, mod=1, rf_status=0):
        self.ErrorFlag = False
        self.ErrorMsg = False
        try:
            if True:
                status = self.CMD_to_SetFreq(setfreq=freq)
                time.sleep(1)
                # print(status)
                # if self.ErrorFlag == True:
                #     return False, self.ErrorMsg
                # self.SSGSetFreq = freq

            if True:
                status = self.CMD_to_SetAttn(attn=attn)
                time.sleep(1)
#                 print(status)
#                 if self.ErrorFlag == True:
#                     return False, self.ErrorMsg
#                 self.SSGSetPower = attn

            if True:
                # if signal_type == 'PULSE':
                    # if pw >= pri:
                    #     return False, 'PW>PRI'
                    if True:
                        status = self.CMD_to_SetPRI(pri=pri)
                        time.sleep(1)
#                         print(status)
#                         if self.ErrorFlag == True:
#                             return False, self.ErrorMsg
#                         self.SSGSetPRI = pri

                    if True:
                        status = self.CMD_to_SetPW(pw=pw)
                        time.sleep(1)
#                         print(status)
#                         if self.ErrorFlag == True:
#                             return False, self.ErrorMsg
#                         self.SSGSetPW = pw

                    status = self.CMD_to_SetModulation(mod=mod)
                    time.sleep(1)
#                     if self.ErrorFlag == True:
#                         return False, self.ErrorMsg
                    status = self.CMD_to_SetStatus(status=rf_status)
                    # time.sleep(1)
                    #                     if self.ErrorFlag == True:
                    #                         return False, self.ErrorMsg

#                     status = self.CMD_to_SetLedgeDelay(ledge_delay=ledge_delay)
# #                     if self.ErrorFlag == True:
# #                         return False, self.ErrorMsg
#
#                     status = self.CMD_to_SetTedgeDelay(tedge_delay=tedge_delay)
#                     if self.ErrorFlag == True:
#                         return False, self.ErrorMsg


        except Exception as e:
            self.ErrorFlag = True
            self.ErrorMsg = e

            # else:
            #     pass
                # status, msg = self.SetModulation(status='OFF')
                # print(status, msg)
                # if not status:
                #     return False, msg
                # status, msg = self.SetStat(status='OFF')
                # print(status, msg)
                # if not status:
                #     return False, msg
            # self.SSGSetSigType = signal_type

        # if CmdStr != '':
        #     Resp = self.InstWrite(CmdStr)
        #     if Resp['errorcode'] != NOERROR:
        #         return False, Resp
        #
        #     Status, Resp = self.ReadStatusByte()
        #     print('Status Byte = ', Resp)
        #     if Status == False:
        #         return False, Resp
        #     else:
        #         if Resp['ReadData'] != b'+0,"No error"\n':
        #             return False, {'errorcode': SSG_STATUS_REG_ERROR, 'id': 'SSG', 'errmsg': 'Send Error', 'ExceptionMsg': f'SSGWrite- ERROR IN SSG Parameters - Freq = {freq}, Modulation-{signal_type}, PW-{pw}, PRI-{pri}'}

        # return True, 'No Error'

if __name__ == "__main__":
    import sys
    app = QtCore.QCoreApplication(sys.argv)

    handler = PL_Serial_Handler()
    handler.OpenInstr(Port='COM3', baudrate=115200)
    if handler.inst:
        handler.CMD_to_SetFreq(setfreq=6000)
        # handler.CMD_to_SetAttn(attn=1)
        # handler.CMD_to_SetPRI(pri=100)
        # handler.CMD_to_SetPW(pw=1)
        # handler.CMD_to_SetModulation(mod=1)

        handler.CloseInstr()


