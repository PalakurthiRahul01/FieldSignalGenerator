import sys
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout,
    QWidget, QHBoxLayout, QLabel, QLineEdit, QComboBox
)
from PyQt5.QtCore import QTimer
import pyqtgraph as pg


class RadarSpectrumAnalyzer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Radar Spectrum Analyzer (Calibrated dBm)")
        self.setGeometry(100, 100, 1400, 800)

        # ---------------- System Parameters ----------------
        self.fs = 50e6
        self.window_time = 2e-3
        self.N = int(self.fs * self.window_time)
        self.R = 50  # 50 Ohm system

        # Default parameters
        self.freq = 5e6
        self.PW = 5e-6
        self.PRI = 50e-6
        self.mode = "Pulse"
        self.input_power_dbm = 0

        # ---------------- Layout ----------------
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout()
        central.setLayout(layout)

        controls = QHBoxLayout()
        layout.addLayout(controls)

        controls.addWidget(QLabel("Frequency (MHz):"))
        self.freq_input = QLineEdit("5")
        controls.addWidget(self.freq_input)

        controls.addWidget(QLabel("Input Power (dBm):"))
        self.power_input = QLineEdit("0")
        controls.addWidget(self.power_input)

        controls.addWidget(QLabel("PW (us):"))
        self.pw_input = QLineEdit("5")
        controls.addWidget(self.pw_input)

        controls.addWidget(QLabel("PRI (us):"))
        self.pri_input = QLineEdit("50")
        controls.addWidget(self.pri_input)

        controls.addWidget(QLabel("Mode:"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Pulse", "CW"])
        controls.addWidget(self.mode_combo)

        # ---------------- Time Plot ----------------
        self.time_plot = pg.PlotWidget(title="Time Domain (2 ms)")
        self.time_plot.setLabel('left', 'Amplitude (Volts)')
        self.time_plot.setLabel('bottom', 'Time (ms)')
        self.time_plot.showGrid(x=True, y=True)
        layout.addWidget(self.time_plot)

        self.time_curve = self.time_plot.plot(pen='y')

        # ---------------- Spectrum Plot ----------------
        self.spec_plot = pg.PlotWidget(title="Spectrum (dBm)")
        self.spec_plot.setLabel('left', 'Power (dBm)')
        self.spec_plot.setLabel('bottom', 'Frequency (MHz)')
        self.spec_plot.showGrid(x=True, y=True)
        layout.addWidget(self.spec_plot)

        self.spec_curve = self.spec_plot.plot(pen='c')

        # ---------------- Timer ----------------
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_signal)
        self.timer.start(700)

    # ------------------------------------------------
    def dbm_to_voltage(self, dbm):
        power_watts = 10 ** ((dbm - 30) / 10)
        vrms = np.sqrt(power_watts * self.R)
        vpeak = vrms * np.sqrt(2)
        return vpeak

    # ------------------------------------------------
    def generate_signal(self):

        t = np.arange(self.N) / self.fs
        signal = np.zeros(self.N, dtype=complex)

        amplitude = self.dbm_to_voltage(self.input_power_dbm)

        if self.mode == "CW":
            signal = amplitude * np.exp(1j * 2 * np.pi * self.freq * t)

        else:
            pulse_samples = int(self.PW * self.fs)
            PRI_samples = int(self.PRI * self.fs)

            for start in range(0, self.N, PRI_samples):
                end = start + pulse_samples
                if end < self.N:
                    signal[start:end] = amplitude * np.exp(
                        1j * 2 * np.pi * self.freq * t[start:end]
                    )

        noise = 0.001 * (np.random.randn(self.N) + 1j*np.random.randn(self.N))
        return signal + noise

    # ------------------------------------------------
    def compute_spectrum(self, iq):

        # FFT
        fft_vals = np.fft.fftshift(np.fft.fft(iq))

        # Normalize by N
        fft_vals = fft_vals / self.N

        # Convert to RMS voltage
        vrms = np.abs(fft_vals) / np.sqrt(2)

        # Single-sided correction (very important)
        vrms = vrms * 2

        # Power calculation
        power_watts = (vrms ** 2) / self.R

        # Avoid log(0)
        power_watts[power_watts == 0] = 1e-20

        power_dbm = 10 * np.log10(power_watts) + 30

        freqs = np.fft.fftshift(np.fft.fftfreq(self.N, 1/self.fs))

        return freqs / 1e6, power_dbm

    # ------------------------------------------------
    def update_signal(self):

        self.freq = float(self.freq_input.text()) * 1e6
        self.PW = float(self.pw_input.text()) * 1e-6
        self.PRI = float(self.pri_input.text()) * 1e-6
        self.mode = self.mode_combo.currentText()
        self.input_power_dbm = float(self.power_input.text())

        iq = self.generate_signal()

        # -------- Time Domain --------
        time_axis = np.linspace(0, 2, self.N)
        self.time_curve.setData(time_axis, np.real(iq))

        # -------- Spectrum --------
        freqs, power_dbm = self.compute_spectrum(iq)
        self.spec_curve.setData(freqs, power_dbm)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RadarSpectrumAnalyzer()
    window.show()
    sys.exit(app.exec_())