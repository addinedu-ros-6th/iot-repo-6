#define NUM_SAMPLES 4000
#define SOUND_SENSOR_1 A0
#define SOUND_SENSOR_2 A1
#define SOUND_SENSOR_3 A2

// 오프셋 저장 변수
float sound1_offset = 31.2495;
float sound2_offset = 31.5667;
float sound3_offset = 31.5102;

// 필터링된 값 저장 변수
float filtered_sound1 = 0;
float filtered_sound2 = 0;
float filtered_sound3 = 0;

// 상보 필터 상태 변수
float sound1_filter_state = 0;
float sound2_filter_state = 0;
float sound3_filter_state = 0;

unsigned long t_start = 0;

void setup() {
    Serial.begin(115200);

    // 소리 센서 핀 설정
    pinMode(SOUND_SENSOR_1, INPUT);
    pinMode(SOUND_SENSOR_2, INPUT);
    pinMode(SOUND_SENSOR_3, INPUT);

    // 샘플링 주기 타이머 초기화
    t_start = millis();
}

void loop() {
    // 주기적 샘플링 - 0.02초(20ms) 주기
    if (millis() - t_start >= 20) {
        t_start = millis(); // 주기 타이머 초기화

        // 소리 신호의 오프셋을 먼저 제거(1차 필터)
        int raw_sound1 = analogRead(SOUND_SENSOR_1) - sound1_offset;
        int raw_sound2 = analogRead(SOUND_SENSOR_2) - sound2_offset;
        int raw_sound3 = analogRead(SOUND_SENSOR_3) - sound3_offset;

        // 상보 필터 적용(2차 필터)
        filtered_sound1 = applyComplementaryFilter(raw_sound1, sound1_filter_state);
        filtered_sound2 = applyComplementaryFilter(raw_sound2, sound2_filter_state);
        filtered_sound3 = applyComplementaryFilter(raw_sound3, sound3_filter_state);

        // 결과 출력(serial monitor)
        //Serial.print("Filtered Sound1: "); Serial.print(filtered_sound1);
        //Serial.print("\tFiltered Sound2: "); Serial.print(filtered_sound2);
        //Serial.print("\tFiltered Sound3: "); Serial.println(filtered_sound3);

        // 결과 출력(serial plotter)
        Serial.print(filtered_sound1, 4);
        Serial.print("\t");
        Serial.print(filtered_sound2, 4);
        Serial.print("\t");
        Serial.println(filtered_sound3, 4);
    }
}

// 2차적 필터: 상보 필터 적용
float applyComplementaryFilter(int raw_value, float &filter_state) {
    // 매트랩으로 계산된 필터 계수
    float A = 0.8182;
    float B = 0.0091;
    float C = 1;
    float D = 0;

    // 주파수 영역 -> 시간 영역으로 변환(상태 방정식)
    float x = filter_state;
    float y = C * x + D * raw_value;
    filter_state = A * x + B * raw_value;
    
    return y;
}
