# TaskWeb PRO

Hoy, para registrar horas en Taskweb, hay que hacer un montón de pasos a mano: buscar el PBI o bug en Azure, crear una tarea hija con el mismo nombre, asignártela, esperar a que aparezca en Taskweb, y recién ahí cargar el tiempo. Por eso mucha gente se olvida de anotar sus horas.

**TaskWeb PRO automatiza todo eso.** Vos contás qué hiciste (por ejemplo: *"Empecé a desarrollar el PBI 1234112"*) y el sistema:

1. Busca la tarea en Azure DevOps.
2. Si ya existe una tarea hija que sirve, la reutiliza. Si no, la crea y te la asigna.
3. Registra el tiempo en Taskweb (iniciar/parar timer, o cargar un horario puntual).

No reemplaza a Taskweb ni a Azure DevOps — solo te ahorra los pasos manuales.

## Estado actual

| Parte | Estado |
|---|---|
| Buscar / crear / asignar tareas en Azure DevOps | ✅ Listo |
| Registrar horas en Taskweb (timer, horarios) | 🚧 Código listo, esperando que se conecte `taskweb-mcp` |
| Entender lo que escribís en lenguaje natural | ✅ Listo |
| Control de timer desde un comando de texto | 🚧 Código listo, esperando que se conecte `taskweb-mcp` |

## Development

Local setup (Python 3.12):

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/pip install -e .
.venv/bin/python -m pytest
```

### Inspecting local logs

`taskweb_pro` has no external observability stack for the MVP (see
`architecture/tech_stack_context.md.md`). Logs go to stdout via the
standard `logging` module, configured once in
`taskweb_pro/logging_config.py`. To see them when running a command
manually:

```bash
.venv/bin/python -m taskweb_pro.cli <subcommand> ... 2>&1 | cat
```

Logs are `INFO` by default (parent-type validation, compatibility
decisions, create/assignment decisions, Taskweb action results) and
`WARNING`/`ERROR` for rejected input and ambiguous-child-task
anomalies. No log line ever includes credentials or tokens.
