# Carbon_Monoxide_Sensor

Primeiro vc salva uma entidade com os dados do bot:
	- Pra salvar, vc manda uma requisição que contém os dados do bot (região, token e canal)
	- Esse salvar chama uma função Lambda para criar o evento de notificar e a fila do SQS
	- Com todos os dados prontos (região, token, canal, fila sqs), ele salva a entidade

Função de salvar dados das leituras:
	- Os sensores enviam os dados (região, id_sensor e leitura) para uma API a cada 1 hora;
	- Uma função Lambda salva os dados (região, id_sensor, leitura, data, hora) numa tabela DynamoDB;

Função registrar médias:
	- O evento criado no primeiro passo possui a região, e chama uma função a cada hora;
	- Essa função pega as médias da região na última hora e salva numa tabela DynamoDB;
	- Ao salvar, a função chama uma próxima função para notificar o Telegram

Função notificar Telegram:
	- Essa função serve para mandar mensagens para o Telegram;
	- Primeiro ela busca os dados necessários na tabela DynamoDB do começo;
	- Em seguida, ela verifica se tem mensagens pendentes no SQS e tenta enviar;
	- Após isso ela cria a nova mensagem e tenta enviar;
	- Caso dê errado ele salva a mensagem no SQS.