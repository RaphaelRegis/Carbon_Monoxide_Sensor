// bibliotecas
#include <WiFi.h>
#include <HTTPClient.h>

// variaveis globais
const char* ssid = "nome_rede";
const char* senha = "senha_rede";
const char* serverUrl = "url_do_servidor";
const char* token = "token";

// funcoes auxiliares
void conectarWiFi(char* ssid, char* senha) {
    //implementação da conexão
    WiFi.begin(ssid, senha);

    while (WiFi.status() != WL_CONNECTED) {
        delay(5000);
        Serial.print(".");
    }

    Serial.println("\nWiFi conectado!")

}

int getMedicao() {
    return 0;
}

void enviarMedicao(char* medicao, char* url, char* token) {
    HTTPClient http;

    // inicia a conexao HTTP
    http.begin(serverUrl + "\\" + token);
    // define o tipo de conteudo
    http.addHeader("Content-Type", "application/json");

    // objeto da requisicao
    String jsonData = "{\"medicao\": \"" + medicao + "\"}";

    // envia o POST
    int httpResponseCode = http.POST(jsonData);

    // imprime a resposta
    if (httpResponseCode > 0) {
        Serial.print("Código de resposta: ")
        Serial.println(codigo_resposta);
        String response = http.getString();
        Serial.print("Resposta do servidor: ");
        Serial.println(response);
    } else {
        Serial.print("Erro na requisição: ");
        Serial.println(http.errorToString(httpResponseCode));
    }

    http.end();
}

// funcoes principais
void setup {
    Serial.begin(115200);
    delay(5000);
}

void loop {
    // conecta o WiFi se ele nao estiver conectado
    if (WiFi.status() != WL_CONNECTED) {
        conectarWiFi(ssid, senha);
    }

    // faz a medicao
    int medicao = getMedicao();

    // envia a medicao para o servidor
    enviarMedicao(medicao, url, token);

    // pausa a execucao por 1 hora
    delay(3600000);
}