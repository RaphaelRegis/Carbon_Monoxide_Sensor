#include <MQUnifiedsensor.h>

// Configuração do hardware
#define BOARD "ESP-32"
#define PIN_ANALOG 34
#define VOLTAGE_RESOLUTION 3.3
#define ADC_BIT_RESOLUTION 12
#define RATIO_MQ7_CLEAN_AIR 27.0  // valor típico (pode ajustar)

MQUnifiedsensor MQ7(BOARD, VOLTAGE_RESOLUTION, ADC_BIT_RESOLUTION, PIN_ANALOG, "MQ-7");

void setup() {
  Serial.begin(115200);

  // Configurações iniciais
  MQ7.setRegressionMethod(1);   // método de regressão 1 = exponencial
  MQ7.setA(99.042);             // parâmetros da curva padrão da biblioteca
  MQ7.setB(-1.518);             // curva para CO
  MQ7.init();
  
  Serial.println("Calibrando... Aguarde 5 segundos");
  float calcR0 = 0;
  for(int i = 0; i < 50; i++) {
    MQ7.update();
    calcR0 += MQ7.calibrate(RATIO_MQ7_CLEAN_AIR);
    delay(100);
  }
  MQ7.setR0(calcR0 / 50);

  Serial.print("R0 = ");
  Serial.println(MQ7.getR0());

  if (isnan(MQ7.getR0())) {
    Serial.println("Falha ao calibrar o sensor!");
    while(1);
  }

  Serial.println("Calibração concluída!");
}

void loop() {
  MQ7.update();                // atualiza leitura ADC
  float CO_ppm = MQ7.readSensor();  // lê CO estimado em ppm

  Serial.print("CO estimado: ");
  Serial.print(CO_ppm);
  Serial.println(" ppm");

  delay(1000);
}
