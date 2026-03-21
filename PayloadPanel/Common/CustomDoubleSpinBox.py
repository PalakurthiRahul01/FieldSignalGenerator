from PyQt5.QtWidgets import QDoubleSpinBox


class CustomDoubleSpinBox(QDoubleSpinBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDecimals(2)  # Set default number of decimal places

    def stepBy(self, steps):
        """
        Adjusts the step size based on the cursor position relative to the decimal point.
        """
        cursor_position = self.lineEdit().cursorPosition()
        text = self.text()
        decimal_position = text.find('.')

        # Determine step size based on cursor position relative to decimal point
        if decimal_position != -1 and cursor_position > decimal_position:
            self.setSingleStep(0.1)  # Smaller step for fractional values
        else:
            self.setSingleStep(1.0)  # Larger step for whole values

        # Perform the step operation
        super().stepBy(steps)

        # Restore the cursor position after stepping
        self.lineEdit().setCursorPosition(cursor_position)

    def get_value(self):
        """
        Formats the value to two decimal places for display.
        """
        return round(float(self.value()), 2)
