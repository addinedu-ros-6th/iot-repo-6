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
    def __init__(self, End, serial, socket):
        while True:
            Msg = b''

            while End not in Msg:
                Msg += socket.recv(1024)

            if Msg != b'':
                Msg_len = len(Msg)
                Start = Msg[:3].decode("utf-8")
                Msg = Msg[3:-len(End)]
                print(Start)
                print(Msg)

                if Start == "GRA" and Msg_len == 4:
                    SendStart = b"RAA"
                    SendPacket = SendStart + End
                    print(SendPacket)
                    serial.write(SendPacket)

                elif Start == "GRM" and Msg_len == 5:
                    Data = Msg[0]
                    checksum = Msg[1]
                    DataSum = Data + checksum
                    DataSum &= 0xFF
                    print(DataSum)

                    if DataSum == 0x00:
                        SendStart = b'RAM'
                        checksum = Data & 0xFF
                        checksum = (~checksum & 0xFF) + 1
                        SendPacket = SendStart + Data.to_bytes(1, byteorder="big") + checksum.to_bytes(1, byteorder="big") + End
                        serial.write(SendPacket)
                        print(SendPacket)



class DataUpload:
    def __init__(self, End, serial, cursor):
        while True:
            msg = b''
            while End not in msg:
                msg += serial.read()

            print("receive:", msg)

            if msg != b'':
                start = msg[:3]
                print(start)
                if start == b'ARA' and len(msg) == 26:
                    start = start.decode()
                    msg = msg[3:-len(End)]
                    print("cut start, end:", msg)
                    if start == "ARA":
                        control = msg[0].to_bytes(1, byteorder = 'big').decode()
                        print(control)
                        sound_check = msg[1]
                        sound = msg[2:14]
                        ultra_check = msg[14]
                        ultra = msg[15:19]
                        motor_check = msg[19]
                        motor = msg[20:21]
                        checksum = msg[-1].to_bytes(1, byteorder = 'big')
                        if sound_check.to_bytes(1, byteorder = 'big').decode() == 'S' and ultra_check.to_bytes(1, byteorder = 'big').decode() == 'U' and motor_check.to_bytes(1, byteorder = 'big').decode() == 'M':
                            checksum_check = 0
                            for i in [sound, ultra, motor, checksum]:
                                for j in i:
                                    checksum_check += j
                            print("checksum:", checksum)
                            print("checksum_check:", checksum_check)
                            print("checksum_check byte:", checksum_check.to_bytes(2, byteorder="big"))
                            checksum_check &= 0xFF
                            print("checksum_check cal:", checksum_check)
                            if checksum_check == 0x00:
                                sound1 = msg[2:6]
                                sound2 = msg[6:10]
                                sound3 = msg[10:14]
                                sound1_de = int.from_bytes(sound1, byteorder="big")
                                sound2_de = int.from_bytes(sound2, byteorder="big")
                                sound3_de = int.from_bytes(sound3, byteorder="big")
                                print("sound1:", sound1_de/10000, "sound2:", sound2_de/10000, "sound3:", sound3_de/10000)
                                ultra1 = msg[15:17]
                                ultra2 = msg[17:19]
                                ultra2_de = int.from_bytes(ultra2, byteorder="big")
                                ultra1_de = int.from_bytes(ultra1, byteorder="big")
                                print("ultra1:",ultra1_de, "ultra2:", ultra2_de)
                                motor = msg[20:21]
                                print("motor:", motor)

                                checksum = msg[-1]
                                print("checksum:", checksum, type(checksum))
                                print("upload SQL")
                                #sql = """insert into (tableName) values()"""



if __name__ == "__main__":
    EndMarker = b'\n'
    ServerAddress = "192.168.0.140"
    ServerPort = 9998
    ClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ClientSocket.connect((ServerAddress, ServerPort))
    ArduinoSerial = serial.Serial("/dev/ttyACM0", 115200, timeout=1)
    # db = mysql.connector.connect(
    #     host = "addinedu-database.ctw06kigusdq.ap-northeast-2.rds.amazonaws.com",
    #     port = "3306",
    #     user = "",
    #     password = "",
    #     database = ""
    # )
    # db_cursor = db.cursor(buffered=True)

    cam_thread = Thread(target=Cam(ClientSocket))
    manual_thread = Thread(target=Manual(EndMarker, ArduinoSerial, ClientSocket))
    dataUpload_thread = Thread(target=DataUpload(EndMarker, ArduinoSerial))
    cam_thread.start()
    manual_thread.start()
    dataUpload_thread.start()