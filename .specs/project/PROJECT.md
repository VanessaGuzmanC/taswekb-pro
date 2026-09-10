# TaskWeb PRO

**Visão:** Automatizar e simplificar o registro de horas no Taskweb, permitindo que o usuário descreva a atividade em texto livre e o sistema localize ou crie a tarefa filha correta e efetive o apontamento.
**Para:** Desenvolvedores e demais integrantes de projetos de desenvolvimento internos da empresa que precisam registrar horas no Taskweb vinculadas a PBIs, bugs (hom/client) ou atividades recorrentes (daily, reuniões).
**Resolve:** O fluxo manual e fragmentado de registro de horas — hoje o usuário precisa localizar o item pai no Azure, criar manualmente uma tarefa filha, atribuí-la a si mesmo, aguardar sincronização com o Taskweb e só então lançar as horas, o que causa esquecimentos frequentes e prejudica as métricas de acompanhamento do time.

## Objetivos

- Reduzir o registro de horas de um fluxo manual multi-etapas para uma única interação em texto livre — sucesso: um comando único resulta em apontamento efetivado no Taskweb sem navegação manual entre sistemas.
- Automatizar a criação/atribuição de tarefas filhas quando necessário — sucesso: zero criação manual de tarefa filha pelo usuário para os casos cobertos pelo MVP.
- Reduzir esquecimentos de imputação e melhorar a confiabilidade das métricas de uso de horas do time — sucesso a ser mensurado com o time após uso real (ex.: redução de chamadas de atenção por falta de apontamento).

## Stack Tecnológico

**Núcleo:**

- Linguagem: Python 3.12
- Runtime: execução local via terminal (CLI ou bot/chat), sem servidor de aplicação dedicado
- Banco de dados: nenhum (sem persistência estruturada no MVP)

**Dependências-chave:** MCP (protocolo de integração com Azure e Taskweb), Claude (interpretação de linguagem natural), pip com versões travadas (`requirements.txt`), pytest (testes, recomendado)

## Escopo

**v1 inclui:**

- Integração com Azure e Taskweb (consulta de tarefas pai/filhas, ações operacionais de timer e apontamento)
- Criação e atribuição automática de tarefas filhas quando não existir uma compatível para usuário + tipo de trabalho
- Registro de horas via texto livre (por intervalo horário, por duração a partir de contexto textual, com confirmação assistida em casos ambíguos)
- Controle de timer (iniciar e parar via comando textual)

**Explicitamente fora de escopo:**

- Substituir o Taskweb como sistema oficial de apontamento
- Manter histórico próprio de registros ou gerar relatórios gerenciais avançados
- Editar tarefas em massa ou fazer gestão completa de backlog no Azure
- Modificar a tarefa pai ou remover tarefas filhas existentes

## Restrições

- Prazo: não informado
- Técnicas: sem frontend web, sem framework backend pesado, sem banco de dados, sem Docker; execução somente local; tokens e credenciais via variáveis de ambiente (nunca em código-fonte); não modificar a tarefa pai; não remover tarefas filhas existentes; criar tarefa filha somente quando não existir uma compatível para o usuário e o tipo de trabalho
- Recursos: MVP conduzido pelo usuário proponente, com validação inicial pelos colegas do time; patrocinador formal ainda a definir
