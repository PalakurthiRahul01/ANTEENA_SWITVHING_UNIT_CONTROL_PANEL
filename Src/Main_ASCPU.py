import sys

import serial
import serial.tools.list_ports
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow

from Src.AS_ControlPannelunit import Ui_MainWindow
from Src.EnumClasses import Enum_connection, Enum_Color_Background
from Src.serial_handler import SerialHandler


class Main_ASCPU(QMainWindow,Ui_MainWindow):
    def __init__(self, parent=None, ):
        super(Main_ASCPU, self).__init__(parent)
        self.setupUi(self)
        self.initUIComponents()
        self.Signals_and_Slots()

    ####################################################################################################################
    def initUIComponents(self):
        self.serial = SerialHandler()
        self.is_connected = False
        self.load_ports()
        self.timer = QTimer()
        self.timer.timeout.connect(self.read_serial)
        self.timer.start(100)

        self.LE_BaudRate.setText(Enum_connection.BAUD_RATE.value)

    ####################################################################################################################
    def Signals_and_Slots(self):
        self.PB_HF1.clicked.connect(self.HF1)
        self.PB_HF2.clicked.connect(self.HF2)
        self.PB_HF_BACKUP_ANT.clicked.connect(self.HF_BackUP_ANT)
        self.PB_HF_Load.clicked.connect(self.HF_Load)
        self.PB_HF_MAIN_ANT.clicked.connect(self.HF_Main_ANT)
        self.PB_BW_HF_ANT.clicked.connect(self.BW_HF_ANT)
        self.PB_Connect.clicked.connect(self.connect_serial)
    ####################################################################################################################
    def load_ports(self):
        self.CB_Portlist.clear()

        ports = serial.tools.list_ports.comports()

        if ports:
            for port in ports:
                self.CB_Portlist.addItem(port.device)
        else:
            self.CB_Portlist.addItem( Enum_connection.NO_PORTS_FOUND.value)
    ####################################################################################
    def connect_serial(self):
        if self.is_connected:
            self.disconnect_serial()
            return
        port = self.CB_Portlist.currentText()
        baud = self.LE_BaudRate.text()

        if Enum_connection.NO_PORTS.value in port:
            print("No valid port selected")
            return

        try:
            self.ser = serial.Serial(port, int(baud), timeout=1)
            self.is_connected = True
            print(f"Connected to {port} @ {baud}")
            self.PB_Connect.setText(Enum_connection.DISCONNECT.value)
            self.CB_Portlist.setEnabled(False)
            self.LE_BaudRate.setEnabled(False)

        except Exception as e:
            print("Connection Error:", e)

    ##################################################################################
    def disconnect_serial(self):

        try:
            if self.ser and self.ser.is_open:
                self.ser.close()

            self.is_connected = False
            print("Disconnected")

            # UI updates
            self.PB_Connect.setText(Enum_connection.CONNECT.value)
            self.CB_Portlist.setEnabled(True)
            self.CB_BaudRate.setEnabled(True)

        except Exception as e:
            print("Disconnect Error:", e)

    #################################################################################
    def read_serial(self):
        if self.is_connected and self.ser and self.ser.is_open:
            try:
                if self.ser.in_waiting:
                    data = self.ser.readline().decode().strip()
                    print("Received Data:", data)
                    self.handle_response(data)
            except Exception as e:
                print("Read Error:", e)
    #################################################################################
    def send_command(self, button, ch):
        if ch == 6:
            if Enum_Color_Background.GREEN_COLOR.value in button.styleSheet():
                cmd = f":{ch},0"
            else:
                cmd = f":{ch},1"
        else:
            cmd = f":{ch},1"

        print("Send Data:", cmd)
        self.send_serial(cmd)
    ##################################################################################
    def HF1(self):
        self.send_command(self.PB_HF1, 1)

    def HF2(self):
        self.send_command(self.PB_HF2, 2)

    def HF_BackUP_ANT(self):
        self.send_command(self.PB_HF_BACKUP_ANT, 3)

    def HF_Load(self):
        self.send_command(self.PB_HF_Load, 4)

    def HF_Main_ANT(self):
        self.send_command(self.PB_HF_MAIN_ANT, 5)

    def BW_HF_ANT(self):
        self.send_command(self.PB_BW_HF_ANT, 6)
    ##############################################################################################
    def send_serial(self, msg):
        print(msg)

        if self.is_connected and self.ser and self.ser.is_open:
            try:
                self.ser.write((msg + "\n").encode())
            except Exception as e:
                print("Serial Error:", e)
        else:
            print("Serial not connected")

    def handle_response(self, data):
        try:
            data = data.strip()
            print("Raw Data:", data)
            if data.startswith(":"):
                data = data[1:]

            parts = data.split(",")
            print("Parsed:", parts)

            if len(parts) == 3 and parts[0] == "R":
                ch = parts[1]
                status = parts[2]
                self.set_button_color(ch, status)

        except Exception as e:
            print("Parse Error:", e)

    def set_button_color(self, ch, status):

        group1 = {
            "1": self.PB_HF1,
            "2": self.PB_HF2
        }

        group2 = {
            "3": self.PB_HF_BACKUP_ANT,
            "4": self.PB_HF_Load,
            "5": self.PB_HF_MAIN_ANT
        }

        group3 = {
            "6": self.PB_BW_HF_ANT
        }

        # ---------------- GROUP 1 ----------------
        if ch in group1:
            if status == "1":
                for btn in group1.values():
                    btn.setStyleSheet("background-color: #444; color: white;")
                group1[ch].setStyleSheet("background-color: #00C853; color: white;")

        # ---------------- GROUP 2 ----------------
        elif ch in group2:
            if status == "1":
                for btn in group2.values():
                    btn.setStyleSheet("background-color: #444; color: white;")
                group2[ch].setStyleSheet("background-color: #00C853; color: white;")

        # ---------------- GROUP 3 ----------------
        elif ch in group3:
            if status == "1":
                group3[ch].setStyleSheet("background-color: #00C853; color: white;")
            else:
                group3[ch].setStyleSheet("background-color: #444; color: white;")

        # if ch in group1:
        #     for btn in group1.values():
        #         btn.setStyleSheet(Enum_Color_Background.BACKGROUND_COLOR_NORMAL.value)
        #
        #     group1[ch].setStyleSheet(Enum_Color_Background.BACKGROUND_COLOR_GREEN.value)
        #
        # elif ch in group2:
        #     for btn in group2.values():
        #         btn.setStyleSheet(Enum_Color_Background.BACKGROUND_COLOR_NORMAL.value)
        #
        #     group2[ch].setStyleSheet(Enum_Color_Background.BACKGROUND_COLOR_GREEN.value)
        #
        # elif ch in group3:
        #     if status == "1":
        #         group3[ch].setStyleSheet(Enum_Color_Background.BACKGROUND_COLOR_NORMAL.value)
        #     else:
        #         group3[ch].setStyleSheet(Enum_Color_Background.BACKGROUND_COLOR_GREEN.value)


########################################################################################################################
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Main_ASCPU()
    win.show()
    sys.exit(app.exec_())