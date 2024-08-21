import io, socket, struct, time, picamera, serial, mysql.connector
from threading import Thread



class Cam:
    def __init__(self, socket):
        Connection = socket.makefile('wb')
        try:
            with picamera.PiCamera() as Camera:
                Camera.resolution = (640, 480) # 해상도 설정
                Camera.framerate = 24 # 프레임 레이트 설정
                Camera.vflip = True
                time.sleep(2) # 초기화 시간 설정
                Start = time.time()
                Stream = io.BytesIO()

                for _ in Camera.capture_continuous(Stream, 'jpeg', use_video_port=True):
                    Connection.write(struct.pack('<L', Stream.tell()))
                    Connection.flush()
                    Stream.seek(0)
                    Connection.write(Stream.read())
                    Stream.seek(0)
                    Stream.truncate()
                    Connection.write(struct.pack('<L', 0))
        finally:
            Connection.close()
            socket.connect()



class Manual:
    def __init__(self, socket):
        EndMarker = b'\n'
        EndMarkerLength = len(EndMarker)
        Msg = b''

        while EndMarker not in Msg:
            Msg += socket.recv(1024)
        
        if Msg != b'':
            Start = Msg[:3].decode()
            Msg = Msg[3:-EndMarkerLength]

            if Start == "GRA":
                SendStart = b"RAA"
                Send = SendStart + EndMarker
                # serial Send

            elif Msg == "GRM":
                Data = Msg[:-1]
                DataSum = sum(Msg)
                DataSum &= 0xFF

                if DataSum == 0x00:
                    SendPacket = b'RAM' + Data + EndMarker
                    # serial SendPacket



class DataUpload:
    def __init__(self):
        # serial accept
        # packet 
        # sound_sensor_data = Msg[0:5]
        # ultraSoundSensorData = Msg[]
        # motor_data = Msg[]

        # if Start == "ARA":
            # if checksum == 0:
                # upload mysql



if __name__ == "__main__":
    server_address = "192.168.0.13"
    server_port = 9999
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_address, server_port))
    db = mysql.connector.connect(
        host = "",
        user = "",
        password = "",
        database = ""
    )

    # cam(client_socket)
    
    # multi thread
    # thread1    cam()
    # thread2    manual()
    # thread3    data_upload()