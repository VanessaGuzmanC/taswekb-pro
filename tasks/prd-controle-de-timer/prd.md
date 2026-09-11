# Product Requirements Document (PRD)

## Overview

Hoje, mesmo com o TaskWeb PRO automatizando a localização e criação de tarefas filhas e o registro retrospectivo de horas (rango horário, duração), iniciar e parar o relógio operacional do Taskweb continua sendo uma ação manual: o usuário precisa abrir o Taskweb, encontrar a tarefa filha correta e clicar em iniciar/parar o timer no momento exato em que começa ou termina uma atividade.

Esta feature fecha essa lacuna, permitindo que o usuário controle o timer do Taskweb por comando de texto livre — por exemplo, "Empecé a desarrollar el PBI 1234112" para iniciar, e "Terminé"/"Paré" para encerrar — reaproveitando a mesma resolução automática de tarefa (pai → filha compatível → criação/atribuição, se necessário) já entregue pelos módulos anteriores. É o quarto e último módulo do roadmap do TaskWeb PRO, complementando o registro retrospectivo com acompanhamento em tempo real da atividade.

## Goals

- Eliminar a necessidade de abrir o Taskweb manualmente para iniciar ou parar o timer de uma atividade — sucesso: um comando de texto único resulta no timer iniciado/parado no Taskweb, sem navegação manual.
- Reduzir o esquecimento de registrar o início real de uma atividade — sucesso: o timer começa a contar no exato momento em que o usuário comunica que começou a trabalhar.
- Permitir encerrar uma atividade em andamento sem que o usuário precise repetir qual tarefa estava sendo medida — sucesso: um comando de parada simples ("parei", "terminei") é suficiente na maioria dos casos.

## User Stories

- Como desenvolvedor, quero dizer "Empecé a desarrollar el PBI 1234112" e ter o timer da tarefa filha correta iniciado automaticamente no Taskweb, para não esquecer de marcar o início do meu trabalho.
- Como desenvolvedor, quero dizer apenas "Terminé"/"Parei" ao concluir uma atividade e ter o timer correspondente parado, sem precisar informar de novo qual PBI ou bug eu estava trabalhando.
- Como desenvolvedor, quero poder informar explicitamente outra tarefa ao parar (ex.: "Paré el testing del bug 123910") quando quiser encerrar um timer diferente do último iniciado.
- Como desenvolvedor, quero ser avisado se eu tentar iniciar um novo timer enquanto já existe um em andamento, para não perder silenciosamente o rastreamento da atividade anterior.
- Como desenvolvedor, quero receber uma mensagem clara se eu pedir para parar um timer e não houver nenhum em andamento, em vez de uma ação silenciosa ou um erro confuso.

## Main Features

### Feature 1: Iniciar timer a partir de comando textual

Interpreta um comando de texto livre de início de atividade (ex.: "Empecé a desarrollar el PBI 1234112") e inicia o timer no Taskweb para a tarefa filha correspondente, reaproveitando integralmente o fluxo já existente de resolução de tarefa pai, busca de tarefa filha compatível, criação e atribuição automática quando necessário (Módulo 1 — Integração com Azure/Taskweb).

Requisitos funcionais:
1. O sistema deve aceitar um comando de texto livre contendo uma referência a PBI/bug (por ID) e uma indicação de início de atividade.
2. Antes de iniciar o timer, o sistema deve garantir que existe uma tarefa filha compatível com o usuário e o tipo de trabalho identificado, criando e atribuindo uma nova tarefa filha quando não houver uma compatível (reaproveitando a regra de negócio do Módulo 1, sem duplicá-la).
3. O sistema deve iniciar o timer no Taskweb para essa tarefa filha assim que ela estiver disponível (existente ou recém-criada e atribuída).
4. Se já existir um timer em andamento para uma tarefa diferente da solicitada, o sistema deve avisar o usuário e pedir confirmação antes de iniciar o novo timer, em vez de substituir silenciosamente o rastreamento do timer anterior.
5. Se o comando de início não permitir identificar com segurança a tarefa (PBI/bug), o sistema deve seguir a mesma regra de confirmação assistida já definida para o registro de horas em texto livre (pedir confirmação ou solicitar o ID da tarefa pai).

### Feature 2: Parar timer e consolidar apontamento

Interpreta um comando de texto livre de encerramento de atividade (ex.: "Terminé", "Paré", "Terminé el PBI 1234112") e para o timer correspondente no Taskweb, identificando automaticamente qual timer encerrar quando o usuário não repetir a referência da tarefa.

Requisitos funcionais:
6. O sistema deve reconhecer um comando de parada de atividade mesmo quando ele não menciona explicitamente qual tarefa está sendo encerrada.
7. Quando o comando de parada não especifica a tarefa, o sistema deve parar o timer da última tarefa para a qual um timer foi iniciado pelo usuário (o timer ativo mais recente).
8. Quando o comando de parada menciona explicitamente uma tarefa (PBI/bug), o sistema deve usar essa referência para decidir qual timer parar, mesmo que seja diferente do timer ativo mais recente.
9. Se o usuário pedir para parar um timer e não houver nenhum timer em andamento rastreado pelo sistema, o sistema deve informar isso claramente em vez de executar uma ação silenciosa ou retornar um erro genérico.
10. Parar o timer no Taskweb é suficiente para consolidar o apontamento do intervalo trabalhado — nenhum registro ou cálculo adicional de horas é feito pelo TaskWeb PRO além da própria parada do timer.

## User Experience

- Usuário primário: desenvolvedores e demais integrantes de projetos internos que já usam o TaskWeb PRO para registro de horas em texto livre, agora estendendo o mesmo canal de comando de texto para controlar o timer.
- Fluxo principal de início: usuário informa em texto livre que começou uma atividade vinculada a um PBI/bug → sistema resolve/cria/atribui a tarefa filha → timer é iniciado → sistema confirma ao usuário que o timer está rodando e em qual tarefa.
- Fluxo principal de parada: usuário informa em texto livre que terminou/parou → sistema identifica o timer ativo relevante (implícito ou explícito) → timer é parado → sistema confirma ao usuário que o timer foi encerrado e em qual tarefa.
- Fluxos alternativos: tentativa de iniciar um segundo timer com um primeiro ainda ativo (pede confirmação); tentativa de parar sem timer ativo (mensagem informativa); referência ambígua à tarefa (segue a mesma confirmação assistida do registro de horas em texto livre).
- Interface: sem UI própria — interação via texto livre pelo mesmo canal usado pelas demais features do TaskWeb PRO (CLI/chat), sem tela dedicada.
- Acessibilidade: por ser uma interação inteiramente textual, sem elementos visuais próprios, os requisitos de acessibilidade já cobertos pelo canal de texto livre existente (linguagem natural, sem exigência de formato rígido) se aplicam integralmente.

## High-Level Technical Constraints

- Depende das ações de timer do Taskweb (iniciar/parar) já modeladas na integração com o Taskweb (Módulo 1); enquanto essa integração não estiver conectada em produção, esta feature fica no mesmo estado "código pronto, aguardando conexão" descrito no README do projeto.
- Depende da resolução/criação/atribuição automática de tarefa filha (Módulo 1) e da interpretação de comandos em texto livre (Módulo 3) — não deve duplicar essa lógica, apenas reaproveitá-la.
- Sem banco de dados e sem servidor de aplicação dedicado (restrição do projeto) — qualquer rastreamento de qual timer está ativo deve funcionar dentro dessas restrições, sem exigir infraestrutura nova.
- Execução somente local, sem frontend web — mesma restrição técnica das demais features do TaskWeb PRO.
- Tokens e credenciais de Azure/Taskweb continuam vindo exclusivamente de variáveis de ambiente, nunca em código-fonte.
- Não deve modificar a tarefa pai nem remover tarefas filhas existentes, seguindo as restrições já estabelecidas para todo o produto.

## Out of Scope

- Sincronizar ou reconciliar o rastreamento de timer do TaskWeb PRO com o estado real do timer no Taskweb caso ele seja alterado diretamente na interface do Taskweb (fora do TaskWeb PRO) — o sistema assume que toda ação de timer passa pelo TaskWeb PRO.
- Suportar múltiplos timers simultâneos ativos para o mesmo usuário.
- Gerar relatórios, histórico próprio ou totais de tempo trabalhado a partir dos timers iniciados/parados — o Taskweb continua sendo o sistema oficial de apontamento.
- Pausar/retomar um timer (apenas iniciar e parar são cobertos).
- Qualquer alteração na tarefa pai ou remoção de tarefas filhas existentes.
- Editar tarefas em massa ou gestão completa de backlog no Azure.
