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
    def __init__(self, End, socket):
        Msg = b''

        while End not in Msg:
            Msg += socket.recv()
        
        if Msg != b'':
            Start = Msg[:3].decode()
            Msg = Msg[3:-len(End)]

            if Start == "GRA":
                SendStart = b"RAA"
                SendPacket = SendStart + End
                print(SendPacket.decode())

            elif Msg == "GRM":
                Data = Msg[:-1]
                DataSum = sum(Msg)
                DataSum &= 0xFF

                if DataSum == 0x00:
                    SendStart = b'RAM'
                    checksum = Data & 0xFF
                    checksum = (~checksum & 0xFF) + 1
                    SendPacket = SendStart + Data + checksum + End
                    print(SendPacket.decode())



if __name__ == "__main__":
    EndMarker = b'\n'
    ServerAddress = "192.168.0.13"
    ServerPort = 9999
    ClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ClientSocket.connect((ServerAddress, ServerPort))

    cam_thread = Thread(target=Cam(ClientSocket))
    manual_thread = Thread(target=Manual(EndMarker, ClientSocket))
    cam_thread.start()
    manual_thread.start()