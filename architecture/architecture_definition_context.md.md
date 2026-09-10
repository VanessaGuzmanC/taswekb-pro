# Definição de Arquitetura

## Padrão Arquitetural Adotado

**Padrão:** Monólito modular orientado a integração

**Justificativa:** O TaskWeb PRO nasce como um MVP simples, sem frontend dedicado, com foco em resolver rapidamente a dor de registro de horas para um usuário inicial e depois para colegas do time. Como a primeira versão será um CLI ou bot/chat com backend único, um monólito modular reduz custo de implementação e operação, evita complexidade desnecessária de distribuição e facilita evoluir regras de interpretação de texto, integrações com Azure/Taskweb e fluxos de confirmação com o usuário dentro de uma mesma base de código. O uso de MCP e Claude apoia a camada de interação e automação, mas não justifica neste momento uma arquitetura distribuída mais sofisticada.

---

## Como o Sistema está Organizado

O sistema deve ser organizado como uma aplicação backend única, dividida em módulos internos por responsabilidade. Um módulo recebe o comando textual via CLI ou chat, outro interpreta intenção, tempos e referências de tarefa, outro aplica regras de negócio para decidir se deve procurar, reutilizar ou criar tarefa filha, e módulos de integração executam ações no Azure e Taskweb. Quando houver ambiguidade, a aplicação interrompe o fluxo automático, devolve opções ou pede confirmação ao usuário antes de concluir o registro.

---

## Decisões Arquiteturais Importantes

| Decisão | O que foi decidido | Justificativa |
|---|---|---|
| Canal de interação | O MVP será entregue como CLI ou bot/chat, sem frontend web dedicado | Minimiza esforço inicial, acelera validação com usuários reais e é suficiente para um fluxo baseado em texto livre |
| Topologia da aplicação | A solução será um backend único com módulos internos bem separados | Reduz complexidade operacional e facilita evolução rápida enquanto o produto ainda está em fase de ideia/MVP |
| Estratégia de integração | O sistema deve se integrar com Azure e Taskweb com apoio de API e/ou MCP, conforme viabilidade | O produto depende de consultar tarefas, criar/atribuir filhas e registrar horas sem navegação manual extensa |
| Interpretação de comandos | A entrada principal será texto livre interpretado pela aplicação com apoio de Claude | Esse modelo ataca diretamente a dor do usuário, que quer registrar horas descrevendo a atividade de forma natural |
| Tratamento de ambiguidade | Casos incertos não devem ser resolvidos silenciosamente; o sistema deve confirmar com o usuário | Evita lançar horas na tarefa errada e reduz risco operacional quando houver múltiplas coincidências ou contexto insuficiente |
| Integridade do item pai | O sistema não deve modificar a tarefa pai | Essa é uma regra de negócio já definida e limita o impacto da automação sobre o fluxo oficial existente |
| Criação de tarefas filhas | A criação de tarefa filha só acontece quando não existir uma compatível para usuário e tipo de trabalho | Evita duplicidade desnecessária e mantém aderência ao processo atual da empresa |

---

## Diagramas

**C1 — Contexto:** `architecture/diagrams/c4/c1-context.png` — pendente de criação  
**C2 — Containers:** `architecture/diagrams/c4/c2-containers.png` — pendente de criação  
**C3 — Componentes:** `architecture/diagrams/c4/c3-components.png` — pendente de criação

---

> **Lembrete:** este documento descreve a intenção arquitetural do MVP atual. Se no futuro o produto evoluir de CLI/chat para uma solução com frontend próprio, múltiplos serviços ou processamento assíncrono, as decisões aqui registradas devem ser revisadas e, se necessário, formalizadas com ADRs.
