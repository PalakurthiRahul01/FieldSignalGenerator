# FCControlPanelView.py
from PyQt5.QtWidgets import QWidget

from PayloadPanel.LMXControl.RadarAnalyzer import RadarAnalyzer
from PayloadPanel.LMXControl.Test6 import RadarSpectrumAnalyzer
# from PayloadPanel.LMXControl.Test6 import RadarSpectrumAnalyzer





from PayloadPanel.UI.LMXControlPanel import  Ui_FieldSignalGenerator


class LMXControlPanelView(QWidget, Ui_FieldSignalGenerator):
    def __init__(self):
        super().__init__()

        self.setupUi(self)
        self.init_Color_buttons()
        self.open_radar()
        # self._RadarAnalyzer = RadarAnalyzer()
        self.LE_PL_Baud.setText(str(9600))

        self.radius = 0  # Default radius in meters
        self.SystemPosition = (17.309512, 78.496898)  # Default to San Francisco before GPS updates
        self.drone_position = self.SystemPosition  # Initialize at the same place
        # self.ModulationStatusFlag = False
        # self.PB_RF_2.setText("MOD ON")
        # self.PB_RF_2.setStyleSheet("background-color: red; color: white;")
        #
        self.OutPutStatusFlag = False  # RF initially OFF
        self.ModulationStatusFlag = False
        #
        # self.PB_RF.setText("RF ON")
        # self.PB_RF.setStyleSheet("background-color: red; color: white;")
        #
        # self.PB_RF.clicked.connect(self.on_pb_rf_clicked)

        # MAVLink connection

        # UI setup

    def init_Color_buttons(self):
        self.PB_RF_2.setStyleSheet("""
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

        self.PB_RF.setStyleSheet("""
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

        self.PB_PL_Conn.setStyleSheet("""
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
    def Validate_Emulator_Input_Range(self, specs_df):
        freq_min = int(specs_df.loc[specs_df['Parameter'] == 'FREQUENCY', 'min_limit'].values[0])
        freq_max = int(specs_df.loc[specs_df['Parameter'] == 'FREQUENCY', 'max_limit'].values[0])

        pw_min = float(specs_df.loc[specs_df['Parameter'] == 'PW', 'min_limit'].values[0])
        pw_max = float(specs_df.loc[specs_df['Parameter'] == 'PW', 'max_limit'].values[0])

        pri_min = int(specs_df.loc[specs_df['Parameter'] == 'PRI', 'min_limit'].values[0])
        pri_max = int(specs_df.loc[specs_df['Parameter'] == 'PRI', 'max_limit'].values[0])

        attn_min = int(specs_df.loc[specs_df['Parameter'] == 'ATTN', 'min_limit'].values[0])
        attn_max = int(specs_df.loc[specs_df['Parameter'] == 'ATTN', 'max_limit'].values[0])

        self.SB_Frequency.setRange(freq_min,freq_max)
        self.SB_Attenuation.setRange(attn_min,attn_max)
        self.SB_PRI.setRange(pri_min,pri_max)
        self.SB_PW.setRange(pw_min,pw_max)
        self.SB_Ledge_delay.setRange(0.05, 9000)
        self.SB_Tedge_delay.setRange(0.05, 9000)
        self.SB_PW.setSuffix(' μs')

        self.label_ledge.hide()
        self.SB_Ledge_delay.hide()
        self.label_tedge.hide()
        self.SB_Tedge_delay.hide()
        self.PB_Set_Ledge_delay.hide()
        self.PB_Set_Tedge_delay.hide()
    def SetEmulatorDefaultInputs(self,default_inputs_df):
        start_freq = int(default_inputs_df.loc[default_inputs_df['Parameter'] == 'STARTFREQ', 'INPUT'].values[0])
        stop_freq = int(default_inputs_df.loc[default_inputs_df['Parameter'] == 'STOPFREQ', 'INPUT'].values[0])
        step_freq = int(default_inputs_df.loc[default_inputs_df['Parameter'] == 'STEPFREQ', 'INPUT'].values[0])
        pw = int(default_inputs_df.loc[default_inputs_df['Parameter'] == 'PW', 'INPUT'].values[0])
        pri = int(default_inputs_df.loc[default_inputs_df['Parameter'] == 'PRI', 'INPUT'].values[0])
        attn = int(default_inputs_df.loc[default_inputs_df['Parameter'] == 'ATTN', 'INPUT'].values[0])

        self.SB_Frequency.setValue(start_freq)
        self.SB_Attenuation.setValue(attn)
        self.SB_PRI.setValue(pri)
        self.SB_PW.setValue(pw)
    def update_radius(self, value):
        """Updates radius value from slider."""
        self.radius = value
        self.radius_label.setText(f"Radius: {self.radius}m")

    def populate_ports(self, port_list):
        self.CB_PL_Port.clear()
        self.CB_PL_Port.addItems(port_list)

    def get_selected_port(self):
        return self.CB_PL_Port.currentText()

    def get_baudrate(self):
        return self.LE_PL_Baud.text()

    def connect_buttons(self, controller):
        self.controller = controller

        self.PB_PL_Conn.clicked.connect(controller.handle_connection)
        self.PB_Set_Frequency.clicked.connect(controller.SetFrequency)
        self.PB_Set_pw.clicked.connect(controller.SetPulseWidth)
        self.PB_Set_pri.clicked.connect(controller.SetPeriod)
        self.PB_Set_Attenuation.clicked.connect(controller.SetAttenuation)
        # self.PB_RF.clicked.connect(self.on_pb_rf_clicked)
        # self.PB_RF_2.clicked.connect(self.on_pb_modulation_clicked)
        self.PB_RF.clicked.connect(controller.SetRFONOFF)
        self.PB_RF_2.clicked.connect(controller.SetModulationONOFF)
        self.PB_Send_All.clicked.connect(controller.send_all_commands)

    def open_radar(self):
        self.radar_window = RadarAnalyzer()
        self.VL_RadarAnalyzer.addWidget(self.radar_window)

    def on_pb_modulation_clicked(self):
        if not self.controller.SetModulationONOFF():
            print("Modulation command failed")
            return
        if self.ModulationStatusFlag:
            # ON State
            self.PB_RF_2.setText("MOD OFF")
            self.PB_RF_2.setStyleSheet(
                "background-color: green; color: white;"
            )
            print("Modulation ON")
        else:
            # OFF State
            self.PB_RF_2.setText("MOD ON")
            self.PB_RF_2.setStyleSheet(
                "background-color: red; color: white;"
            )
            print("Modulation OFF")

    def on_pb_rf_clicked(self):

        if not self.controller.SetRFONOFF():
            print("RF Command Failed")
            return

        # Update UI
        if self.OutPutStatusFlag:
            # RF ON
            self.PB_RF.setText("RF OFF")
            self.PB_RF.setStyleSheet("background-color: green; color: white;")
            print("RF ON")

        else:
            # RF OFF
            self.PB_RF.setText("RF ON")
            self.PB_RF.setStyleSheet("background-color: red; color: white;")
            print("RF OFF")

