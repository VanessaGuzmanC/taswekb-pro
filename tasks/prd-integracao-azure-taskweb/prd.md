# Product Requirements Document (PRD)

## Overview

TaskWeb PRO precisa se conectar ao Azure DevOps e ao Taskweb para eliminar o fluxo manual e fragmentado de registro de horas descrito em `overview/project_goal_context.md.md`. Este módulo é a camada de integração do produto: consulta tarefas pai e filhas no Azure, cria e atribui tarefas filhas quando necessário, e executa as ações operacionais de timer e apontamento no Taskweb. Ele é consumido pelos demais módulos do produto (interpretação de texto livre e controle de timer) e não possui interface própria voltada ao usuário final.

## Goals

- Permitir que o sistema consulte a tarefa pai (PBI, bug hom ou bug client) e suas tarefas filhas no Azure, sem navegação manual do usuário.
- Garantir que, ao final do fluxo, exista sempre uma única tarefa filha compatível (tipo de trabalho + usuário atribuído) para viabilizar o apontamento no Taskweb.
- Atingir taxa de acerto ≥ 95% na consulta/criação da tarefa filha correta, sem duplicidade, medida sobre os comandos processados durante a validação do MVP.
- Executar ações de timer e registro de horas no Taskweb de forma equivalente ao fluxo manual atual, sem alterar a tarefa pai nem remover tarefas filhas existentes.

## User Stories

- Como desenvolvedor, quero que o sistema localize a tarefa pai a partir de um ID informado, para não precisar navegar manualmente no Azure.
- Como desenvolvedor, quero que o sistema identifique se já existe uma tarefa filha compatível (mesmo tipo de trabalho e atribuída a mim), para evitar duplicidade.
- Como desenvolvedor, quero que, quando não existir tarefa filha compatível, o sistema crie uma automaticamente com o nome da tarefa pai e me atribua a ela, para que ela apareça no Taskweb sem esforço manual.
- Como desenvolvedor, quero que o sistema inicie e pare o timer e registre as horas no Taskweb a partir da tarefa filha correta, para completar o apontamento sem alternar entre sistemas.
- Como colega validador, quero confirmar que a integração não altera nem remove itens existentes no Azure, para confiar que o processo oficial do time não é comprometido.

## Main Features

### 1. Consulta de tarefa pai e tarefas filhas no Azure

O que faz: dado um ID de PBI, bug hom ou bug client, localiza o item pai e lista suas tarefas filhas existentes. Por que importa: é o ponto de entrada que decide se já existe estrutura reutilizável antes de criar algo novo. Como funciona (alto nível): consulta o item e seus relacionamentos no Azure DevOps.

Requisitos funcionais:
1.1. O sistema deve aceitar um ID numérico de tarefa pai (PBI, bug hom ou bug client) e retornar seus dados básicos (tipo, título, responsável).
1.2. O sistema deve listar todas as tarefas filhas vinculadas à tarefa pai informada.
1.3. O sistema deve identificar, entre as tarefas filhas retornadas, quais têm tipo de trabalho e responsável compatíveis com a solicitação atual.
1.4. Se o ID informado não existir ou não corresponder a um tipo de tarefa pai válido, o sistema deve informar o erro de forma clara ao usuário.

### 2. Criação de tarefa filha compatível

O que faz: cria uma nova tarefa filha vinculada à tarefa pai quando não existir uma compatível. Por que importa: elimina a etapa manual mais repetitiva do processo atual.

Requisitos funcionais:
2.1. O sistema só deve criar uma nova tarefa filha quando a consulta (Feature 1) não retornar nenhuma tarefa filha compatível com o tipo de trabalho e o usuário solicitante.
2.2. A tarefa filha criada deve ter o mesmo nome da tarefa pai.
2.3. A tarefa filha criada deve ser corretamente vinculada à tarefa pai de origem.
2.4. O sistema não deve criar uma segunda tarefa filha compatível caso já exista uma (evitar duplicidade).

### 3. Atribuição automática de tarefa filha

O que faz: garante que a tarefa filha (nova ou já existente) esteja atribuída ao usuário solicitante. Por que importa: no processo atual, a tarefa filha só aparece no Taskweb quando atribuída ao próprio usuário.

Requisitos funcionais:
3.1. O sistema deve atribuir a tarefa filha ao usuário solicitante quando ela ainda não estiver atribuída a ele.
3.2. A atribuição é condição necessária para que a tarefa fique disponível para uso no Taskweb.

### 4. Ações operacionais no Taskweb

O que faz: executa no Taskweb as ações de iniciar timer, parar timer e registrar horários para a tarefa filha correta. Por que importa: é a etapa final que transforma a estrutura preparada no Azure em um apontamento efetivo de horas.

Requisitos funcionais:
4.1. O sistema deve iniciar o timer no Taskweb para a tarefa filha correta, a partir de um comando processado por outro módulo.
4.2. O sistema deve parar o timer ativo no Taskweb quando solicitado.
4.3. O sistema deve registrar horas no Taskweb para a tarefa filha correta, respeitando um intervalo ou uma duração informados.
4.4. O sistema deve confirmar (retornar status de sucesso ou falha) ao concluir qualquer ação de timer ou registro.

## User Experience

Este módulo é majoritariamente uma camada de integração interna, sem interface própria voltada ao usuário final; é consumido pelos módulos de interpretação de texto livre e de controle de timer.

- **Perfis de usuário** (conforme `overview/project_goal_context.md.md`): Desenvolvedor (perfil primário), Integrante de projeto de desenvolvimento (perfil secundário), Colegas validadores (validação inicial).
- **Fluxo principal:** comando textual processado por outro módulo → este módulo consulta/cria/atribui a tarefa filha no Azure → executa a ação correspondente no Taskweb → retorna confirmação.
- **Acessibilidade:** por não ter UI própria, os requisitos de acessibilidade se aplicam à camada de saída de texto — mensagens de erro e confirmação devem ser claras, diretas e adequadas para leitura em terminal/chat.

## High-Level Technical Constraints

- Integração obrigatória com Azure DevOps via MCP (já disponível e conectado neste ambiente).
- Integração obrigatória com Taskweb via MCP dedicado (`taskweb-mcp`) — atualmente configurado, mas não conectado neste ambiente por uma pendência de permissões a ser resolvida fora do escopo deste módulo. Tratado como **dependência externa bloqueante** para a Feature 4 até que a conexão seja restabelecida.
- O sistema não deve modificar a tarefa pai além do necessário para leitura de contexto.
- O sistema não deve remover tarefas filhas existentes.
- Autenticação por token para as integrações, com credenciais nunca expostas em código-fonte (uso de variáveis de ambiente).
- Sem banco de dados: qualquer verificação de reaproveitamento de tarefa filha deve ser resolvida por consulta direta ao Azure, não por persistência local.

## Out of Scope

- Registro de horas por texto livre e interpretação de linguagem natural (coberto por outro módulo).
- Início/parada de timer disparados diretamente por comando de alto nível do usuário (módulo de Controle de Timer; este PRD cobre apenas a execução da ação no Taskweb).
- Edição em massa de tarefas ou gestão completa de backlog no Azure.
- Modificação da tarefa pai além da leitura de contexto.
- Resolução do problema de conectividade/permissões do MCP `taskweb-mcp` — tratada como dependência externa, não como entrega deste módulo.
- Relatórios gerenciais ou histórico próprio de registros de horas.
