% 샘플링 주기 (T) 20ms
T = 0.02;

% 필터 파라미터 설정
alpha = 1;  % 필터의 이득
beta = 10;   % 필터의 컷오프 주파수

% Tustin 변환을 사용하여 이산화
% 연속 시간 도메인에서의 시스템을 샘플링 시간에 맞춰 이산 시스템으로 변환한다.
% ZOH를 사용하여 샘플링 주기 T 동안 입력 신호가 일정하다고 가정하고 변환을 수행한다.
A = (2 - beta * T) / (2 + beta * T);
B = (alpha * T) / (2 + beta * T);
C = 1; 
D = 0;  

% 상태 방정식 계수 출력
disp('State-space matrix A:');
disp(A);

disp('State-space matrix B:');
disp(B);

disp('State-space matrix C:');
disp(C);

disp('State-space matrix D:');
disp(D);
