# Product Requirements Document (PRD)

## Overview

Este módulo transforma comandos em texto livre do usuário em informação estruturada (referência de tarefa, tipo de trabalho, intervalo ou duração) para acionar o registro de horas e o controle de timer já construídos no módulo de Integração com Azure/Taskweb. É o núcleo da simplificação do processo descrito em `overview/project_goal_context.md.md`: elimina a necessidade de o usuário abrir sistemas e montar manualmente os dados do apontamento.

## Goals

- Permitir que o usuário registre horas descrevendo a atividade em texto livre, sem precisar informar campos estruturados manualmente.
- Suportar tanto referência direta por ID de tarefa pai quanto descrição da atividade sem ID (ex.: "daily", "reunião"), pedindo confirmação ou o ID quando necessário.
- Reduzir esquecimentos de apontamento e o tempo gasto para completar um registro de horas.
- Meta mensurável: interpretar corretamente (referência + intervalo/duração) pelo menos 90% dos comandos de exemplo documentados sem exigir confirmação adicional, medido durante a validação do MVP.

## User Stories

- Como desenvolvedor, quero informar "Estuve testeando el bug 123910 desde las 15:00 por 1 hora" e ter o sistema registrar automaticamente essas horas na tarefa filha correta.
- Como desenvolvedor, quero informar "Tuve daily desde las 10:00 hasta las 10:15" mesmo sem citar um ID, e ser guiado a confirmar ou informar a tarefa pai quando o sistema não conseguir determiná-la sozinho.
- Como desenvolvedor, quero informar "Empecé a desarrollar el PBI 1234112" e ter o sistema reconhecer que isso é um início de atividade (não um intervalo já concluído), encaminhando para o controle de timer.
- Como colega validador, quero que, em casos ambíguos, o sistema sempre confirme comigo antes de registrar, para não lançar horas na tarefa errada.

## Main Features

### 1. Interpretação de comandos em linguagem natural

Extrai da frase do usuário os dados necessários para acionar o registro. Por que importa: é o que permite ao usuário descrever o trabalho como faria naturalmente, em vez de preencher campos.

Requisitos funcionais:
1.1. O sistema deve extrair da frase: a atividade/referência de tarefa (ID explícito ou descrição textual), o tipo de trabalho quando inferível, e a informação temporal (horário de início, horário de fim e/ou duração).
1.2. O sistema deve reconhecer comandos que indicam início de atividade (ex.: "Empecé a...") como uma intenção de iniciar timer, distinta de um registro de intervalo já concluído.
1.3. Quando a frase não citar um ID de tarefa pai, o sistema deve tentar associar a atividade descrita a uma tarefa pai conhecida pelo contexto; se não for possível com segurança, deve seguir para a Feature 4 (confirmação assistida).
1.4. Atividades sem tipo de trabalho reconhecível associado a um PBI/bug explícito (ex.: "daily", "reunião") devem ser classificadas como `business_analysis` (decisão confirmada com o usuário — ver Restrições Técnicas de Alto Nível).

### 2. Registro por rango horario

Permite registrar a partir de um intervalo explícito de horários.

Requisitos funcionais:
2.1. O sistema deve aceitar um horário de início e um horário de fim, calculando a duração a partir deles.
2.2. O sistema deve aceitar um horário de início combinado com uma duração informada, calculando o horário de fim.
2.3. O sistema deve rejeitar e reportar de forma clara intervalos inválidos (fim anterior ou igual ao início).

### 3. Registro por quantidade de horas a partir de contexto textual

Permite registrar quando o usuário informa apenas a atividade e uma duração total, sem detalhar o horário.

Requisitos funcionais:
3.1. O sistema deve aceitar uma atividade e uma duração total sem exigir horário de início explícito.
3.2. Quando nenhum horário for informado, o sistema deve assumir que o intervalo termina no momento atual e inicia `duração` antes dele.

### 4. Confirmação assistida em casos ambíguos

Garante que o sistema nunca registre horas com base em uma suposição não confirmada.

Requisitos funcionais:
4.1. Quando a atividade descrita não apontar claramente para uma única tarefa pai, o sistema deve tentar a coincidência mais próxima e pedir confirmação explícita ao usuário antes de prosseguir.
4.2. Se a tarefa pai não puder ser determinada com segurança mesmo após a tentativa de coincidência, o sistema deve pedir o ID da tarefa pai diretamente ao usuário.
4.3. O sistema nunca deve registrar horas sem que a tarefa pai e o tipo de trabalho estejam determinados — seja por inferência confirmada, seja por informação direta do usuário.

## User Experience

Este módulo é o ponto de entrada conversacional do TaskWeb PRO: o usuário interage diretamente em texto livre (CLI ou chat), sem preencher formulários.

- **Perfis de usuário** (conforme `overview/project_goal_context.md.md`): Desenvolvedor (primário), Integrante de projeto de desenvolvimento (secundário), Colegas validadores (validação inicial).
- **Fluxo principal:** usuário descreve a atividade → este módulo extrai referência + tipo + tempo → o resultado é encaminhado ao módulo de Integração com Azure/Taskweb (para resolver/criar a tarefa filha e registrar horas) ou ao módulo de Controle de Timer (para início/fim de timer) → o usuário recebe confirmação.
- **Acessibilidade:** mensagens de confirmação e erro devem ser claras e diretas, adequadas para leitura em terminal/chat, sem exigir que o usuário decore uma sintaxe rígida de comando.

## High-Level Technical Constraints

- A interpretação de linguagem natural é realizada pelo próprio Claude, executando este módulo como skill do Claude Code — não por um modelo de NLP customizado nem por regras rígidas de parsing.
- A normalização determinística (cálculo de intervalo/duração, validação de horários, mapeamento de atividade para tipo de trabalho) é feita em código Python, reutilizando as convenções já estabelecidas no módulo de Integração com Azure/Taskweb.
- Atividades sem tipo de trabalho reconhecível (ex.: "daily", "reunião") são classificadas como `business_analysis` — decisão confirmada nesta sessão, para não estender o glossário nem o mapeamento de `Microsoft.VSTS.Common.Activity` já implementado.
- Este módulo produz a entrada estruturada consumida pelo módulo de Integração com Azure/Taskweb (`ensure-child-task` / registro de horas) e pelo módulo de Controle de Timer (início/parada); não duplica a lógica de resolução de tarefa filha nem de execução no Taskweb já implementada.
- A execução real de ações no Taskweb (log de horas, timer) permanece bloqueada enquanto `taskweb-mcp` estiver desconectado. Este módulo pode ser implementado e testado (interpretação + estrutura de saída) independentemente dessa pendência, mas a validação de ponta a ponta depende dela.

## Out of Scope

- Execução das ações no Taskweb (log de horas, iniciar/parar timer) — já coberta pelos módulos de Integração com Azure/Taskweb e Controle de Timer; este módulo apenas os aciona.
- Suporte a comandos de voz ou qualquer entrada que não seja texto.
- Interpretação de múltiplas atividades em um único comando (ex.: relatar duas tarefas diferentes na mesma frase).
- Aprendizado ou ajuste automático da interpretação a partir do histórico do usuário — cada comando é interpretado de forma independente.
- Correção retroativa de registros já efetivados no Taskweb.
