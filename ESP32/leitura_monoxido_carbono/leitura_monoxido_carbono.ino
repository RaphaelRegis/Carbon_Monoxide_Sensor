#include <MQUnifiedsensor.h>

// Sensor MQ-7
#define SENSOR_PLACA "ESP-32"
#define SENSOR_VOLTAGE_RESOLUTION 3.3
#define SENSOR_ANALOG_PIN 32
#define SENSOR_TYPE "MQ-7"
#define SENSOR_ADC_RESOLUTION 12
#define SENSOR_CLEAN_AIR_RATIO 27.5
#define SENSOR_PWM_PIN 5

// Intervalos de tempo para ciclos de aquecimento e leitura
const unsigned long HEATING_HIGH_DURATION = 60 * 1000;  // 60 segundos em 5V
const unsigned long HEATING_LOW_DURATION = 90 * 1000;   // 90 segundos em 1.4V
const unsigned long CYCLE_WAIT_DURATION   = 450 * 1000; // 7min30s entre ciclos

// Objetos globais
MQUnifiedsensor MQ7(SENSOR_PLACA, SENSOR_VOLTAGE_RESOLUTION, SENSOR_ADC_RESOLUTION, SENSOR_ANALOG_PIN, SENSOR_TYPE);

void calibrateSensor() {
  Serial.print("Calibrando sensor MQ-7... ");
  
  float calcR0 = 0;
  for(int i = 1; i <= 10; i++) {
    MQ7.update();
    calcR0 += MQ7.calibrate(SENSOR_CLEAN_AIR_RATIO);
    Serial.print(".");
  }
  
  MQ7.setR0(calcR0 / 10.0);
  Serial.println(" Concluído!");

  // Verificações de erro na calibração
  if (isinf(calcR0)) {
    Serial.println("Erro: Circuito aberto! Verifique o cabeamento.");
    while(1);
  }
  
  if (calcR0 == 0) {
    Serial.println("Erro: Curto-circuito no pino analógico!");
    while(1);
  }
}


void setupSensor() {
  // Configuração do modelo matemático de PPM
  MQ7.setRegressionMethod(1); // _PPM = a * ratio^b
  MQ7.setA(99.042);
  MQ7.setB(-1.518);

  // Inicialização do sensor
  MQ7.init();
  pinMode(SENSOR_PWM_PIN, OUTPUT);

  // Calibração
  calibrateSensor();
}


void setup() {
  Serial.begin(115200);
  setupSensor();
}

void loop() {
  // Ciclo de 60s com 3.3V (aquecimento)
  Serial.println("Iniciando aquecimento alto (3.3V)...");
  analogWrite(SENSOR_PWM_PIN, 255);
  delay(HEATING_HIGH_DURATION);

  // Ciclo de 90s com 1.4V (medição)
  Serial.println("Reduzindo para baixa tensão (1.4V)...");
  analogWrite(SENSOR_PWM_PIN, 20);
  delay(HEATING_LOW_DURATION);

  // Leitura do sensor
  MQ7.update();
  float ppm = MQ7.readSensor();

  Serial.print("Leitura de CO: ");
  Serial.print(ppm);
  Serial.println(" ppm");


  // Espera 7min30s antes de repetir para completar ciclo de 10 minutos
  Serial.println("Aguardando 7min30s antes do próximo ciclo...");
  delay(CYCLE_WAIT_DURATION);
}