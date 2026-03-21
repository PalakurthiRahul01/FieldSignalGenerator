import math
import os

import pandas as pd
from PyQt5.QtCore import QTimer, pyqtSignal, QObject
from PyQt5.QtGui import QIcon
import serial.tools.list_ports

from PayloadPanel.LMXControl.RadarAnalyzer import RadarAnalyzer
from PayloadPanel.Payload.Middleware.PL_Middleware import PL_MiddlewareThread


class LMXControlCntrl(QObject):

    telemetry_signal = pyqtSignal(dict)
    waypoints_signal = pyqtSignal(list)
    radarParamsChanged = pyqtSignal(dict)

    def __init__(self, model, view):
        super().__init__()

        self.model = model
        self.view = view
        # self._RadarAnalyzer = RadarAnalyzer()

        # self.radarParamsChanged.connect(self._RadarAnalyzer.set_radar_parameters)

        self.view.connect_buttons(self)

        self.middleware             = None
        self.ConnFlag               = False
        self.OutPutStatusFlag       = False
        self.ModulationStatusFlag   = False
        self.rf_status_flag         = False
        self.mod_status_flag         = False

        self.Update_EmulatorInputsRange()
        self.Update_EmulatorDefaultInputs()
        self.Get_PortList()

        self.input_data = {'freq': self.view.SB_Frequency.value(),
                'pw': self.view.SB_PW.value(),
                'pri': self.view.SB_PRI.value()
                }

    def Update_Inputs(self,data):
        self.view.radar_window.update_input_parameters(data=data)

    def Update_EmulatorInputsRange(self):
        proj_path = os.getcwd()
        spec_file = r'EmulatorInputsRangeSpecs.xlsx'
        file_path = os.path.join(proj_path, spec_file)
        specs_df = pd.read_excel(file_path)
        self.view.Validate_Emulator_Input_Range(specs_df= specs_df)

    def Update_EmulatorDefaultInputs(self):
        proj_path = os.getcwd()
        spec_file = r'EmulatorDefaultInputsSpecs.xlsx'
        file_path = os.path.join(proj_path, spec_file)
        defaultspecs_df = pd.read_excel(file_path)
        self.view.SetEmulatorDefaultInputs(default_inputs_df= defaultspecs_df)

    def Get_PortList(self):
        ports = serial.tools.list_ports.comports()
        port_list = []
        for port in ports:
            print(f"Port: {port.device} - {port.description}")
            port_list.append(port.device)
        self.view.populate_ports(port_list)

    # def handle_connection(self):
    #
    #     # proj_path = os.getcwd()
    #     # icon_path = ''
    #     if self.ConnFlag == False:
    #         port = self.view.get_selected_port()
    #         baudrate = self.view.get_baudrate()
    #         self.model.Connect_to_FC(port, baudrate)
    #         print(f"Connected to {port} @ {baudrate}")
    #
    #         # Start middleware thread
    #         self.middleware = PL_MiddlewareThread()
    #
    #         Conn_Status = self.middleware.LMXConnect(COM_Port=port, Baud=baudrate)
    #         if Conn_Status == True:
    #             # self.middleware.position_updated.connect(self.handle_position_update)
    #             # if self.health_controller:
    #             #     self.middleware.battery_info.connect(self.health_controller.ShowBatteryStatus)
    #             #     self.middleware.arm_status.connect(self.health_controller.ShowArmStatus)
    #             #     self.middleware.mode_status.connect(self.health_controller.ShowModeStatus)
    #             #     self.middleware.gps_info.connect(self.health_controller.ShowGPSStatus)
    #             #     self.middleware.position_updated.connect(self.health_controller.ShowPositionStatus)
    #             #     self.middleware.failsafe_message.connect(self.handle_failsafe_message)
    #
    #             # self.middleware.start()
    #             self.view.PB_PL_Conn.setIcon(QIcon(r'/Src/MMI/Resources/Icons/connect.png'))
    #             self.ConnFlag = True
    #     elif self.ConnFlag == True:
    #         self.middleware.LMXClose()
    #         self.view.PB_PL_Conn.setIcon(QIcon(r'/Src/MMI/Resources/Icons/disconnect.png'))
    #         self.ConnFlag = False
    #         self.middleware = None

    def handle_connection(self):

        if self.ConnFlag == False:

            port = self.view.get_selected_port()
            baudrate = self.view.get_baudrate()

            self.model.Connect_to_FC(port, baudrate)
            print(f"Connected to {port} @ {baudrate}")

            self.middleware = PL_MiddlewareThread()
            Conn_Status = self.middleware.LMXConnect(COM_Port=port, Baud=baudrate)

            if Conn_Status == True:
                # 🟢 Connected State
                self.view.PB_PL_Conn.setText("Disconnect")
                self.view.PB_PL_Conn.setIcon(QIcon(r'/Src/MMI/Resources/Icons/connect.png'))
                self.view.PB_PL_Conn.setStyleSheet("""
                    QPushButton {
                        background-color: green;
                        color: white;
                        font-weight: bold;
                        border-radius: 6px;
                        padding: 5px;
                    }
                    QPushButton:hover {
                        background-color: #00aa00;
                    }
                """)

                self.ConnFlag = True

        else:

            # 🔴 Disconnect
            self.middleware.LMXClose()

            self.view.PB_PL_Conn.setText("Connect")
            self.view.PB_PL_Conn.setIcon(QIcon(r'/Src/MMI/Resources/Icons/disconnect.png'))
            self.view.PB_PL_Conn.setStyleSheet("""
                QPushButton {
                    background-color: red;
                    color: white;
                    font-weight: bold;
                    border-radius: 6px;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #cc0000;
                }
            """)

            self.ConnFlag = False
            self.middleware = None

#######################################################################################################
    def emit_radar_parameters(self):

        radar_data = {
            "freq": self.view.SB_Frequency.value(),
            "pw": self.view.SB_PW.value(),
            "pri": self.view.SB_PRI.value(),
            "attn":self.view.SB_Attenuation.value()

        }

        self.radarParamsChanged.emit(radar_data)
##################################################################################################################
    def SetFrequency(self):
        if self.middleware is None:
            return False
        freq_value = self.view.SB_Frequency.value()
        self.middleware.SetFreq(freq=freq_value)
        self.input_data = {'freq': self.view.SB_Frequency.value()}
        self.Update_Inputs(data=self.input_data)
        if self.middleware.ErrorFlag:
            return False
        # self.emit_radar_parameters()
        return True

    def SetPulseWidth(self):
        if self.middleware is None:
            return False
        pw_value = self.view.SB_PW.value()
        self.middleware.SetPW(pw=pw_value)
        self.input_data = {'pw': self.view.SB_PW.value()}
        self.Update_Inputs(data=self.input_data)
        if self.middleware.ErrorFlag:
            return False
        # self.emit_radar_parameters()
        return True

    def SetPeriod(self):
        if self.middleware is None:
            return False
        pri_value = self.view.SB_PRI.value()
        self.middleware.SetPRI(pri=pri_value)
        self.input_data = {'pri': self.view.SB_PRI.value()}
        if self.middleware.ErrorFlag:
            return False
        # self.emit_radar_parameters()
        return True

##################################################################################################################
    # def SetFrequency(self):
    #     if self.middleware != None:
    #         self.middleware.SetFreq(freq=self.view.SB_Frequency.value())
    #         if self.middleware.ErrorFlag == True:
    #             return False
    #         return True
    #     else:
    #         return False

    # def SetPulseWidth(self):
    #     if self.middleware != None:
    #         self.middleware.SetPW(pw=self.view.SB_PW.value())
    #         if self.middleware.ErrorFlag == True:
    #             return False
    #         self.emit_radar_parameters()
    #         return True
    #     else:
    #         return False


    # def SetPeriod(self):
    #     if self.middleware != None:
    #         self.middleware.SetPRI(pri=self.view.SB_PRI.value())
    #         if self.middleware.ErrorFlag == True:
    #             return False
    #         return True
    #     else:
    #         return False


    def SetAttenuation(self):
        if self.middleware != None:
            attn = self.view.SB_Attenuation.value()
            self.middleware.SetAttn(attn=attn)
            self.input_data = {'attn': self.view.SB_Attenuation.value()}
            if self.middleware.ErrorFlag == True:
                return False
            return True
        else:
            return False

    # def SetRFONOFF(self):
    #     if self.middleware != None:
    #         if self.OutPutStatusFlag == False:
    #             self.middleware.SetStatus(status=1)
    #             self.view.PB_RF.setText("RF OFF")
    #             if self.middleware.ErrorFlag == True:
    #                 self.OutPutStatusFlag = False
    #                 return False
    #             self.OutPutStatusFlag = True
    #             return True
    #         elif self.OutPutStatusFlag == True:
    #             self.middleware.SetStatus(status=0)
    #             self.view.PB_RF.setText("RF ON")
    #             if self.middleware.ErrorFlag == True:
    #                 self.OutPutStatusFlag = True
    #                 return False
    #             self.OutPutStatusFlag = False
    #             return True
    #
    #     else:
    #         return False

    def SetRFONOFF(self):

        if self.middleware is None:
            return False
        # -------- RF ON --------
        if self.OutPutStatusFlag is False:
            self.middleware.SetStatus(status=1)
            if self.middleware.ErrorFlag:
                return False
            self.OutPutStatusFlag = True
            self.view.PB_RF.setText("RF OFF")
            self.view.PB_RF.setIcon(QIcon(r'/Src/MMI/Resources/Icons/connect.png'))
            self.view.PB_RF.setStyleSheet("""
                               QPushButton {
                                   background-color: green;
                                   color: white;
                                   font-weight: bold;
                                   border-radius: 6px;
                                   padding: 5px;
                               }
                               QPushButton:hover {
                                   background-color: #00aa00;
                               }
                           """)
            if hasattr(self.view, "radar_window"):
                self.view.radar_window.set_rf_status(True)
            return True
        # -------- RF OFF --------
        else:
            self.middleware.SetStatus(status=0)
            if self.middleware.ErrorFlag:
                return False
            self.OutPutStatusFlag = False
            self.view.PB_RF.setText("RF ON")

            self.view.PB_RF.setStyleSheet("""
                            QPushButton {
                                background-color: red;
                                color: white;
                                font-weight: bold;
                                border-radius: 6px;
                                padding: 5px;
                            }
                            QPushButton:hover {
                                background-color: #cc0000;
                            }
                        """)

            if hasattr(self.view, "radar_window"):
                self.view.radar_window.set_rf_status(False)
            return True
    # def SetModulationONOFF(self):
    #     if self.middleware is not None:
    #
    #         if self.ModulationStatusFlag == False:
    #             self.middleware.SetModulation(mod=1)
    #             self.view.PB_RF_2.setText("MOD OFF")
    #             if hasattr(self.view, "radar_window"):
    #                 self.view.radar_window.set_mod_status(True)
    #             if self.middleware.ErrorFlag == True:
    #                 self.ModulationStatusFlag = False
    #                 return False
    #             self.ModulationStatusFlag = True
    #             return True
    #
    #
    #         elif self.ModulationStatusFlag == True:
    #             self.middleware.SetModulation(mod=0)
    #             self.view.PB_RF_2.setText("MOD ON")
    #             if hasattr(self.view, "radar_window"):
    #                 self.view.radar_window.set_mod_status(False)
    #             if self.middleware.ErrorFlag == True:
    #                 self.ModulationStatusFlag = True
    #                 return False
    #
    #             self.ModulationStatusFlag = False
    #             return True
    #
    #     else:
    #         return False
    def SetModulationONOFF(self):
        if self.middleware is None:
            return False
        # -------- MOD ON --------
        if self.ModulationStatusFlag is False:
            self.middleware.SetModulation(mod=1)
            if self.middleware.ErrorFlag:
                return False
            self.ModulationStatusFlag = True
            self.view.PB_RF_2.setText("MOD OFF")
            self.view.PB_RF_2.setStyleSheet("""
                                           QPushButton {
                                               background-color: green;
                                               color: white;
                                               font-weight: bold;
                                               border-radius: 6px;
                                               padding: 5px;
                                           }
                                           QPushButton:hover {
                                               background-color: #00aa00;
                                           }
                                       """)
            if hasattr(self.view, "radar_window"):
                self.view.radar_window.set_mod_status(True)
            return True
        #MOD OFF
        else:
            self.middleware.SetModulation(mod=0)
            if self.middleware.ErrorFlag:
                return False
            self.ModulationStatusFlag = False
            self.view.PB_RF_2.setText("MOD ON")
            self.view.PB_RF_2.setStyleSheet("""
                                        QPushButton {
                                            background-color: red;
                                            color: white;
                                            font-weight: bold;
                                            border-radius: 6px;
                                            padding: 5px;
                                        }
                                        QPushButton:hover {
                                            background-color: #cc0000;
                                        }
                                    """)
            if hasattr(self.view, "radar_window"):
                self.view.radar_window.set_mod_status(False)
            return True

    # def SetRFONOFF(self):
    #     if not self.middleware:
    #         return False
    #     new_status = 0 if self.OutPutStatusFlag else 1
    #     self.middleware.SetStatus(status=new_status)
    #     if self.middleware.ErrorFlag:
    #         return False
    #     self.OutPutStatusFlag = bool(new_status)
    #     return True


    # def SetModulationONOFF(self):
    #
    #     if not self.middleware:
    #         return False
    #
    #     new_status = 0 if self.ModulationStatusFlag else 1
    #     self.middleware.SetModulation(status=new_status)
    #
    #     if self.middleware.ErrorFlag:
    #         return False
    #
    #     self.ModulationStatusFlag = bool(new_status)
    #     return True

    def send_all_commands(self):
        if self.middleware != None:
            freq_status = self.SetFrequency()
            if freq_status == False:
                return False
            pw_status = self.SetPulseWidth()
            if pw_status == False:
                return False
            pri_status = self.SetPeriod()
            if pri_status == False:
                return False
            attn_status = self.SetAttenuation()
            if attn_status == False:
                return False
            return True
        else:
            return False


    def handle_failsafe_message(self, message):
        self.failsafe_reset_timer.stop()
        if self.health_controller:
            self.health_controller.ShowFailsafeMessage(message)
        self.failsafe_reset_timer.start()  # Reset the timer

    def reset_failsafe_status(self):
        if self.health_controller:
            self.health_controller.ShowFailsafeOK()

    def handle_position_update(self, data):
        # print("POSITION UPDATE:", data)
        self.latitude = data['lat']
        self.longitude = data['lon']
        self.telemetry_signal.emit(data)

    def arm_or_disarm(self):
        if self.middleware != None:
            if self.ARM_DISARM_FLAG == False:
                arm_status = self.middleware.ARM()
                if arm_status == True:
                    self.ARM_DISARM_FLAG = True
                    self.view.TB_ARM_DISARM.setText('DISARM')
            elif self.ARM_DISARM_FLAG == True:
                disarm_status = self.middleware.DISARM()
                if disarm_status == True:
                    self.ARM_DISARM_FLAG = False
                    self.view.TB_ARM_DISARM.setText('ARM')



