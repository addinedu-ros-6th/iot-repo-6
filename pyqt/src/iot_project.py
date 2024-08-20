import sys
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
import urllib.request
import cv2, imutils
import time 
import datetime
import socket
import struct
import pickle
import io
import numpy as np
from collections import namedtuple




class ImageReceiver(QThread):
    frame_received = pyqtSignal(QImage)
    connection_status = pyqtSignal(bool)

    def __init__(self, ip='0.0.0.0', port=8000):
        super().__init__()
        self.ip = ip
        self.port = port
        self.is_running = True
        self.server_socket = None
        self.client_socket = None

    def run(self):
        while self.is_running:
            if self.client_socket is None:
                self.start_server()
            else:
                self.receive_frames()

    def start_server(self):
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.bind((self.ip, self.port))
            self.server_socket.listen(1)
            print("Waiting for a connection...")
            self.client_socket, _ = self.server_socket.accept()
            print("Connection established")
            self.connection_status.emit(True)
        except socket.error as e:
            print(f"Socket error: {e}")
            self.retry_connection()

    def receive_frames(self):
        data = b""
        payload_size = struct.calcsize("L")

        try:
            while self.is_running:
                while len(data) < payload_size:
                    packet = self.client_socket.recv(4096)
                    if not packet:
                        raise ConnectionError("Connection lost")
                    data += packet

                packed_msg_size = data[:payload_size]
                data = data[payload_size:]
                msg_size = struct.unpack("L", packed_msg_size)[0]

                while len(data) < msg_size:
                    data += self.client_socket.recv(4096)

                frame_data = data[:msg_size]
                data = data[msg_size:]

                frame = pickle.loads(frame_data)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = frame.shape
                bytes_per_line = ch * w
                qimg = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                self.frame_received.emit(qimg)

                if self.video_writer is not None:
                    self.video_writer.write(frame)

        except (ConnectionError, pickle.UnpicklingError) as e:
            print(f"Error receiving frames: {e}")
            self.retry_connection()

    def send_data(self, data):
        try:
            self.client_socket.sendall(data.encode())
            print(f"Sent data: {data}")
        except Exception as e:
            print(f"Error sending data: {e}")

    def retry_connection(self):
        self.client_socket = None
        self.connection_status.emit(False)

    def start_recording(self, file_path):
        # Start writing video file
        self.video_writer = cv2.VideoWriter(file_path, cv2.VideoWriter_fourcc(*'XVID'), 20.0, (640, 480))

    def stop_recording(self):
        if self.video_writer is not None:
            self.video_writer.release()
            self.video_writer = None

    def stop(self):
        self.is_running = False
        if self.client_socket:
            self.client_socket.close()

    def send_data(self, data):
        try:
            self.client_socket.sendall(data.encode())
            print(f"Sent data: {data}")
        except Exception as e:
            print(f"Error sending data: {e}")

    def retry_connection(self):
        self.client_socket = None
        self.connection_status.emit(False)

        self.quit()
        self.wait()




Constants = namedtuple('Constants', ['USER_UI', 'DEVELOP_UI'])
constants = Constants(0,1)

from_class = uic.loadUiType('/home/jeback/dev_ws/PyQt_cv/ui/main.ui')[0]

class Windowclass(QMainWindow, from_class):
    def __init__(self):

        super().__init__()
        self.setupUi(self)

        self.ModePage.clicked.connect(self.switchUI)
        # Set the initial UI
        self.stackedUI.setCurrentIndex(constants.USER_UI)
        self.m_UserPage = self.stackedUI.widget(constants.USER_UI)
        self.m_DevelopPage = self.stackedUI.widget(constants.DEVELOP_UI)     

        self.m_MinValue = self.m_UserPage.findChild(QLabel, "MinValue")
        self.m_MidValue = self.m_UserPage.findChild(QLabel, "MidValue")
        self.m_MaxValue = self.m_UserPage.findChild(QLabel, "MaxValue")
        self.m_MotorValue = self.m_UserPage.findChild(QLabel, "MotorValue")

        self.m_ComStatus = self.m_UserPage.findChild(QLabel, "ComStatus")
        self.m_StreamBtn = self.m_UserPage.findChild(QPushButton, "StreamBtn")   

        self.m_DisplayFrame = self.m_UserPage.findChild(QLabel, "DisplayFrame")
        self.m_MoveBar = self.m_UserPage.findChild(QSlider, "MoveBar")
        self.m_ManualBtn = self.m_UserPage.findChild(QPushButton, "ManualBtn")
        self.m_RecBtn = self.m_UserPage.findChild(QPushButton, "RecBtn")

        self.updateMotorValue(self.m_MoveBar.value())
        self.m_ManualBtn.clicked.connect(self.clickedManualBtn)
        self.m_MoveBar.valueChanged.connect(self.updateMotorValue)

        self.m_MoveBar.setEnabled(False)
        self.m_ManualBtn.setEnabled(False)
        self.m_RecBtn.setEnabled(False)
        
        self.m_ComStatus.setText("TCP / IP Not connected")
        self.m_StreamBtn.clicked.connect(self.clickedStreamBtn)

        self.m_MinValue.setText("MinValue : {}".format(self.m_MoveBar.minimum()))
        self.m_MaxValue.setText("MaxValue : {}".format(self.m_MoveBar.maximum()))
        self.m_MidValue.setText("MidValue : 0")

        self.m_isStreamOn = False  # Stream On Off 반전 시킬 용도로만 사용됨. 
        self.m_isManualModeOn = False # Manual Mode On Off 반전 시킬 용도로 사용됨.
        self.m_isRecordOn = False #Record On Off 반전 시킬 용도로 사용됨 . 
        self.m_image_receiver = None # Image receive Thread 생성될 변수

        self.pixmap = QPixmap()  # QLabel 에 이미지 띄울 때 쓰는 변수

    def switchUI(self):
        current_index = self.stackedUI.currentIndex()

        if current_index == constants.USER_UI:
            self.stackedUI.setCurrentIndex(constants.DEVELOP_UI)
            self.ModePage.setText('User Page')            
        else: # current_index == constants.DEVELOP_UI:
            self.stackedUI.setCurrentIndex(constants.USER_UI)
            self.ModePage.setText('Developer Page')            

    def clickedStreamBtn(self):        
        if self.m_isStreamOn == False:  
            #self.start_stream()
            self.m_StreamBtn.setText("Stream OFF")
            self.m_isStreamOn = True            
        else: # self.m_isStreamOn == True: 
            #self.stop_stream()
            self.m_StreamBtn.setText("Stream ON")
            self.m_isStreamOn = False
    
    def clickedManualBtn(self):
        if self.m_isManualModeOn == False:
            self.m_ManualBtn.setText("OFF")
            self.m_isManualModeOn = True
            # DB에서 마지막 모터값을 받아오는 코드 적용 해야함. 
            self.m_MoveBar.setEnabled(True)
            #self.send_command()
        else: # self.m_isManualModeOn == True:
            self.m_ManualBtn.setText("ON")
            self.m_isManualModeOn = False
            self.m_MoveBar.setEnabled(False)

    def clickedRecordBtn(self):
        if self.m_isRecordOn == False:
            self.m_RecBtn.setText("OFF")
            self.m_isRecordOn = True
            #self.start_recording()
        else: # self.m_isRecordOn == True:
            self.m_RecBtn.setText("ON") 
            self.m_isRecordOn = False
            #self.stop_recording()

    def updateMotorValue(self, value):
        self.m_MotorValue.setText(f'Motor Angle : {value}')
        Command = "GRM" # GUI -> RAS Manual Mode 전송 
        MotorValue = (value + 90)
        MotorValue = MotorValue.to_bytes(1, byteorder='big')
        CheckSum   = MotorValue 
        DataPacket = Command.encode() + MotorValue
        #self.m_image_receiver.send_data(DataPacket)
            
    def start_stream(self):
        if self.m_image_receiver and self.m_image_receiver.isRunning():
            return

        # 서버 IP와 포트 번호 설정
        server_ip = '192.168.0.x'  # 라즈베리파이의 IP 주소로 변경
        server_port = 8000

        # 이미지 수신 스레드 생성 및 시작
        self.m_image_receiver = ImageReceiver(server_ip, server_port)
        self.m_image_receiver.frame_received.connect(self.update_image)
        self.m_image_receiver.connection_status.connect(self.update_status)
        self.m_image_receiver.start()

    def stop_stream(self):
        if self.m_image_receiver:
            self.m_image_receiver.stop()
            self.m_image_receiver = None
            self.m_ComStatus.setText('TCP/IP Not connected')

    def update_image(self, q_img):
        self.pixmap = self.pixmap.fromImage(q_img)
        self.pixmap = self.pixmap.scaled(self.m_DisplayFrame.width(), self.m_DisplayFrame.height())
        self.m_DisplayFrame.setPixmap(self.pixmap)
    
    def start_recording(self):
        now = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = now + '.avi'
        file_path = '/home/kjb/dev_ws/pyqt_cv/data/{0}'.format(filename)
        self.m_image_receiver.start_recording(file_path)

    def stop_recording(self):
        self.m_image_receiver.stop_recording()

    def update_status(self, status):
        if status:
            self.m_ComStatus.setText('TCP / IP Connected')
            self.m_ManualBtn.setEnabled(True)
            self.m_RecBtn.setEnabled(True)
            if self.m_isManualModeOn == True:
                self.m_MoveBar.setEnabled(True)
        else:
            self.m_ComStatus.setText('TCP / IP Not connected')
            self.m_ManualBtn.setEnabled(False)
            self.m_MoveBar.setEnabled(False)
            self.m_RecBtn.setEnabled(False)            
            if self.m_isRecordOn == True:
                self.stop_recording()
                self.m_RecBtn.setText("OFF")
                self.m_isRecordOn = False

    def send_command(self, DataPacket):
        if self.m_image_receiver:
            self.m_image_receiver.send_command(DataPacket)

    def closeEvent(self, event):
        self.stop_stream()
        event.accept()
        



if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindows = Windowclass()
    myWindows.show()
    sys.exit(app.exec_())