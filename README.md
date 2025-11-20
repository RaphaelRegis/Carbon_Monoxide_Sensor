# Sistema de Monitoramento Híbrido de Monóxido de Carbono (CO)

Este projeto apresenta um sistema híbrido (on-premises / nuvem) desenvolvido para monitoramento de monóxido de carbono. A solução combina um módulo físico capaz de realizar leituras locais com uma arquitetura em nuvem responsável por recepção, processamento, armazenamento e distribuição de notificações.

Na parte física, foram utilizados **ESP32** e **sensor MQ-7** para coleta dos dados ambientais.
Na camada de nuvem, o projeto integra diversos serviços da AWS, incluindo **Amazon API Gateway**, **AWS Lambda**, **Amazon DynamoDB**, **Amazon EventBridge**, **Amazon SQS** e **Amazon CloudWatch**.

---

## ⚙️ Funções do Projeto

### **Lambda: Save_Newer_Readings**

A função Save_Newer_Readings tem como propósito registrar no banco de dados as leituras de monóxido de carbono enviadas pelo hardware. Ela atua como o primeiro ponto de processamento dentro da arquitetura em nuvem e é acionada automaticamente sempre que a API desenvolvida no Amazon API Gateway recebe uma requisição do tipo POST, garantindo que todas as medições sejam devidamente capturadas e organizadas. 

### **Lambda: Save_Average_Readings**

A função Save_Average_Readings tem como objetivo agregar e consolidar as medições de monóxido de carbono previamente registradas. O acionamento da função ocorre de maneira agendada. A cada 1 hora, um evento configurado no Amazon EventBridge, personalizado para cada região monitorada, dispara a execução da Save_Average_Readings. Ao ser invocada, a função coleta todas as leituras associadas à região correspondente ao evento dentro da última hora, realiza o cálculo da média das concentrações registradas e prepara um novo objeto contendo essas informações para ser salvo no Amazon DynamoDB.

### **Lambda: Prepare_Channel_Message**

A função Prepare_Channel_Message é responsável pela preparação das notificações que serão enviadas ao canal do Telegram, desempenhando um papel intermediário entre o processamento das médias e o envio efetivo das mensagens. Seu acionamento ocorre de forma automática por meio de um gatilho associado à tabela Average_CO_Measurements do Amazon DynamoDB. Sempre que uma nova média é registrada, o evento de inserção ativa essa função Lambda, passando o objeto recém-salvo como parâmetro.

### **Lambda: Notify_Message_Channel_Function**

A função Notify_Message_Channel_Function constitui a etapa final do fluxo de notificações, sendo responsável pelo envio efetivo das mensagens ao canal do Telegram. Diferentemente das funções anteriores, que lidam com ingestão, cálculo ou preparação de dados, esta função tem como foco exclusivo a comunicação direta com os usuários, garantindo que as informações de qualidade do ar cheguem ao público inscrito. 

---

## 📡 Esquema do Hardware

![Esquema do hardware](assets\04-Esquema_hardware.png)

---

## 🗂️ Esquema Completo da Aplicação

![AEsquema da aplicação](assets\06-Esquema_sistema.png)