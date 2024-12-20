#include <NewPing.h>
#include <Servo.h>

// 소리 센서 핀 설정
const int soundSensor1Pin = A0;
const int soundSensor2Pin = A1;
const int soundSensor3Pin = A2;

// 초음파 센서 핀 설정
const int triggerPin1 = 4;
const int echoPin1 = 8;
const int triggerPin2 = 9;
const int echoPin2 = 10;
const int maxDistance = 40;  // 초음파 센서의 최대 거리(cm)

NewPing sonar1(triggerPin1, echoPin1, maxDistance);
NewPing sonar2(triggerPin2, echoPin2, maxDistance);

Servo motor;  // 서보 모터 객체 생성

// 모터 핀 설정
const int motorPin = 3;

// 오프셋 저장 변수
const float sound1_offset = 80.8053;
const float sound2_offset = 48.9360;
const float sound3_offset = 86.5220;

// 필터링된 값 저장 변수
float filtered_sound1 = 0;
float filtered_sound2 = 0;
float filtered_sound3 = 0;

// 상보 필터 상태 변수
float sound1_filter_state = 0;
float sound2_filter_state = 0;
float sound3_filter_state = 0;

unsigned long t_start = 0;

// 소리 감지 임계값
const int soundThreshold = 10;

// grid sxale = 5cm
const float gridScale = 5.0;  

// 모터 위치 (cm 단위)
const float motorX = 6.0 * gridScale;  // 모터의 X 좌표 (30cm)
const float motorY = 0.0 * gridScale;  // 모터의 Y 좌표 (0cm)

// 소리 센서 위치 (cm 단위)
const float sensor1_x = 0.0 * gridScale;  // 0 cm
const float sensor1_y = 4.0 * gridScale;  // 20 cm
const float sensor2_x = 6.0 * gridScale;  // 30 cm
const float sensor2_y = 8.0 * gridScale;  // 40 cm
const float sensor3_x = 12.0 * gridScale; // 60 cm
const float sensor3_y = 4.0 * gridScale;  // 20 cm

// 초음파 센서 위치 (cm 단위)
const float ultrasonic1_x = 3.0 * gridScale;  // 15cm
const float ultrasonic1_y = 8.0 * gridScale;  // 40cm
const float ultrasonic2_x = 9.0 * gridScale;  // 45cm
const float ultrasonic2_y = 8.0 * gridScale;  // 40cm

//********** Function declaration code **********//

// 2차적 필터: 상보 필터 적용
float applyComplementaryFilter(int raw_value, float &filter_state) 
{
    float A = 0.8182;
    float B = 0.0091;
    float C = 1;
    float D = 0;

    float x = filter_state;
    float y = C * x + D * raw_value;
    filter_state = A * x + B * raw_value;
    
    return y;
}

// 패킷으로 데이터를 전송하는 함수
void sendPacket(char sensorType, float sound1, float sound2, float sound3, int distance1, int distance2, uint8_t motorValue) 
{   
    uint8_t packet[29]; // 패킷을 위한 배열 (ARA + 타입 + 센서 데이터 + 체크섬 + '\n' 포함)
    uint8_t checksum = 0;

    // 패킷 시작 ('ARA')
    packet[0] = 'A';
    packet[1] = 'R';
    packet[2] = 'A';

    // 센서 타입 ('S' 또는 'U')
    packet[3] = sensorType;

    // 소리 센서 데이터 시작 ('S')
    packet[4] = 'S';

    // 소리 센서 데이터를 고정 소수점으로 변환하여 패킷에 추가
    uint32_t sound1_fixed = convertToFixedPoint(sound1);
    uint32_t sound2_fixed = convertToFixedPoint(sound2);
    uint32_t sound3_fixed = convertToFixedPoint(sound3);
    
    packet[5] = (sound1_fixed >> 24) & 0xFF;
    packet[6] = (sound1_fixed >> 16) & 0xFF;
    packet[7] = (sound1_fixed >> 8) & 0xFF;
    packet[8] = sound1_fixed & 0xFF;
    packet[9] = (sound2_fixed >> 24) & 0xFF;
    packet[10] = (sound2_fixed >> 16) & 0xFF;
    packet[11] = (sound2_fixed >> 8) & 0xFF;
    packet[12] = sound2_fixed & 0xFF;
    packet[13] = (sound3_fixed >> 24) & 0xFF;
    packet[14] = (sound3_fixed >> 16) & 0xFF;
    packet[15] = (sound3_fixed >> 8) & 0xFF;
    packet[16] = sound3_fixed & 0xFF;

    // 초음파 센서 데이터 시작 ('U')
    packet[17] = 'U';
    packet[18] = (distance1 >> 8) & 0xFF;
    packet[19] = distance1 & 0xFF;
    packet[20] = (distance2 >> 8) & 0xFF;
    packet[21] = distance2 & 0xFF;

    // 모터 데이터 시작 ('M')
    packet[22] = 'M';
    packet[23] = motorValue;

    checksum = packet[5]+packet[6]+packet[7]+packet[8]+packet[9]+packet[10]+packet[11]+packet[12]+packet[13]+packet[14]+packet[15]+packet[16]+packet[18]+packet[19]+packet[20]+packet[21]+packet[23];

    checksum = sensor_calculateChecksum(checksum);
    packet[24] = checksum;

    // 패킷 끝에 '\n' 추가
    packet[25] = '\n';

    Serial.write(packet, 26); // 26바이트 패킷 전송 (\n 포함)
}

// 소리센서 값을 고정 소수점으로 변환하는 함수
uint32_t convertToFixedPoint(float value) 
{
    return (uint32_t)(value * 10000); // 소수점 4자리까지 고정 소수점으로 변환
}

// sensor check sum 계산 함수
uint8_t sensor_calculateChecksum(uint8_t checksum) 
{   
    checksum = checksum & 0xFF;
    checksum = ~checksum + 1;

    return checksum;
}

// 초음파 센서로 좌표 계산하는 함수
void calculateUltrasonicCoordinates(int d1, int d2, float &x, float &y) 
{
    if (d1 < d2) 
    {
        x = ultrasonic1_x;
        y = ultrasonic1_y - d1; // 거리가 멀어질수록 y축 값이 작아짐
    } 
    else 
    {
        x = ultrasonic2_x;
        y = ultrasonic2_y - d2; // 거리가 멀어질수록 y축 값이 작아짐
    }

    x = round(x / 5.0) * 5;
    y = round(y / 5.0) * 5;

    if (y < 0) 
    {
        y = 0;
    }
}

// 모터 각도 계산 함수
int calculateMotorAngle(float x, float y) 
{
    float deltaX = x - motorX;
    float deltaY = y - motorY;

    float angleRadians = atan2(deltaY, deltaX);
    int angleDegrees = angleRadians * 180 / PI;

    angleDegrees = 180 - angleDegrees;

    int constrainedAngle = constrain(angleDegrees, 20, 160);

    return constrainedAngle;
}

// 초음파 센서를 읽고 모터를 제어하는 함수
void readUltrasonicSensorsAndControlMotor() 
{
    int distance1 = sonar1.ping_cm();
    int distance2 = sonar2.ping_cm();

    float x = 0, y = 0;

    calculateUltrasonicCoordinates(distance1, distance2, x, y);

    int motorAngle = calculateMotorAngle(x, y);
    motor.write(motorAngle);
}

// 소리 센서 중 가장 큰 값을 가진 센서의 좌표로 모터 각도를 계산하는 함수
int calculateMotorAngleFromMaxSensor() 
{
    // 가장 큰 소리 값을 가진 센서를 찾음
    float max_value = max(filtered_sound1, max(filtered_sound2, filtered_sound3));
    float target_x, target_y;

    if (max_value == filtered_sound1) 
    {
        target_x = sensor1_x;
        target_y = sensor1_y;
    } 
    else if (max_value == filtered_sound2) 
    {
        target_x = sensor2_x;
        target_y = sensor2_y;
    } 
    else 
    {
        target_x = sensor3_x;
        target_y = sensor3_y;
    }

    // 목표 좌표와 서보 모터 위치 사이의 차이 계산
    float deltaX = target_x - motorX;
    float deltaY = target_y - motorY;

    // atan2 함수로 라디안 단위의 각도 계산
    float angleRadians = atan2(deltaY, deltaX);

    // 라디안을 도 단위로 변환
    int angleDegrees = angleRadians * 180 / PI;

    // 시계 방향으로 회전할 수 있도록 각도 조정
    angleDegrees = 180 - angleDegrees;

    // 서보 모터의 각도를 20도에서 160도 사이로 제한
    int constrainedAngle = constrain(angleDegrees, 20, 160);

    return constrainedAngle;
}

char lastCommand[4] = "RAA";  // 초기 상태를 RAA로 설정

void processReceivedData() 
{
    if (Serial.available() >= 6) 
    {
        char packet[6];
        Serial.readBytes(packet, 6);  // 한 번에 6바이트 읽기

        char byte1 = packet[0];
        char byte2 = packet[1];
        char byte3 = packet[2];
        uint8_t motorValue = packet[3];
        uint8_t receivedChecksum = packet[4];
        char endChar = packet[5];

        if (endChar != '\n') 
        {
            return;  // 패킷이 유효하지 않으면 반환
        }

        String receivedCommand = String(byte1) + String(byte2) + String(byte3);

        if (receivedCommand.equals("RAA")) 
        {
            strcpy(lastCommand, "RAA");  // 명령을 RAA로 설정
        } 
        else if (receivedCommand.equals("RAM")) 
        {
            strcpy(lastCommand, "RAM");  // 명령을 RAM으로 설정

            uint16_t sum = motorValue + receivedChecksum;
            uint8_t calculatedChecksum = sum & 0xFF;

            if (calculatedChecksum == 0x00) 
            {
                int adjustedMotorValue = constrain(motorValue, 20, 160);
                motor.write(adjustedMotorValue);
            } 
            else 
            {
                return;
            }
        }
    }
}

//********** Main code **********//
void setup() 
{
    Serial.begin(115200);

    pinMode(soundSensor1Pin, INPUT);
    pinMode(soundSensor2Pin, INPUT);
    pinMode(soundSensor3Pin, INPUT);

    pinMode(triggerPin1, OUTPUT);
    pinMode(echoPin1, INPUT);
    pinMode(triggerPin2, OUTPUT);
    pinMode(echoPin2, INPUT);

    motor.attach(motorPin);
    motor.write(90);  // 모터를 초기 위치 90도로 설정

    t_start = millis();
}

void loop() 
{
    if (millis() - t_start >= 20) 
    {
        t_start = millis();

        // 소리 센서 값 읽기(소숫점 넷째 자리까지)
        float raw_sound1 = (analogRead(soundSensor1Pin) / 1023.0) * 5.0 - sound1_offset;
        float raw_sound2 = (analogRead(soundSensor2Pin) / 1023.0) * 5.0 - sound2_offset;
        float raw_sound3 = (analogRead(soundSensor3Pin) / 1023.0) * 5.0 - sound3_offset;

        // 상보 필터 적용
        filtered_sound1 = applyComplementaryFilter(raw_sound1, sound1_filter_state);
        filtered_sound2 = applyComplementaryFilter(raw_sound2, sound2_filter_state);
        filtered_sound3 = applyComplementaryFilter(raw_sound3, sound3_filter_state);

        // 초음파 센서 값 읽기
        int distance1 = sonar1.ping_cm();
        int distance2 = sonar2.ping_cm();
        
        // 
        // Serial.print(lastCommand); 
        // 마지막 명령에 따라 모터 제어 수행
        if (strcmp(lastCommand, "RAA") == 0) 
        {
            char sensorType = (filtered_sound1 <= soundThreshold || filtered_sound2 <= soundThreshold || filtered_sound3 <= soundThreshold) ? 'U' : 'S';

            if (sensorType == 'S') 
            {
                int motorAngle = calculateMotorAngleFromMaxSensor();
                motor.write(motorAngle);
            } 
            else if (sensorType == 'U') 
            {
                readUltrasonicSensorsAndControlMotor();
            }

            // 패킷 전송
            sendPacket(sensorType, filtered_sound1, filtered_sound2, filtered_sound3, distance1, distance2, motor.read());
        }

        // 라즈베리파이로부터 데이터 읽기 및 명령 처리
        processReceivedData();
    }
}