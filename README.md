# Carbon_Monoxide_Sensor

FLUXO

I. SENSORES:
    - Os sensores enviam as leituras para uma API a cada 2 horas;
    - Essa API chama uma função Lambda;
    - Essa função Lambda salva os dados numa tabela do DynamoDB; (ok)

II. A CADA 2 HORAS:
    - A cada 2 horas, uma função pega os dados salvos, faz uma média e salva numa outra tabela do DynamoDB; (ok)
    - Toda vez que essa tabela recebe um novo dado, outra função Lambda é chamada;
    - Essa função fará o trabalho de notificar o Telegram com as recomendações; (ok)

III. TODO DIA ÀS 18:00 HORAS:
    - Uma outra função será chamada para imprimir a variação da qualidade do ar ao longo do dia