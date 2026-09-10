# Restrições e Decisões Técnicas

## Tecnologias Proibidas

> Liste tecnologias, bibliotecas, frameworks ou abordagens que não devem ser usados neste projeto, independentemente do contexto.

| O que não usar | Motivo | Alternativa recomendada |
|---|---|---|
| Frameworks frontend | O MVP não prevê interface gráfica ou camada web de apresentação | Execução por terminal / CLI em Python |
| Frameworks backend completos desnecessários | O projeto não precisa de servidor web nem estrutura pesada para o MVP | Scripts ou aplicação leve em Python sem framework |
| Banco de dados | O escopo atual não exige persistência estruturada | Fluxo sem persistência local ou remota |

---

## Restrições de Ambiente

> Limitações impostas pelo ambiente do cliente, infraestrutura existente ou políticas da organização.

| Restrição | Descrição | Impacto no projeto |
|---|---|---|
| Execução somente local | O sistema deve rodar localmente em terminal | Não considerar deploy em servidor ou cloud no MVP |
| Sem Docker | O ambiente não prevê conteinerização neste momento | Setup e execução devem funcionar diretamente no ambiente local |
| Sem banco de dados | Não há infraestrutura nem necessidade prevista para persistência | Arquitetura deve evitar dependência de storage relacional ou NoSQL |

---

## Restrições de Segurança e Compliance

> Requisitos obrigatórios de segurança, privacidade ou regulação que condicionam as decisões técnicas.

| Requisito | Descrição | Como é atendido |
|---|---|---|
| Proteção de tokens e credenciais | Tokens, senhas e outros segredos não podem ficar expostos no código-fonte ou em arquivos inseguros | Uso de variáveis de ambiente ou mecanismo seguro equivalente para injeção de segredos |
| Autenticação por token | Integrações que exigirem autenticação devem utilizar token de acesso | Configuração segura de credenciais no ambiente de execução local |

---

## Decisões Tomadas e Não Reverter

> Escolhas técnicas já feitas e consolidadas que não devem ser questionadas sem um ADR. Diferente de proibições — são decisões que já custaram tempo e que reverter teria custo alto.

| Decisão | Contexto | Por que não reverter |
|---|---|---|
| Execução via terminal no MVP | Definido para manter a solução simples e aderente ao problema inicial | Introduzir interface gráfica ou web mudaria escopo, esforço e arquitetura |
| Integrações obrigatórias via MCP | Definido como mecanismo principal de conexão com Azure, Taskweb e demais componentes externos | Mudar o padrão de integração exigiria redesenho técnico do fluxo principal |
| Ausência de frontend no MVP | Decisão alinhada ao uso operacional previsto neste estágio inicial | Adicionar frontend criaria nova camada técnica sem necessidade atual |
