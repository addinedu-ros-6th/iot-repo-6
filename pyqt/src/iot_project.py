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
import res_rc




class Communicator(QThread):
    frame_received = pyqtSignal(QImage)
    connection_status = pyqtSignal(bool)

    def __init__(self, ip='0.0.0.0', port=8000):
        super().__init__()
        self.ip = ip
        self.port = port
        self.is_running = True
        self.server_socket = None
        self.client_socket = None
        self.video_writer = None

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
            self.connection = self.client_socket.makefile('rb')
            print("Connection established")
            self.connection_status.emit(True)
        except socket.error as e:
            print(f"Socket error: {e}")
            self.retry_connection()

    def receive_frames(self):
        try:
            while self.is_running:
                image_len = struct.unpack('<L', self.connection.read(struct.calcsize('<L')))[0]
                if not image_len:
                    break
                # 이미지 데이터 수신
                image_stream = self.connection.read(image_len)
                qimage = QImage.fromData(image_stream)
                self.frame_received.emit(qimage)

                if self.video_writer is not None:
                    frame = cv2.imdecode(np.frombuffer(image_stream, np.uint8), cv2.IMREAD_COLOR)
                    self.video_writer.write(frame)

        except (ConnectionError, pickle.UnpicklingError) as e:
            print(f"Error receiving frames: {e}")
            self.retry_connection()

    def send_data(self, data):
        try:
            self.client_socket.sendall(data)
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
            print("Socket Close Completed!!")
        self.connection_status.emit(False)
        print("Thread Exit Completed!!")
          

    def retry_connection(self):
        self.client_socket = None
        self.connection_status.emit(False)

        self.quit()
        self.wait()




Constants1 = namedtuple('Constants1', ['USER_UI', 'DEVELOP_UI'])
constants1 = Constants1(0,1)

from_class = uic.loadUiType('/home/jeback/dev_ws/iot_project/iot-repo-6/pyqt/ui/iot_project.ui')[0]

class Windowclass(QMainWindow, from_class):
    def __init__(self):

        super().__init__()
        self.setupUi(self)

        self.ModePage.clicked.connect(self.switchUI)
        # Set the initial UI
        self.stackedUI.setCurrentIndex(constants1.USER_UI)
        self.m_UserPage = self.stackedUI.widget(constants1.USER_UI)
        self.m_DevelopPage = self.stackedUI.widget(constants1.DEVELOP_UI)     

        self.m_ComStatusImg  = self.m_UserPage.findChild(QLabel, "ComStatusImg")
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

        
        self.m_ManualBtn.clicked.connect(self.clickedManualBtn)
        self.m_RecBtn.clicked.connect(self.clickedRecordBtn)
        self.m_MoveBar.valueChanged.connect(self.updateMotorValue)

        self.m_MoveBar.setEnabled(False)
        self.m_ManualBtn.setEnabled(False)
        self.m_ManualBtn.setStyleSheet('background-color:gray; color : black; border-radius : 8px;')
        self.m_RecBtn.setEnabled(False)
        self.m_RecBtn.setStyleSheet('background-color:gray; color : black; border-radius : 8px;')
        
        self.m_ComStatus.setText("TCP / IP Not connected")
        self.m_StreamBtn.clicked.connect(self.clickedStreamBtn)

        self.m_MinValue.setText("MinValue : {}".format(self.m_MoveBar.minimum()))
        self.m_MaxValue.setText("MaxValue : {}".format(self.m_MoveBar.maximum()))
        self.m_MidValue.setText("MidValue : 0")

        self.m_isStreamOn = False  # Stream On Off 반전 시킬 용도로만 사용됨. 
        self.m_isManualModeOn = False # Manual Mode On Off 반전 시킬 용도로 사용됨.
        self.m_isRecordOn = False #Record On Off 반전 시킬 용도로 사용됨 . 
        self.m_image_receiver = None # Image receive Thread 생성될 변수
        self.m_SliderValueInitFlag = False# Auto Mode <=> Manual Mode 상호 변경 시, 알려주는 명령 커맨드 

        self.updateMotorValue(self.m_MoveBar.value())

        self.m_FrameImg = QPixmap()  # QLabel 에 카메라에서 넘어온 이미지 프레임 띄울 때 쓰는 변수
        self.m_disconnectImg = QPixmap('/home/jeback/dev_ws/iot_project/iot-repo-6/pyqt/img/disconnect.png')
        self.m_connectImg = QPixmap('/home/jeback/dev_ws/iot_project/iot-repo-6/pyqt/img/connect.png') 
        self.m_videoImg = QPixmap('/home/jeback/dev_ws/iot_project/iot-repo-6/pyqt/img/video.png')

    def switchUI(self):
        current_index = self.stackedUI.currentIndex()

        if current_index == constants1.USER_UI:
            self.stackedUI.setCurrentIndex(constants1.DEVELOP_UI)
            self.ModePage.setText('User Page')            
        else: # current_index == constants.DEVELOP_UI:
            self.stackedUI.setCurrentIndex(constants1.USER_UI)
            self.ModePage.setText('Developer Page')            

    def clickedStreamBtn(self):        
        if self.m_isStreamOn == False:  
            self.start_stream()
            self.m_StreamBtn.setText("Stream OFF")
            self.m_StreamBtn.setStyleSheet('background-color: rgb(237, 51, 59); color : black; border-radius : 8px;')
            self.m_isStreamOn = True            
        else: # self.m_isStreamOn == True: 
            self.stop_stream()
            self.m_StreamBtn.setText("Stream ON")
            self.m_StreamBtn.setStyleSheet('background-color:rgba(80, 188, 223, 0.5); color : black; border-radius : 8px;')
            self.m_isStreamOn = False
    
    def clickedManualBtn(self):
        if self.m_isManualModeOn == False:
            self.m_ManualBtn.setText("OFF")
            self.m_ManualBtn.setStyleSheet('background-color: rgb(237, 51, 59); color : black; border-radius : 8px;')
            self.m_isManualModeOn = True
            # DB에서 마지막 모터값을 받아오는 코드 적용 해야함. 
            self.m_MoveBar.setEnabled(True)
            Command = 'GRM'
            checksum = 0
            checksum = checksum.to_bytes(1, byteorder='big')
            DataPacket = Command.encode() + checksum + checksum + b'\n'
            self.send_command(DataPacket)
        else: # self.m_isManualModeOn == True:
            self.m_ManualBtn.setText("ON")
            self.m_ManualBtn.setStyleSheet('background-color:rgba(80, 188, 223, 0.5); color : black; border-radius : 8px;')
            self.m_isManualModeOn = False
            self.m_MoveBar.setEnabled(False)
            Command = 'GRA'
            DataPacket = Command.encode() + b'\n'
            self.send_command(DataPacket)


    def clickedRecordBtn(self):
        if self.m_isManualModeOn == True:
            if self.m_isRecordOn == False:
                self.m_RecBtn.setText("OFF")
                self.m_RecBtn.setStyleSheet('background-color: rgb(237, 51, 59); color : black; border-radius : 8px;')
                self.m_isRecordOn = True
                self.start_recording()
            else: # self.m_isRecordOn == True:
                self.m_RecBtn.setText("ON") 
                self.m_RecBtn.setStyleSheet('background-color:rgba(80, 188, 223, 0.5); color : black; border-radius : 8px;')
                self.m_isRecordOn = False
                self.stop_recording()
        else: # self.m_isManualModeOn == False:
            QMessageBox.warning(self, 'Recording - Warning', 'Manual Mode Not Activated. \nPlease Activate Manual Mode!')

    def updateMotorValue(self, value):        
        if not self.m_SliderValueInitFlag:
            self.m_MotorValue.setText(f'Motor Angle : {value}')     
            self.m_SliderValueInitFlag = True  
        else:
            self.m_MotorValue.setText(f'Motor Angle : {value}')
            Command = "GRM" # GUI -> RAS Manual Mode 전송 
            MotorValue = (value + 90)
            MotorValue &= 0xFF
            if MotorValue != 0:
                checksum = (~MotorValue & 0xFF) + 1
                checksum = checksum.to_bytes(1, byteorder='big')
            else:
                checksum = 0
            
            MotorValue = MotorValue.to_bytes(1, byteorder='big')
            EndData = b'\n'
            
            DataPacket = Command.encode() + MotorValue + checksum + EndData
            self.m_image_receiver.send_data(DataPacket)
            
    def start_stream(self):
        if self.m_image_receiver and self.m_image_receiver.isRunning():
            return

        # 서버 IP와 포트 번호 설정
        server_ip = '192.168.219.16' 
        server_port = 9999

        # 이미지 수신 스레드 생성 및 시작
        self.m_image_receiver = Communicator(server_ip, server_port)
        self.m_image_receiver.frame_received.connect(self.update_image)
        self.m_image_receiver.connection_status.connect(self.update_status)
        self.m_image_receiver.start()

    def stop_stream(self):
        if self.m_image_receiver:
            self.m_image_receiver.stop()
            self.m_image_receiver = None
            # self.m_ComStatus.setText('TCP/IP Not connected')

    def update_image(self, q_img):
        self.m_FrameImg = self.m_FrameImg.fromImage(q_img)
        self.m_FrameImg = self.m_FrameImg.scaled(self.m_DisplayFrame.width(), self.m_DisplayFrame.height())
        self.m_DisplayFrame.setPixmap(self.m_FrameImg)
    
    def start_recording(self):
        now = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = now + '.avi'
        file_path = '/home/jeback/dev_ws/iot_project/iot-repo-6/pyqt/record{0}'.format(filename)
        self.m_image_receiver.start_recording(file_path)

    def stop_recording(self):
        self.m_image_receiver.stop_recording()

    def update_status(self, status):
        if status:
            self.m_ComStatus.setText('TCP / IP Connected')
            self.m_ComStatusImg.clear()
            self.m_DisplayFrame.clear()
            ScaledConnectImg = self.m_connectImg.scaled(self.m_ComStatusImg.size(), Qt.KeepAspectRatio)           
            self.m_ComStatusImg.setPixmap(ScaledConnectImg)
            self.m_ManualBtn.setEnabled(True)
            self.m_ManualBtn.setStyleSheet('background-color:rgba(80, 188, 223, 0.5); color : black; border-radius : 8px;')
            self.m_RecBtn.setEnabled(True)
            self.m_RecBtn.setStyleSheet('background-color:rgba(80, 188, 223, 0.5); color : black; border-radius : 8px;')
            if self.m_isManualModeOn == True:
                self.m_MoveBar.setEnabled(True)
        else:
            self.m_ComStatus.setText('TCP / IP Not connected')
            self.m_ComStatusImg.clear()
            self.m_DisplayFrame.clear()
            ScaledDisConnectImg = self.m_disconnectImg.scaled(self.m_ComStatusImg.size(), Qt.KeepAspectRatio)           
            self.m_ComStatusImg.setPixmap(ScaledDisConnectImg)
            ScaledVideoImg = self.m_videoImg.scaled(self.m_DisplayFrame.size(), Qt.KeepAspectRatio)
            self.m_DisplayFrame.setPixmap(ScaledVideoImg)
            self.m_ManualBtn.setEnabled(False)
            self.m_ManualBtn.setStyleSheet('background-color: gray; color : black; border-radius : 8px;')
            self.m_MoveBar.setEnabled(False)
            self.m_RecBtn.setEnabled(False)            
            self.m_RecBtn.setStyleSheet('background-color: gray; color : black; border-radius : 8px;')
            if self.m_isRecordOn == True:
                self.stop_recording()
                self.m_RecBtn.setText("OFF")
                self.m_isRecordOn = False

    def send_command(self, DataPacket):
        if self.m_image_receiver:
            self.m_image_receiver.send_data(DataPacket)

    def closeEvent(self, event):
        self.stop_stream()
        event.accept()
        



if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindows = Windowclass()
    myWindows.show()
    sys.exit(app.exec_())