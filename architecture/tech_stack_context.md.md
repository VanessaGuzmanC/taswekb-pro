# Stack de Tecnologia

## Linguagem e Runtime

| Item | Tecnologia | Versão | Observação |
|---|---|---|---|
| Linguagem principal | Python | 3.12 | Linguagem escolhida para implementação do projeto |
| Runtime / Plataforma | Python | 3.12 | Execução local via terminal, sem servidor de aplicação dedicado |
| Gerenciador de pacotes | pip | Fixar via `requirements.txt` com versões travadas (`pip freeze`) | Garante reprodutibilidade do ambiente local mesmo sem CI/CD formal no MVP |

---

## Frameworks e Bibliotecas Principais

| Camada | Framework / Biblioteca | Versão | Finalidade |
|---|---|---|---|
| Backend | Sem framework | N/A | Projeto orientado a execução em terminal e automação/integração |
| Frontend | Não se aplica | N/A | Não há interface web prevista neste momento |
| ORM / Acesso a dados | Não se aplica | N/A | O projeto não prevê uso de banco de dados |
| Testes | pytest | Recomendado (a confirmar com o time) | Framework leve, sem dependências pesadas, adequado para testar a lógica de interpretação de texto e as regras de decisão de tarefa filha |

---

## Banco de Dados

| Tipo | Tecnologia | Versão | Uso no sistema |
|---|---|---|---|
| Relacional | Não se aplica | N/A | O projeto não necessita banco de dados |
| Cache | Não se aplica | N/A | Não há necessidade de cache prevista |
| Busca | Não se aplica | N/A | Não há mecanismo de busca previsto |

---

## Infraestrutura e Cloud

| Item | Tecnologia | Observação |
|---|---|---|
| Cloud provider | Não se aplica por enquanto | Execução apenas local via terminal |
| Containers | Não utilizados | Não há empacotamento em contêiner definido |
| Orquestração | Não se aplica | Sem execução em ambiente orquestrado |
| CI/CD | Não crítico para o MVP | Execução é local e manual; se o repositório migrar para Azure Repos, avaliar Azure Pipelines para lint/testes básicos antes de evoluir o produto |
| Monitoramento | Logging local (módulo `logging` do Python) | Sem stack de observabilidade formal; registrar em log local as interpretações de comando, decisões de reaproveitar/criar tarefa filha e erros de integração, para permitir diagnóstico manual durante o MVP |

---

## Sistemas e Componentes Externos

> Registre todos os sistemas de terceiros, APIs externas e componentes compartilhados da organização que este sistema consome ou com os quais se integra.

| Sistema / Componente | Tipo | Finalidade | Como integra |
|---|---|---|---|
| Azure | MCP | Disponibilizar recursos e operações necessárias ao fluxo do projeto | Consumo via MCP já integrado ao ambiente Claude do usuário |
| Taskweb | MCP | Acessar capacidades e informações necessárias do ecossistema Taskweb | Integração via MCP |
| MCP | Protocolo / camada de integração | Padronizar a comunicação com ferramentas e serviços externos | Uso como mecanismo principal de integração |
| Claude | Serviço de IA | Apoiar interações e execuções necessárias no fluxo do projeto | Integração com autenticação por token |

---

## Ferramentas de Desenvolvimento

| Ferramenta | Finalidade |
|---|---|
| Terminal | Execução principal do projeto |
| Claude Desktop / ambiente com MCP | Operação das integrações MCP necessárias |
| pip | Instalação e gestão básica de dependências |
| Editor de código à escolha do usuário | Desenvolvimento e manutenção do projeto |
