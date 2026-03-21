# FCControlPanelModel.py

class LMXControlPanelModel:
    def __init__(self):
        self.connected = False
        self.armed = False
        self.mode = None
        self.altitude = 0
        self.port = None
        self.baudrate = None

    def Connect_to_FC(self, port, baudrate):
        self.port = port
        self.baudrate = baudrate

        self.connected = True  # Simulate successful connection

    def toggle_arm(self):
        self.armed = not self.armed
