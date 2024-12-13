#define SOUND_SENSOR_1 A0
#define SOUND_SENSOR_2 A1
#define SOUND_SENSOR_3 A2

void setup() {
    Serial.begin(115200);

    // 소리 센서 핀 설정
    pinMode(SOUND_SENSOR_1, INPUT);
    pinMode(SOUND_SENSOR_2, INPUT);
    pinMode(SOUND_SENSOR_3, INPUT);
}

void loop() {
    // 각 소리 센서에서 값을 읽어오기
    int sound1_value = analogRead(SOUND_SENSOR_1);
    int sound2_value = analogRead(SOUND_SENSOR_2);
    int sound3_value = analogRead(SOUND_SENSOR_3);

    // 읽은 값을 시리얼 모니터에 출력
    Serial.print("Sound Sensor 1: "); Serial.print(sound1_value);
    Serial.print("\tSound Sensor 2: "); Serial.print(sound2_value);
    Serial.print("\tSound Sensor 3: "); Serial.println(sound3_value);

    delay(100); // 100ms 간격으로 데이터 출력
}
