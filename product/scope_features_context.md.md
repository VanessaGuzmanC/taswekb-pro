# Detalhamento do Escopo Macro do Projeto

## Visão Geral do Produto

TaskWeb PRO é uma solução interna para reduzir o atrito operacional no registro de horas em Taskweb. O produto permite que usuários descrevam em texto livre o trabalho realizado, para que o sistema identifique a atividade correta, consulte Taskweb e Azure, crie e atribua tarefas filhas quando necessário e registre o tempo sem exigir o fluxo manual atual. Quando o projeto estiver completo, o registro de horas deve acontecer com muito menos passos, menor risco de esquecimento e melhor aderência às regras do processo atual da empresa.

---

## Roadmap

| Ordem | Módulo | O que entrega ao negócio |
|---|---|---|
| 1 | Integração com Azure/Taskweb | Permite que o sistema consulte tarefas, crie e atribua tarefas filhas e execute ações de apontamento no ecossistema atual |
| 2 | Criação e atribuição automática de tarefas filhas | Elimina a etapa manual de preparar a tarefa necessária para que ela apareça no Taskweb e possa receber horas |
| 3 | Registro de horas em texto livre | Reduz o esforço do usuário ao permitir informar atividade e tempo de forma natural, sem navegar manualmente entre sistemas |
| 4 | Controle de timer | Permite iniciar e parar o relógio operacional diretamente pelo software, reduzindo esquecimentos e fricção no acompanhamento do trabalho |

---

## Módulos e Features

---

### Módulo: Integração com Azure/Taskweb

Este módulo conecta o TaskWeb PRO aos sistemas envolvidos no fluxo atual de trabalho. Ele é usado principalmente por desenvolvedores e demais participantes de projetos de desenvolvimento para que o software possa consultar tarefas, localizar referências de trabalho e executar ações operacionais sem depender de navegação manual em cada plataforma.

#### Feature: Consulta de tarefas pai e filhas no Azure

Esta feature permite ler tarefas pai e tarefas filhas no Azure para entender a estrutura de trabalho associada a um PBI, bug hom ou bug client. O objetivo é que, ao receber um ID numérico informado pelo usuário, o sistema consiga identificar a tarefa pai correta, verificar se já existe tarefa filha compatível e reaproveitar essa estrutura sempre que possível. A consulta precisa respeitar as regras atuais do processo, em que o lançamento de horas depende da existência de uma tarefa filha utilizável no Taskweb.

#### Feature: Criação de tarefas filhas no Azure

Esta feature cria automaticamente uma tarefa filha quando o fluxo exigir uma tarefa vinculada a um PBI ou bug e ainda não houver uma filha compatível para o usuário e para o tipo de trabalho executado. A criação deve seguir a regra de negócio já estabelecida: a tarefa filha precisa ter o mesmo nome da tarefa pai. O valor entregue ao negócio é eliminar uma etapa manual recorrente que hoje atrasa e desincentiva o apontamento de horas.

#### Feature: Atribuição automática de tarefas filhas

Esta feature atribui a tarefa filha ao próprio usuário quando isso for necessário para que ela apareça no Taskweb. Isso é essencial porque, no fluxo atual, tarefas filhas só podem ser usadas no apontamento quando estão atribuídas à pessoa que registrará as horas. A feature deve ser usada tanto para tarefas recém-criadas quanto para tarefas já existentes que ainda precisem ser atribuídas corretamente.

#### Feature: Ações operacionais no Taskweb

Esta feature permite que o software execute no Taskweb as ações de iniciar timer, parar timer e registrar horários. O objetivo não é substituir o Taskweb, mas operar sobre ele de forma assistida ou integrada para que o usuário continue obedecendo ao processo oficial da empresa com menos esforço manual. Essa feature é crítica porque concentra a etapa final de transformação do comando em texto em um lançamento efetivo de horas.

---

### Módulo: Criação e atribuição automática de tarefas filhas

Este módulo resolve a principal fricção do processo atual: a necessidade de preparar manualmente a estrutura de tarefa antes de conseguir lançar horas. Ele atende usuários que trabalham sobre PBIs e bugs e precisam garantir que exista uma tarefa filha adequada, com tipo correto e atribuída corretamente.

#### Feature: Reutilização de tarefa filha existente

Esta feature verifica se já existe uma tarefa filha compatível para a atividade solicitada antes de criar uma nova. A compatibilidade deve considerar, no mínimo, a pessoa atribuída e o tipo de tarefa filha necessário para a atividade, como development, test ou business analysis. O comportamento esperado é evitar duplicidade desnecessária e reaproveitar estruturas já válidas para o fluxo operacional do usuário.

#### Feature: Criação condicional por tipo de trabalho

Esta feature decide quando uma nova tarefa filha precisa ser criada com base no tipo de trabalho informado ou inferido, como development, test ou business analysis. Por exemplo, se o usuário disser que está desenvolvendo um PBI específico, o sistema deve procurar uma tarefa filha do tipo development; se existir uma compatível, deve usá-la, e se não existir, deve criá-la. Essa regra diferencia o produto de uma automação genérica porque leva em conta o vínculo entre natureza da atividade e tipo da tarefa filha.

#### Feature: Validação de unicidade da tarefa compatível

Esta feature parte da premissa de negócio de que não deveria existir mais de uma tarefa filha compatível ao mesmo tempo para a mesma pessoa e o mesmo tipo de trabalho. A validação deve cruzar o tipo da tarefa filha com a pessoa atribuída para reduzir ambiguidades no momento do apontamento. O valor entregue é aumentar previsibilidade e evitar que o sistema registre horas na tarefa errada quando houver múltiplas alternativas indevidas.

---

### Módulo: Registro de horas em texto livre

Este módulo transforma comandos escritos pelo usuário em ações concretas de apontamento. Ele é o núcleo da simplificação da experiência, pois reduz a necessidade de abrir vários sistemas e navegar manualmente para completar o registro de horas.

#### Feature: Interpretação de comandos em linguagem natural

Esta feature interpreta frases escritas livremente pelo usuário para extrair atividade, referência de tarefa e informação temporal. O sistema deve conseguir entender comandos como “Tuve daily desde las 10:00 hasta las 10:15”, “Tuve una reunión a las 10:00 y duró 2 horas”, “Empecé a desarrollar el PBI 1234112” e “Estuve testeando el bug 123910 desde las 15:00 por 1 hora”. A interpretação precisa ser suficientemente robusta para suportar tanto descrições por nome quanto referências diretas por ID.

#### Feature: Registro por rango horario

Esta feature permite registrar horas a partir de uma hora inicial e uma hora final, ou de uma hora inicial combinada com uma duração informada. Isso atende situações em que o usuário sabe exatamente em que intervalo trabalhou e quer converter essa informação diretamente em apontamento no Taskweb. O benefício para o negócio é tornar o lançamento mais rápido e compatível com a forma como as pessoas relatam trabalho no dia a dia.

#### Feature: Registro por quantidade de horas a partir de contexto textual

Esta feature suporta frases em que o usuário informa uma atividade e a duração total, sem precisar detalhar todo o fluxo operacional intermediário. O sistema deve extrair o tempo, relacioná-lo com a atividade informada e encaminhar o apontamento na tarefa adequada. Isso amplia a flexibilidade de uso e reduz a dependência de comandos rígidos.

#### Feature: Confirmação assistida em casos ambíguos

Esta feature lida com textos em que a atividade descrita não aponta claramente para uma única tarefa. Nesses casos, o sistema deve tentar encontrar a coincidência mais próxima, mas sempre pedir confirmação ao usuário antes de registrar as horas. Se mesmo assim a tarefa não puder ser determinada com segurança, o sistema deve pedir o ID da tarefa pai para continuar o processo.

---

### Módulo: Controle de timer

Este módulo cobre situações em que o usuário não quer apenas registrar horas retrospectivamente, mas acompanhar a atividade em andamento. Ele complementa o lançamento por texto com operações de início e fim de medição operacional no Taskweb.

#### Feature: Iniciar timer a partir de comando textual

Esta feature permite que o usuário inicie o timer por meio de um comando em texto, como ao informar que começou a desenvolver um PBI específico. O sistema deve localizar a tarefa correta, preparar a estrutura necessária caso não exista tarefa filha compatível e então iniciar o relógio operacional no Taskweb. O valor é reduzir o risco de o usuário adiar o apontamento e depois esquecer de registrar o início real da atividade.

#### Feature: Parar timer e consolidar apontamento

Esta feature permite encerrar o timer por comando textual quando o usuário concluir ou interromper a atividade. O sistema deve identificar o timer ativo relacionado à tarefa correta e efetivar a parada do relógio no Taskweb. Isso mantém o fluxo simples e ajuda a reduzir erros comuns de deixar medições abertas por esquecimento.

---

## Fora do Escopo

| Item excluído | Motivo |
|---|---|
| Substituir o Taskweb como sistema oficial de apontamento | O produto existe para facilitar o processo atual, não para trocar a ferramenta corporativa |
| Manter histórico próprio de registros | A primeira versão foca em registrar horas, não em construir uma camada paralela de auditoria ou histórico |
| Gerar relatórios gerenciais avançados | O objetivo inicial é eficiência operacional no apontamento, não analytics de gestão |
| Editar tarefas em massa | O escopo está restrito ao fluxo pontual necessário para registrar horas de uma atividade específica |
| Fazer gestão completa de backlog no Azure | O sistema só deve consultar itens e criar/atribuir tarefas filhas quando necessário para o apontamento |
| Modificar tarefas pai | A solução não deve alterar PBI, bug hom ou bug client além do estritamente necessário para localizar contexto |
| Remover tarefas filhas | O produto não deve excluir estruturas existentes, apenas reutilizar ou criar quando fizer sentido |
