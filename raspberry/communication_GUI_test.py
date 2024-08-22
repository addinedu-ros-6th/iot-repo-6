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
            socket.close()


class Manual:
    def __init__(self, End, socket):
    # def __init__(self, End, serial, socket):
        while True:
            Msg = b''

            while End not in Msg:
                Msg += socket.recv(1024)

            if Msg != b'':
                print(Msg)
                Msg_len = len(Msg)
                Start = Msg[:3].decode("utf-8")
                Msg = Msg[3:-len(End)]
                print(Start)
                print(Msg)

                if Start == "GRA" and Msg_len == 4:
                    SendStart = b"RAA"
                    SendPacket = SendStart + End
                    print(SendPacket)
                    # serial.write(SendPacket)

                elif Start == "GRM" and Msg_len == 6:
                    Data = Msg[0]
                    checksum = Msg[1]
                    checksum_check = Data + checksum
                    checksum_check &= 0xFF
                    print(checksum_check)

                    if checksum_check == 0x00:
                        SendStart = b'RAM'
                        checksum = (~Data & 0xFF) + 1
                        checksum &= 0xFF
                        print(Data, checksum)
                        SendPacket = SendStart + Data.to_bytes(1, byteorder="big") + checksum.to_bytes(1, byteorder="big") + End
                        # serial.write(SendPacket)
                        print(SendPacket)



if __name__ == "__main__":
    EndMarker = b'\n'
    ServerAddress = "192.168.219.16"
    ServerPort = 9999
    ClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ClientSocket.connect((ServerAddress, ServerPort))

    # ArduinoSerial = serial.Serial("/dev/ttyACM0", 115200, timeout=1)

    cam_thread = Thread(target=lambda: Cam(ClientSocket))
    # manual_thread = Thread(target=lambda: Manual(EndMarker, ArduinoSerial, ClientSocket))
    manual_thread = Thread(target=lambda: Manual(EndMarker, ClientSocket))
    cam_thread.start()
    manual_thread.start()