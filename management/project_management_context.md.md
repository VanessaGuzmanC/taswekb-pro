# Gestão do Projeto e Ciclo de Desenvolvimento

## Plataforma de Gestão

**Plataforma:** Azure DevOps
**URL / Acesso:** A confirmar — usar a mesma organização/projeto Azure DevOps já utilizado pelo time para PBIs, bugs e tarefas filhas
**Como solicitar acesso:** Solicitar ao usuário proponente (owner do projeto) ou ao administrador do projeto Azure DevOps da equipe

---

## Modelo de Organização do Trabalho

> Defina o significado de cada nível da hierarquia de trabalho neste projeto. Sem essa definição, cada pessoa do time interpreta os conceitos de forma diferente.

| Nível | Nome utilizado | O que representa | Exemplo |
|---|---|---|---|
| 1 — mais alto | Epic | Grande objetivo de negócio ou frente macro de entrega | Automação do registro de horas no TaskWeb PRO |
| 2 | Feature | Conjunto de funcionalidades relacionadas que entregam uma capacidade de negócio | Integração de registro de horas via MCP |
| 3 | PBI / Bug | Entrega implementável em um ciclo ou correção de defeito identificado | Registrar horas corretamente em um fluxo específico |
| 4 — mais baixo | Tarea hija | Atividade técnica menor necessária para concluir um PBI ou Bug | Ajustar validação de retorno ao registrar horas |

---

## Tamanho e Critérios de um PBI

> O tamanho máximo de um PBI define o ritmo de entrega e a capacidade de revisão do time. Estabeleça limites claros para evitar PBIs que duram semanas.

**Tamanho máximo:** Proposta inicial — até 3 dias de esforço estimado para uma pessoa (a confirmar com o time); acima disso, quebrar em mais de um PBI

**Um bom PBI deve:**
- Ter um critério de aceite claro e verificável
- Poder ser desenvolvido e testado de forma independente
- Ser pequeno o suficiente para caber em um ciclo
- Ter valor de negócio ou técnico identificável

**Um PBI deve ser quebrado quando:**
- Exceder o tamanho viável para um ciclo
- Tiver mais de uma responsabilidade principal
- Depender de outro item para ser validado adequadamente

---

## Modelo de Desenvolvimento

**Metodologia:** Scrum

**Duração do ciclo:** Proposta inicial — 1 semana, adequado ao ritmo de MVP e à necessidade de validação rápida com o time (a confirmar)

**Início do ciclo:** Proposta inicial — toda segunda-feira (a confirmar com o time)

---

## Cerimônias e Rituais

> Liste apenas as cerimônias que este time realmente pratica. Remova as que não se aplicam.

| Cerimônia | Frequência | Duração | Objetivo |
|---|---|---|---|
| Daily | Diária | 15 min (proposta padrão Scrum, a confirmar) | Sincronizar o time e identificar bloqueios |
| Sprint Planning | A cada sprint | 1h (proposta para ciclo de 1 semana, a confirmar) | Planejar o trabalho do ciclo |
| Review | A cada sprint | 30 min (proposta, a confirmar) | Demonstrar o trabalho entregue |
| Retrospectiva | A cada sprint | 30 min (proposta, a confirmar) | Identificar melhorias no processo |

---

## Fluxo de Status

> Defina os status que um item percorre desde a criação até a entrega. Mapeie exatamente como está configurado na plataforma de gestão.

| Status | Descrição | Quem move para cá |
|---|---|---|
| New | Item criado | Quem cria o item (usuário proponente ou colega do time) |
| Para desenvolvimento | Item priorizado e pronto para ser iniciado | Usuário proponente, ao priorizar o item no board |
| En desarrollo | Item em desenvolvimento | Desenvolvedor responsável pelo item |
| Para code review | Desenvolvimento concluído, aguardando revisão | Desenvolvedor responsável, ao concluir a implementação |
| En code review | Item em revisão técnica | Revisor técnico designado |
| Para homologacion | Revisão concluída, aguardando validação | Revisor técnico, ao aprovar o code review |
| En homologacion | Item em validação funcional | Colega validador / aprovador inicial |
| Done | Item validado e concluído | Colega validador, ao confirmar que o item atende à Definição de Pronto |

> Observação: responsáveis acima são uma proposta inicial baseada nos perfis descritos em `overview/project_goal_context.md.md`; devem ser confirmados formalmente com o time assim que houver mais de uma pessoa ativa no fluxo.

---

## Definição de Pronto (Definition of Done)

> Um item só pode ser marcado como Done quando todos os critérios abaixo forem atendidos. Esta lista é do time — ajuste conforme a realidade do projeto.

- O registro de horas deve ser realizado corretamente
- Se ocorrer algum erro no registro de horas, o sistema deve indicar o problema de forma clara
- O item deve estar validado no fluxo definido pelo time
- O trabalho entregue deve poder ser demonstrado

---

## Acompanhamento e Monitoramento

**Responsável pelo acompanhamento:** Usuário proponente (owner e idealizador do projeto), até que haja um patrocinador formal definido

**Métricas acompanhadas:**

| Métrica | O que mede | Onde é acompanhada | Frequência |
|---|---|---|---|
| Avanço por coluna | Progressão dos itens no fluxo de trabalho | Board do Azure DevOps | Contínua |

**Reporte para stakeholders:** O avanço é acompanhado pelas colunas do board e o trabalho concluído é demonstrado por meio de vídeo.
