# Objetivo do Projeto

## Identificação do Sistema

**Nome do sistema:** TaskWeb PRO

**Status:** Ideia

**Repositório de código:** Sem repositório por enquanto

**Última atualização:** 2026-09-10 — Makuco

### Ambientes

| Ambiente | URL |
|---|---|
| Desenvolvimento | Não definido |
| Homologação | Não definido |
| Produção | Não definido |

---

## Problema a Ser Resolvido

**Situação atual:** Hoje, para registrar horas no Taskweb, pessoas que participam de projetos de desenvolvimento precisam executar um fluxo manual e fragmentado. Após concluir ou iniciar um trabalho, a pessoa precisa localizar o item pai no Azure ou fluxo equivalente (como PBI, bug client ou bug hom), criar uma tarefa filha com o mesmo nome do item pai, atribuí-la a si mesma, aguardar até que essa tarefa apareça no Taskweb, recarregar o sistema e só então registrar as horas. Esse processo também vale para atividades recorrentes como daily, quando o usuário precisa encontrar a tarefa correta antes de lançar o tempo.

**Causa raiz:** O Taskweb só permite registrar horas em tarefas filhas visíveis no sistema, e essas tarefas só aparecem quando estão atribuídas ao próprio usuário. Além disso, a criação e atribuição dessas tarefas não é automatizada, obrigando o usuário a alternar entre sistemas, esperar sincronização e executar várias etapas operacionais antes de lançar o tempo.

**Impacto:** O excesso de etapas faz com que usuários esqueçam de registrar horas com frequência. Isso gera chamadas de atenção internas, prejudica as métricas de acompanhamento e reduz a capacidade do time de entender onde o esforço está sendo consumido para depois otimizar alocação e produtividade. O problema afeta principalmente desenvolvedores, mas pode atingir qualquer pessoa envolvida em projetos de desenvolvimento que precise registrar horas no fluxo atual.

---

## Objetivo do Projeto

**Onde devemos chegar com o projeto entregue:**

- Reduzir o processo de registro de horas de um fluxo com múltiplos passos manuais para uma interação principal baseada em texto livre.
- Permitir que o usuário informe a atividade e o intervalo de tempo em linguagem natural, e que o sistema interprete essa informação para localizar a tarefa correta e registrar as horas.
- Automatizar a criação e atribuição de tarefas filhas quando elas forem necessárias para que o lançamento apareça no Taskweb.
- Reduzir esquecimentos de imputação e melhorar a confiabilidade das métricas de uso de horas do time.

---

## Visão Geral do Sistema

### Propósito

TaskWeb PRO é um software interno pensado para simplificar o registro de horas no Taskweb. Em vez de obrigar o usuário a criar manualmente tarefas filhas, alternar entre sistemas e esperar sincronização, a proposta é permitir que ele descreva em texto livre o que fez e em que intervalo trabalhou. A partir disso, o sistema deve identificar a atividade, localizar ou criar a tarefa necessária, atribuí-la ao usuário quando aplicável e registrar as horas com menos atrito operacional.

### Público-Alvo e Usuários

**Perfil 1 — Desenvolvedor**  
_Descrição: profissional de desenvolvimento que atua em projetos internos da empresa e precisa registrar horas de trabalho no Taskweb vinculadas a PBIs, bugs ou atividades recorrentes._  
_O que faz e quando faz: informa atividades realizadas ao longo do dia, como desenvolvimento de um PBI, atuação em bug ou participação em daily, esperando que o sistema identifique a referência correta e registre as horas sem depender de várias etapas manuais._

**Perfil 2 — Integrante de projeto de desenvolvimento**  
_Descrição: qualquer pessoa do time de projeto que também precise imputar horas dentro da operação atual, ainda que não seja o usuário inicial do produto._  
_O que faz e quando faz: registra esforço em atividades relacionadas ao projeto e sofre com o mesmo fluxo operacional de criação, atribuição e espera até a tarefa aparecer no Taskweb._

**Perfil 3 — Colegas validadores / aprovadores iniciais**  
_Descrição: membros do time que compartilham a dor do processo atual e atuarão como primeiros validadores do software._  
_O que faz e quando faz: experimentam o sistema no uso diário, verificam se o fluxo automatizado realmente reduz atrito e validam se os registros realizados fazem sentido para a rotina do time._

### Contexto de Mercado e Posicionamento

**Contexto de mercado:** O sistema se insere no contexto de ferramentas internas de produtividade para times de desenvolvimento que precisam conciliar gestão de trabalho em plataformas como Azure e apontamento operacional de horas em sistemas corporativos como Taskweb.

**Posicionamento:** TaskWeb PRO não pretende substituir o Taskweb nem uma ferramenta de gestão de backlog. Seu diferencial é atuar como uma camada de automação e simplificação do processo de imputação de horas, reduzindo esforço operacional para um fluxo que hoje depende de navegação manual, criação de tarefas e espera por sincronização.

**Público-alvo de mercado:** Equipes internas de desenvolvimento que usam Taskweb para registro de horas e mantêm itens de trabalho como PBI, bug client e bug hom em ferramentas relacionadas ao fluxo de desenvolvimento.

### Contexto de Uso pelo Cliente

O sistema será usado dentro da operação da empresa como ferramenta de apoio ao registro de horas. Ele deve se relacionar com o Taskweb e com Azure por integração via API ou MCP, conforme viabilidade técnica. No dia a dia, o usuário informará em texto livre o que fez e em qual intervalo de tempo trabalhou; a solução deverá localizar a tarefa correta no Taskweb ou no sistema de origem, verificar se existe tarefa filha adequada, criá-la e atribuí-la quando necessário e então efetivar o registro de horas no fluxo atual da empresa.

---

## Contexto de Negócio

**Sobre o negócio:** Trata-se de uma necessidade interna de uma empresa em que parte das pessoas envolvidas em projetos de desenvolvimento precisa registrar horas de trabalho em Taskweb. A dor não é universal para toda a empresa, mas é relevante para quem depende desse processo no dia a dia.

**Domínio e segmento:** O sistema se insere no domínio de gestão operacional de horas em projetos de desenvolvimento de software, com dependência de integração entre apontamento de horas e gestão de itens de trabalho.

**Processo atual (como as pessoas fazem hoje):** Ao realizar uma atividade, o usuário abre o item correspondente, como um PBI ou bug, cria manualmente uma tarefa filha com o mesmo nome do item pai, atribui essa tarefa a si mesmo, volta ao Taskweb, recarrega a interface e aguarda a tarefa aparecer para então lançar as horas. Em casos como daily, o usuário ainda precisa encontrar a tarefa correspondente antes de registrar o período trabalhado.

**Restrições e regras de negócio relevantes:**
- O Taskweb só exibe para apontamento as tarefas filhas de PBI e bug.
- A tarefa filha só aparece no Taskweb se estiver atribuída ao próprio usuário.
- Quando uma tarefa filha for criada para esse fluxo, ela deve ter o mesmo nome da tarefa pai.
- O sistema não deve remover tarefas filhas existentes.
- O sistema não deve modificar a tarefa pai.
- O registro de horas deve acontecer a partir de entrada em texto livre suficientemente clara para interpretação da atividade e do intervalo de tempo.

---

## Escopo Macro do Projeto

| # | Módulo / Epic | Prioridade |
|---|---|---|
| 1 | Integração com Taskweb e Azure/MCP | Alta |
| 2 | Criação e atribuição automática de tarefas filhas | Alta |
| 3 | Registro de horas por texto livre | Alta |
| 4 | Interpretação de atividades e associação com tarefa correta | Média |

---

## Escopo Negativo do Projeto

| O que não será feito | Motivo |
|---|---|
| Substituir o Taskweb | O objetivo é facilitar o uso do processo atual, não trocar o sistema oficial de apontamento |
| Remover tarefas filhas | A solução deve apenas criar quando necessário para viabilizar o registro |
| Modificar a tarefa pai | O foco é operar sobre o necessário para registrar horas, sem alterar o item principal |
| Manter histórico próprio de registros | Nesta primeira versão o foco é simplificar o lançamento de horas, não criar uma camada adicional de histórico |

---

## Pessoas e Interesses (Stakeholders)

| Nome | Empresa / Área | Papel no Projeto |
|---|---|---|
| Usuário proponente | Time de desenvolvimento | Stakeholder inicial, idealizador e usuário final |
| Colegas do time | Time de desenvolvimento | Usuários finais, validadores e aprovadores iniciais |
| Patrocinador formal | A definir | Patrocinador ou aprovador futuro, se necessário |

---

> **Próximo passo:** com este documento preenchido e revisado, acione o `makuco-specify` referenciando este arquivo para gerar as specs de cada módulo listado no Escopo Macro.
