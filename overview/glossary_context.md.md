# Glossário do Projeto

## Termos do Domínio

| Termo | Tradução EN | Definição | Evitar (sinônimos incorretos) |
|---|---|---|---|
| Taskweb | Taskweb | Sistema web corporativo onde os usuários apontam as horas trabalhadas durante o horário laboral. No contexto deste projeto, é o sistema oficial de registro de horas, incluindo ações como registrar intervalos de trabalho e operar o timer. É usado por pessoas envolvidas em projetos de desenvolvimento que precisam imputar esforço em tarefas válidas para apontamento. | Sistema de tarefas |
| Azure | Azure | Sistema web utilizado para consultar tarefas pai e tarefas filhas relacionadas ao trabalho executado. No contexto do produto, serve como fonte para localizar PBIs e bugs, verificar tarefas filhas existentes, criar novas tarefas filhas quando necessário e atribuí-las ao usuário para que possam ser usadas no Taskweb. | Taskweb |
| PBI | Product Backlog Item | Tipo de tarefa pai que representa um desenvolvimento novo. É um item principal de trabalho visível no board e pode originar tarefas filhas usadas no fluxo de apontamento. Quando o usuário informa um ID de PBI, o sistema deve localizar esse item e verificar ou criar a tarefa filha apropriada para registro de horas. | Tarefa filha |
| Bug hom | Homologation bug | Tipo de tarefa pai que representa um bug descoberto por alguém da própria empresa. Assim como o PBI, pode ter tarefas filhas e servir de referência para criação, atribuição e uso no fluxo de apontamento de horas do Taskweb. | Bug client |
| Bug client | Client bug | Tipo de tarefa pai que representa um bug descoberto pelo cliente. É usado como referência principal de trabalho no fluxo atual e pode originar tarefas filhas compatíveis com o apontamento de horas. | Bug hom |
| Tarefa pai | Parent task | Tarefa principal visível no board, como um PBI, bug hom ou bug client. Pode ter uma ou mais tarefas filhas associadas. No contexto deste projeto, a tarefa pai é a origem funcional da atividade informada pelo usuário e não deve ser modificada pela solução além do necessário para localizar contexto. | Tarefa de horas |
| Tarefa filha | Child task | Tarefa vinculada a exatamente uma tarefa pai. No processo atual, é a unidade operacional necessária para que o registro de horas apareça no Taskweb. Para ser utilizável, precisa estar associada ao pai correto, ser atribuída ao usuário e possuir um tipo compatível com a natureza do trabalho executado. | Subtarefa genérica |
| Registro de horas | Time entry | Ato de anotar no sistema web as horas utilizadas em atividades durante o horário laboral. No contexto do TaskWeb PRO, o registro pode ser disparado a partir de texto livre, desde que o sistema consiga identificar a atividade, a referência correta e o intervalo de tempo a lançar. | Fechar tarefa |
| Timer | Timer | Relógio operacional usado para indicar por quanto tempo o usuário esteve trabalhando em uma tarefa. No contexto do projeto, o timer pode ser iniciado e parado a partir de comandos em texto, desde que exista uma tarefa válida no Taskweb para receber a medição. | Cronômetro informal |
| Development | Development | Tipo de tarefa filha que indica que o trabalho executado foi de desenvolvimento. Deve ser usado quando o usuário informar que está desenvolvendo um PBI, bug ou outra atividade que exija uma tarefa filha classificada como development para fins de apontamento. | Coding |
| Test | Test | Tipo de tarefa filha que indica que o trabalho executado foi de teste, code review ou homologação de uma tarefa. No contexto do produto, é uma classificação funcional importante para encontrar ou criar a tarefa filha correta antes do registro de horas. | QA genérico |
| Business analysis | Business analysis | Tipo de tarefa filha que indica que o trabalho executado foi de análise da tarefa. É usado quando a atividade informada estiver relacionada a entendimento, refinamento ou avaliação do trabalho antes da implementação ou validação. | Análise sem tarefa |

---

## Status e Ciclos de Vida

### Tarefa filha

A tarefa filha percorre um ciclo operacional necessário para que possa receber apontamento no Taskweb. Ela pode nascer a partir de uma necessidade de registro do usuário ou ser reaproveitada se já existir com os atributos corretos.

| Status | Descrição | Transições permitidas |
|---|---|---|
| Criada | A tarefa filha existe no Azure e está vinculada a uma tarefa pai, mas ainda pode não estar atribuída ao usuário. | Atribuída |
| Atribuída | A tarefa filha já foi atribuída ao usuário que fará o registro de horas. | Visível no Taskweb |
| Visível no Taskweb | A tarefa filha já aparece no Taskweb e pode ser usada para registrar horas. | Disponível para timer |
| Disponível para timer | A tarefa filha está apta para receber operações de timer e apontamento de horas no fluxo normal. | Permanece disponível para novos registros |

---

## Relações Entre Termos

- Um PBI é um tipo de tarefa pai usado para representar um desenvolvimento novo.
- Um bug hom é um tipo de tarefa pai usado para representar um bug descoberto por alguém da empresa.
- Um bug client é um tipo de tarefa pai usado para representar um bug descoberto pelo cliente.
- Uma tarefa pai pode ter uma ou mais tarefas filhas associadas.
- Uma tarefa filha pertence a exatamente uma tarefa pai.
- Uma tarefa filha precisa estar atribuída ao usuário para aparecer no Taskweb.
- Uma tarefa filha precisa ter tipo compatível, como development, test ou business analysis, para ser usada corretamente no fluxo de apontamento.
- O registro de horas acontece no Taskweb, mas depende de informações e estrutura vindas do Azure.
- O timer opera sobre uma tarefa que já está disponível no Taskweb para o usuário.

---

## Siglas e Abreviações

| Sigla | Significado | Contexto de uso |
|---|---|---|
| PBI | Product Backlog Item | Usada para identificar tarefas pai de desenvolvimento novo |

---

## Histórico de Alterações

| Data | Termo | Alteração | Motivo |
|---|---|---|---|
| 2026-09-10 | PBI | Adicionado | Termo inicial necessário para o domínio do projeto |
| 2026-09-10 | Taskweb / Azure / tipos de tarefa filha | Adicionado | Consolidação inicial do vocabulário do processo de registro de horas |
