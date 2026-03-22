from PyQt5.QtWidgets import QApplication, QWidget
import sys

from PayloadPanel.LMXControl.LMXControlCntrl import LMXControlCntrl
from PayloadPanel.LMXControl.LMXControlModel import LMXControlPanelModel
from PayloadPanel.LMXControl.LMXControlView import LMXControlPanelView
from PayloadPanel.UI.LMXPanel import Ui_Form


class LMXPanelWidget(QWidget, Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # Health status setup
        self.lmx_model = LMXControlPanelModel()
        self.lmx_view = LMXControlPanelView()
        self.lmx_controller = LMXControlCntrl(self.lmx_model, self.lmx_view)

        self.VL_LMXControls.addWidget(self.lmx_view)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LMXPanelWidget()
    window.showMaximized()
    sys.exit(app.exec_())