## descricao
O problema clássico de Localização de Facilidades Capacitadas (CFLP, na sigla em inglês) 
consiste em selecionar facilidades a serem abertas/construídas para atender clientes. 
As restrições referem-se aos clientes, cuja demanda deve ser integralmente atendida, 
e à capacidade das facilidades, que não pode ser excedida. 
Consideraremos a versão de múltiplas fontes do problema, na qual 
cada cliente pode ser atendido por mais de uma facilidade. 
A função objetivo, que deve ser minimizada, consiste na soma dos custos fixos de abertura das facilidades e dos custos variáveis de transporte (cliente, facilidade). este problema tradicional, adicionaremos a restrição de que certos pares de clientes não podem ser atendidos pela mesma facilidade. 
Essa restrição modela situações reais em que os clientes possuem demandas conflitantes (por exemplo, componentes químicos que devem ficar bem longe um do outro).

Seja J um conjunto de facilidades tal que cada facilidade j ∈ J possua uma Capacidade_j e um CustoFixo_j. 
Seja I um conjunto de clientes tal que cada cliente i possui uma Demanda_i, 
que deve ser totalmente atendida por uma ou mais facilidades. 
Há também um CustoTransporte_{ij}, que representa o custo de transportar mercadorias da facilidade j para o cliente i. 
Por fim, é fornecido um conjunto de pares de clientes conflitantes: 
para cada (i1, i2) pertencente ao conjunto ParesConflitantes, os clientes i1 e i2 não podem ser atendidos pela mesma facilidade.

Variáveis de decisão:
(i)  Variáveis ​​inteiras não negativas x_{ij}, 
     que representam a quantidade de mercadorias transportadas da facilidade j para o cliente i; e 
(ii) Variáveis ​​binárias y_j, 
     que determinam se uma facilidade j será aberta (y_j = 1) ou não (y_j = 0).


## Toy
Facilidades = 4;
Clientes = 10;

Capacidades = [95, 30, 30, 35];
CustosFixos = [600, 250, 430, 590];
Demandas = [10, 20, 8, 12, 23, 25, 16, 18, 13, 21];
CustosTransporte = [|23, 70, 45, 65
                    |43, 39, 37, 36
                    |57, 80, 38, 90
                    |30, 78, 54, 88
                    |36, 78, 70, 68
                    |47, 65, 39, 41
                    |99, 98, 80, 26
                    |40, 36, 19, 65
                    |86, 50, 53, 39
                    |72, 97, 89, 29|];

A
 
Conflitos = 3;
ParesConflitantes = [| 2, 5 | 1, 7 | 4, 6 |];

## Geração da solução incial gulosa

A geração da solução inicial gulosa funciona da seguinte forma: o algoritmo abre facilidades, uma a uma, até que a soma das capacidades das facilidades abertas seja maior ou igual à demanda total de todos os clientes.

Escolha da facilidade a ser aberta: aquela com a melhor relação CustoFixo/Capacidade, ou seja, a mais barata por unidade de capacidade.
Verificar se posso/devo atender o cliente i com a facilidade aberta j:
O cliente i ainda tem demanda não atendida?
A facilidade j ainda tem capacidade sobrando?
Verificação de Conflito: o cliente i não pode ter conflito com qualquer cliente que já esteja sendo atendido pela facilidade j.
Fazer a alocação: calcular o quanto pode ser enviado da facilidade j para o cliente i: min{demanda não atendida de i, capacidade residual de j}.

## Solução

fazer para GRASP e GA.