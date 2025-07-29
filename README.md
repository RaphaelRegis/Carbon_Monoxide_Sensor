# Carbon_Monoxide_Sensor

1. os sensores enviam os dados para o API Gateway a cada 1 hora;
2. os dados passam por uma função Lambda e são salvos no Amazon DynamoDB;
3. em horários definidos, uma outra função Lambda pega todos os valores da última hora e tira uma média.
3.1 ela então verifica se há alguma mensagem não enviada no SQS.
3.2 caso tenha, ele tenta enviar. Caso contrário, ela volta pro SQS.
3.3 o mesmo é feito com a nova média.
4. todo mês, uma nova função lambda deve fazer uma análise do comportamento do ar ao longo do mês.