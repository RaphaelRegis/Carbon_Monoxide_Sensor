#include <WiFi.h>
#include <HTTPClient.h>

// Configurações da rede Wi-Fi
const char* ssid = "Familia Araujo";
const char* password = "synthwave";

// Definicoes do dispositivo
const String id_sensor = "Centro_Vitoria_da_Conquista_BA_01";
const String region = "Centro_Vitoria_da_Conquista_BA";
const String timezone = "Brazil/East";

void connectWiFi() {
  Serial.println("Conectando ao Wi-Fi...");
  WiFi.begin(ssid, password);  // tenta conectar ao WiFi

  // espera ate o wifi conectar
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  // imprime informacoes da conexao
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
    String url = "https://zt31fcny10.execute-api.us-east-2.amazonaws.com/prod";

    Serial.print("Conectando a: ");
    Serial.println(url);

    http.begin(url);            // Inicia conexao
    http.addHeader("Content-Type", "application/json"); // define o header para a requisicao

    int httpCode = http.POST(requestBody);  // Faz requisição GET

    if (httpCode > 0) {
      Serial.printf("Código de resposta: %d\n", httpCode);
      String payload = http.getString();
      Serial.println("Resposta do servidor:");
      Serial.println(payload);
    } else {
      Serial.printf("Erro na requisição: %s\n", http.errorToString(httpCode).c_str());
    }

    http.end();  // Fecha conexão

}


void setup() {

  Serial.begin(115200);  // permite imprimir coisas num consonle
  delay(1000);           // pequeno atraso para inicializar

  // Conectando ao Wi-Fi
  connectWiFi();

  String requestBody = prepareRequestBody(45.3); // prepara o corpo da requisicao

  
  Serial.println("Resultado:");
  Serial.println(requestBody);
  sendRequest(requestBody); // faz a requisicao

}


void loop() {
  // fazendo a requisicao
  // if (WiFi.status() == WL_CONNECTED) { // caso esteja conectado ao WiFi, tenta fazer a requisicao
  //   sendRequest();

  // } else { // caso contrario, tenta reconectar
  //   connectWiFi();

  // }

  // delay(5000); // delay de 5 segundos
}