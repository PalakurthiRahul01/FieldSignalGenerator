
import sys
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout,
    QWidget, QHBoxLayout, QLabel,
    QLineEdit, QComboBox
)
from PyQt5.QtCore import QTimer
import pyqtgraph as pg


class RadarAnalyzer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Radar Time + Spectrum Analyzer (Calibrated dBm)")
        self.setGeometry(100, 100, 1400, 900)

        # -------- Parameters --------
        self.fs = 100e6
        self.window_time = 2e-3
        self.N = int(self.fs * self.window_time)
        self.R = 50  # 50 Ohm system

        self.center_freq = 10e9
        self.PW = 5e-6
        self.PRI = 50e-6
        self.input_power_dbm = 0
        self.attn = 0

        self.rf_status_flag = False
        self.mod_status_flag = False

        # -------- Layout --------
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout()
        central.setLayout(main_layout)

        # -------- Time Plot --------
        self.time_plot = pg.PlotWidget(title="Time Domain (2 ms)")
        self.time_plot.setLabel('left', 'Amplitude (Volts)')
        self.time_plot.setLabel('bottom', 'Time (ms)')
        self.time_plot.showGrid(x=True, y=True)
        main_layout.addWidget(self.time_plot)

        self.curve_I = self.time_plot.plot(pen='r')
        self.curve_mag = self.time_plot.plot(pen='y')

        # -------- Spectrum Plot --------
        self.fft_plot = pg.PlotWidget(title="Spectrum (dBm)")
        self.fft_plot.setLabel('left', 'Power (dBm)')
        self.fft_plot.setLabel('bottom', 'Frequency (GHz)')
        self.fft_plot.showGrid(x=True, y=True)
        main_layout.addWidget(self.fft_plot)

        self.curve_fft = self.fft_plot.plot(pen='g')

        # -------- Timer --------
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_display)
        self.timer.start(500)

        # Default backend init
        self.update_input_parameters({
            "freq": 10,
            "pw": 5,
            "pri": 50,
            "power": 0,
            "attn": 0
        })

    # dBm → Peak Voltage

    def dbm_to_voltage(self, dbm):

        # Apply attenuation
        effective_dbm = dbm - self.attn

        power_watts = 10 ** ((effective_dbm - 30) / 10)
        vrms = np.sqrt(power_watts * self.R)
        vpeak = vrms * np.sqrt(2)

        return vpeak

    # Backend Update

    def set_rf_status(self, status: bool):
        self.rf_status_flag = status

    def set_mod_status(self, status: bool):
        self.mod_status_flag = status

    def update_input_parameters(self, data):
        if "freq" in data:
            self.center_freq = float(data["freq"]) * 1e9
        if "pw" in data:
            self.PW = float(data["pw"]) * 1e-6
        if "pri" in data:
            self.PRI = float(data["pri"]) * 1e-6
        if "power" in data:
            self.input_power_dbm = float(data["power"])
        if "attn" in data:
            self.attn = float(data["attn"])

    # Signal Generation (Power Calibrated)
    def generate_signal(self):

        if not self.rf_status_flag:
            return np.zeros(self.N, dtype=complex)

        t = np.arange(self.N) / self.fs

        amplitude = self.dbm_to_voltage(self.input_power_dbm)

        noise = 0.002 * (
            np.random.randn(self.N) +
            1j * np.random.randn(self.N)
        )

        carrier = amplitude * np.exp(
            1j * 2 * np.pi * (self.center_freq % self.fs) * t
        )

        # MOD OFF → Continuous Wave
        if not self.mod_status_flag:
            return carrier + noise

        # MOD ON → Pulsed
        pulse_samples = max(1, int(self.PW * self.fs))
        PRI_samples = max(1, int(self.PRI * self.fs))

        signal = np.zeros(self.N, dtype=complex)

        for start in range(0, self.N, PRI_samples):
            end = min(start + pulse_samples, self.N)
            signal[start:end] = carrier[start:end]

        return signal + noise

    # --------------------------------------------------
    # Calibrated Spectrum (dBm)
    # --------------------------------------------------
    def compute_spectrum(self, iq):

        window = np.hanning(self.N)
        iq_windowed = iq * window

        fft_vals = np.fft.fftshift(np.fft.fft(iq_windowed))
        fft_vals = fft_vals / self.N

        vrms = np.abs(fft_vals) / np.sqrt(2)
        vrms = vrms * 2  # single sided correction

        power_watts = (vrms ** 2) / self.R
        power_watts[power_watts <= 0] = 1e-20

        power_dbm = 10 * np.log10(power_watts) + 30

        freqs = np.fft.fftshift(
            np.fft.fftfreq(self.N, 1/self.fs)
        )

        return (
            (self.center_freq + freqs) / 1e9,
            power_dbm
        )

    # --------------------------------------------------
    # Display Update
    # --------------------------------------------------
    def update_display(self):

        iq = self.generate_signal()

        # ---- Time Domain ----
        I = np.real(iq)
        magnitude = np.abs(iq)
        time_axis = np.linspace(0, 2, self.N)

        self.curve_I.setData(time_axis, I)
        self.curve_mag.setData(time_axis, magnitude)

        # ---- Spectrum ----
        freq_axis, power_dbm = self.compute_spectrum(iq)
        self.curve_fft.setData(freq_axis, power_dbm)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    radar = RadarAnalyzer()

    # Example: Turn ON RF & MOD for testing
    radar.set_rf_status(True)
    radar.set_mod_status(True)

    radar.show()
    sys.exit(app.exec_())