import math
import queue
import random
import sys
import time
from queue import Queue

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication
from pymavlink import mavutil

from PayloadPanel.Payload.Driver.PL_Serial_Handler import PL_Serial_Handler


class PL_MiddlewareThread(QThread):
    mode_status = pyqtSignal(dict)

    def __init__(self):
        super().__init__()

        self.msg_queue = None
        self.running = True

        self.ErrorFlag = False
        self.ErrorMsg = False

        self.PLSerialHandler = PL_Serial_Handler()
    def LMXConnect(self, COM_Port='COM13', Baud=115200):
        try:
            self.PLSerialHandler.OpenInstr(Port=COM_Port, baudrate=int(Baud), timeout=1)
            if self.PLSerialHandler.ErrorFlag == True:
                return False
            else:
                return True
        except Exception as e:
            return False
    def LMXClose(self):
        self.PLSerialHandler.CloseInstr()
    def SetFreq(self, freq):
        self.ErrorFlag = False
        self.ErrorMsg = False
        try:
            self.PLSerialHandler.CMD_to_SetFreq(setfreq=freq)
            if self.PLSerialHandler.ErrorFlag == True:
                self.ErrorFlag = True
            else:
                self.ErrorFlag = False
        except Exception as e:
            self.ErrorFlag = True
            self.ErrorMsg = e
    def SetPRI(self, pri):
        self.ErrorFlag = False
        self.ErrorMsg = False
        try:
            self.PLSerialHandler.CMD_to_SetPRI(pri=pri)
            if self.PLSerialHandler.ErrorFlag == True:
                self.ErrorFlag = True
            else:
                self.ErrorFlag = False
        except Exception as e:
            self.ErrorFlag = True
            self.ErrorMsg = e
    def SetPW(self, pw):
        self.ErrorFlag = False
        self.ErrorMsg = False
        try:
            self.PLSerialHandler.CMD_to_SetPW(pw=pw)
            if self.PLSerialHandler.ErrorFlag == True:
                self.ErrorFlag = True
            else:
                self.ErrorFlag = False
        except Exception as e:
            self.ErrorFlag = True
            self.ErrorMsg = e
    def SetAttn(self, attn):
        self.ErrorFlag = False
        self.ErrorMsg = False
        try:
            self.PLSerialHandler.CMD_to_SetAttn(attn=attn)
            if self.PLSerialHandler.ErrorFlag == True:
                self.ErrorFlag = True
            else:
                self.ErrorFlag = False
        except Exception as e:
            self.ErrorFlag = True
            self.ErrorMsg = e
    def SetModulation(self, mod):
        self.ErrorFlag = False
        self.ErrorMsg = False
        try:
            self.PLSerialHandler.CMD_to_SetModulation(mod=mod)
            if self.PLSerialHandler.ErrorFlag == True:
                self.ErrorFlag = True
            else:
                self.ErrorFlag = False
        except Exception as e:
            self.ErrorFlag = True
            self.ErrorMsg = e

    def SetStatus(self, status):
        self.ErrorFlag = False
        self.ErrorMsg = False
        try:
            self.PLSerialHandler.CMD_to_SetStatus(status=status)
            if self.PLSerialHandler.ErrorFlag == True:
                self.ErrorFlag = True
            else:
                self.ErrorFlag = False
        except Exception as e:
            self.ErrorFlag = True
            self.ErrorMsg = e

    def run(self):
        while self.running:
            try:
                msg = self.msg_queue.get()
            except queue.Empty:
                continue
            except Exception as e:
                print("Queue error:", e)
                continue

            msg_type = msg.get_type()

            Available_modes = self.SerialHandler.master.mode_mapping()
            ARDUPILOT_MODES = {v: k for k, v in Available_modes.items()}

            if msg_type == "STATUSTEXT":
                severity = msg.severity
                text = msg.text
                # print(f"⚠️ STATUSTEXT [{severity}]: {text}")
                self.failsafe_message.emit({'message':f"{text}"})
            if msg_type == "GLOBAL_POSITION_INT":
                lat = msg.lat / 1e7
                lon = msg.lon / 1e7
                alt = msg.relative_alt / 1000.0
                heading = msg.hdg / 100.0 if hasattr(msg, 'hdg') and msg.hdg != 65535 else 0

                self.position_updated.emit({
                    'lat': lat,
                    'lon': lon,
                    'alt': alt,
                    'heading': heading,
                    'callsign': 'N12345'
                })

            if msg_type == "BATTERY_STATUS":
                voltage = msg.voltages[0] / 1000.0 if msg.voltages[0] != 0xFFFF else 0
                battery_percent = msg.battery_remaining
                self.battery_info.emit({
                    'voltage': voltage,
                    'percent': battery_percent
                })

            if msg_type == "GPS_RAW_INT":
                fix_type = msg.fix_type
                satellites = msg.satellites_visible
                self.gps_info.emit({
                    'fix': fix_type,
                    'satellites': satellites
                })
            if msg_type == 'MISSION_ACK':
                print(msg)
            if (msg_type == "HEARTBEAT" and
                    msg.get_srcSystem() == self.SerialHandler.master.target_system and
                    msg.get_srcComponent() == mavutil.mavlink.MAV_COMP_ID_AUTOPILOT1):

                armed = (msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED) != 0
                custom_mode = msg.custom_mode
                mode_str = ARDUPILOT_MODES.get(custom_mode, f"Unknown({custom_mode})")
                if armed != self.last_armed:
                    self.last_armed = armed
                if custom_mode != self.last_mode:
                    self.last_mode = custom_mode
                # print(f"🛡️ Armed: {'Yes' if armed else 'No'}, Mode: {mode_str}")
                if armed:
                    self.arm_status.emit({'arm_status':'Armed'})
                else:
                    self.arm_status.emit({'arm_status': 'Disarmed'})
                self.mode_status.emit({'mode':mode_str})
            # self.battery_info.emit({'BatVol':random.randint(50,100), 'BatLeft':random.randint(50,60)})
            # self.position_updated.emit({'lat':random.uniform(17.311892, 17.311892),'lon':random.uniform(78.496988, 78.495988),'alt':random.randint(5,10), "callsign": "N12345",'heading':260})


            # self.msleep(10)

    def stop(self):
        self.running = False
        self.wait()

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # middleware = FC_MiddlewareThread()

    # # Connect signals
    # middleware.position_updated.connect(lambda data: print("Position:", data))
    # middleware.battery_info.connect(lambda data: print("Battery:", data))
    # middleware.gps_info.connect(lambda data: print("GPS:", data))
    #
    # middleware.MavlinkConnect(COM_Port='COM11', Baud=115200)
    # middleware.start()
    #
    # sys.exit(app.exec_())
