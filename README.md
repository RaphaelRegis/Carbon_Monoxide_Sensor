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




1 - Função1 envia mensagens pro Telegram:
	- Recebe: região, average_measurement
	- Precisa de: sqs_queue_url, bot_token, channel_id
	- Região: usada para buscar os outros dados na Tabela3
	- Average_measurement: compõe a mensagem a ser enviada
	- sqs_queue_url: para guardar mensagens não enviadas e tentar enviar depois
	- bot_token: id do bot para enviar corretamente
	- channel_id: para poder enviar no canal correto

2 - Função1 é chamada quando um item é salvo na Tabela1:
	- item contém: região, data, hora, average_measurement

3 - O Evento1 salva alguém na Tabela1 a cada 1 hora:
	- chama uma FunçãoA para pegar as medidas de uma região na última hora, calcular a média e salvar na Tabela1
	- a região específica fica no 'detail' do Evento1 (payload)

4 - Evento1 usa dados da Tabela2:
	- Tabela2 contém as leituras feitas pelos sensores
	- Cada item contém: região, id_sensor, data, hora, measurement

5 - Função2 salva dados na Tabela2:
	- Função 2 é chamada através de uma API	Rest
	- O body que a função recebe inclui: região, id_sensor e medida
	- A data/hora é pega pelo próprio python e convertida de acordo

6 - Função3 cria toda a infraestrutura de eventos acima:
	- Cria uma versão do Evento 1 para cada novo registro
	- Cria também uma fila do sqs para cada novo registro
	- Os atributos de cada registro estão descritos abaixo

7 - Função3 é chamada quando alguém é salvo na Tabela3:
	- Os dados salvos são: região, sqs_queue_url, bot_token, channel_id

9 - Função 4 é chamada quando alguém é removido da Tabela3:
	- Ela exclui a fila e o evento de acordo com a região