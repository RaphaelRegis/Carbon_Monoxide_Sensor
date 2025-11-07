#include <WiFi.h>
#include <HTTPClient.h>

// Configurações da rede Wi-Fi
const char* ssid = "Familia Araujo";
const char* password = "synthwave";

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


void sendRequest() {
    HTTPClient http;
    String url = "http://minhaUrl/minhaApi";  // Exemplo de URL

    Serial.print("Conectando a: ");
    Serial.println(url);

    http.begin(url);            // Inicia conexão
    int httpCode = http.GET();  // Faz requisição GET

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

}


void loop() {
  // fazendo a requisicao
  if (WiFi.status() == WL_CONNECTED) { // caso esteja conectado ao WiFi, tenta fazer a requisicao
    sendRequest();

  } else { // caso contrario, tenta reconectar
    connectWiFi();

  }

  delay(5000); // delay de 5 segundos
}