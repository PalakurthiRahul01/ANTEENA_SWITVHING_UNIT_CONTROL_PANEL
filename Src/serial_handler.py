import serial
import serial.tools.list_ports
from PyQt5.QtCore import QObject, pyqtSignal


class SerialHandler(QObject):
    data_received = pyqtSignal(str)
    connected = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.ser = None

    def connect(self, port, baud):
        try:
            self.ser = serial.Serial(port, int(baud), timeout=1)
            self.connected.emit(True)
        except Exception as e:
            print("Connect Error:", e)
            self.connected.emit(False)

    def disconnect(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
        self.connected.emit(False)

    def send(self, data):
        if self.ser and self.ser.is_open:
            self.ser.write((data + "\n").encode())

    def read(self):
        if self.ser and self.ser.is_open and self.ser.in_waiting:
            try:
                return self.ser.readline().decode().strip()
            except:
                return None
        return None

    @staticmethod
    def list_ports():
        return [p.device for p in serial.tools.list_ports.comports()]