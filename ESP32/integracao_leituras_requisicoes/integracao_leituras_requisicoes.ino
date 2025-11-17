#include <WiFi.h>
#include <HTTPClient.h>
#include <MQUnifiedsensor.h>


// hardware configurations
#define BOARD "ESP-32"
#define PIN_ANALOG 34
#define VOLTAGE_RESOLUTION 3.3
#define ADC_BIT_RESOLUTION 12
#define RATIO_MQ7_CLEAN_AIR 27.0  // valor típico

// MQ-7 object
MQUnifiedsensor MQ7(BOARD, VOLTAGE_RESOLUTION, ADC_BIT_RESOLUTION, PIN_ANALOG, "MQ-7");

// Wi-Fi and request configs
const char* ssid = "";
const char* password = "";
const char* url = "https://zt31fcny10.execute-api.us-east-2.amazonaws.com/prod";


// device specifications
const String id_sensor = "Centro_Vitoria_da_Conquista_BA_01";
const String region = "Centro_Vitoria_da_Conquista_BA";
const String timezone = "Brazil/East";

void calibrateSensor() {
  Serial.println("Calibrando... Aguarde 5 segundos");
  float calcR0 = 0;
  for (int i = 0; i < 50; i++) {
    MQ7.update();
    calcR0 += MQ7.calibrate(RATIO_MQ7_CLEAN_AIR);
    delay(100);
  }
  MQ7.setR0(calcR0 / 50);

  Serial.print("R0 = ");
  Serial.println(MQ7.getR0());

  if (isnan(MQ7.getR0())) {
    Serial.println("Falha ao calibrar o sensor!");
    while (1)
      ;
  }

  Serial.println("Calibração concluída!");
}


void setupSensor() {

  // Configuration of the PPM mathematical model
  MQ7.setRegressionMethod(1);  // regression method 1 = exponential — _PPM = a * ratio^b
  MQ7.setA(99.042);            // standard curve parameters from the library
  MQ7.setB(-1.518);            // curve to CO

  // Sensor initialization
  MQ7.init();

  // Calibration
  calibrateSensor();
}


void connectWiFi() {
  Serial.println("Conectando ao Wi-Fi...");
  WiFi.begin(ssid, password);  // try to connect to WiFi

  // wait until the wifi connects
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  // prints connection information
  Serial.println("\nConectado ao Wi-Fi!");
  Serial.print("Endereço IP: ");
  Serial.println(WiFi.localIP());
}


String prepareRequestBody(float ppm) {
  String requestBody = "{ ";
  requestBody += "\"id_sensor\": \"" + id_sensor + "\", ";
  requestBody += "\"region\": \"" + region + "\", ";
  requestBody += "\"measurement\": \"" + String(ppm, 1) + "\", ";
  requestBody += "\"timezone\": \"" + timezone + "\" }";

  return requestBody;
}


void sendRequest(String requestBody) {
  HTTPClient http;

  Serial.print("Conectando a: ");
  Serial.println(url);

  http.begin(url);                                     // Start connection
  http.addHeader("Content-Type", "application/json");  // Sets the header for the request

  int httpCode = http.POST(requestBody);  // Make a POST request

  if (httpCode > 0) {
    Serial.printf("Código de resposta: %d\n", httpCode);
    String payload = http.getString();
    Serial.println("Resposta do servidor:");
    Serial.println(payload);
  } else {
    Serial.printf("Erro na requisição: %s\n", http.errorToString(httpCode).c_str());
  }

  http.end();  // Close connection
}


void setup() {
  // start serial monitor
  Serial.begin(115200);
  delay(1500);  // short delay to start up

  // Prepares the sensor
  setupSensor();

  // Connect to Wi-Fi
  connectWiFi();
}


void loop() {

  // Reads the sensor
  MQ7.update();                  // Updates ADC reading
  float ppm = MQ7.readSensor();  // reads estimated CO in PPM

  Serial.print("CO estimado: ");
  Serial.print(CO_ppm);
  Serial.println(" ppm");


  // submit the request
  String requestBody = prepareRequestBody(ppm);

  if (WiFi.status() != WL_CONNECTED) {
    connectWiFi();
  }

  sendRequest(requestBody);


  // Wait 10 minutes to send the next reading
  Serial.println("Aguardando 10min antes do próximo ciclo...");
  delay(600000);
}
