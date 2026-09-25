# Упаковка переносимых скиллов и агентов

Дата исследования: 2026-09-25.

Вопрос: как распространять один набор скиллов, общих справочников и ролей под Claude Code, Codex и OpenCode, в том числе через `npx skills add`, без нескольких вручную поддерживаемых копий.

Ниже отдельно отмечены проверенные файлы, заявления авторов и наши выводы. Установщики и чужие workflow не запускались; проверка исходников не доказывает работоспособность сценария во всех клиентах.

## Сравнение выбранных примеров

Это выборка разных подходов, а не рейтинг или полный обзор экосистемы. Популярность ниже — округлённые счётчики страниц GitHub при просмотре; они меняются и не доказывают качество.

| Репозиторий | Звёзды, примерно | Как хранят роли | Основной способ установки |
|---|---:|---|---|
| [mattpocock/skills](https://github.com/mattpocock/skills) | 269,5 тыс. | Промпты обычным подагентам в скиллах | Claude plugin или `npx skills@latest add mattpocock/skills` |
| [anthropics/skills](https://github.com/anthropics/skills) | 178,2 тыс. | В skill-creator — `agents/*.md` внутри скилла | Наборы через Claude marketplace |
| [obra/superpowers](https://github.com/obra/superpowers) | 291,5 тыс. | Шаблоны обычных подагентов рядом со скиллами | Плагины клиентов, включая Codex/OpenCode |
| [open-gsd/gsd-core](https://github.com/open-gsd/gsd-core) | 9,8 тыс. | Общие `agents/*.md` → преобразование в нативные конфиги | Собственный `npx @opengsd/gsd-core@latest` |

Способы установки и конкретные исходники разобраны ниже. У старого архивного GSD свой счётчик; он не прибавлен к GSD Core.

## mattpocock/skills

### Проверенные факты

**Установка.** README предлагает Claude Code plugin командой `claude plugins install mattpocock-skills` и `npx skills@latest add mattpocock/skills` для Codex и других клиентов. Плагин описан как управляемый пакет, `skills.sh` как редактируемые копии; автор предупреждает о дублировании при использовании обоих способов. После установки запускают `setup-matt-pocock-skills`. [README](https://github.com/mattpocock/skills/blob/main/README.md#installation-30-second-setup).

**Структура.** В полном дереве 38 файлов `SKILL.md`: 18 в `engineering`, 7 в `productivity`, 9 в `in-progress`, 4 в `misc`. Claude-манифест версии 1.2.3 перечисляет только 25 скиллов первых двух групп. Корневых зарегистрированных ролей `agents/`, `.codex/agents/`, `.opencode/agents/` нет. `AGENTS.md` действительно symlink на `CLAUDE.md`: режим Git `120000`. [Дерево GitHub API, tree SHA `c55ee46073ed923f86ce59a5eb3b6d895095d1b7`](https://api.github.com/repos/mattpocock/skills/git/trees/c55ee46073ed923f86ce59a5eb3b6d895095d1b7?recursive=1), [plugin.json](https://github.com/mattpocock/skills/blob/main/.claude-plugin/plugin.json), [AGENTS.md](https://github.com/mattpocock/skills/blob/main/AGENTS.md).

```text
skills/
  engineering/
    code-review/
      SKILL.md
      agents/openai.yaml
    codebase-design/
      SKILL.md
      DEEPENING.md
      DESIGN-IT-TWICE.md
      agents/openai.yaml
  productivity/
  in-progress/
  misc/
.claude-plugin/
.agents/                   # правила разработки репозитория и ADR
scripts/
CLAUDE.md
AGENTS.md -> CLAUDE.md
```

Это структура исходников, не список файлов, автоматически устанавливаемых вместе с отдельным скиллом.

**Подагенты.** `code-review/SKILL.md` запускает двух независимых подагентов параллельно: проверку стандартов и проверку соответствия спецификации. Прямо в скилле описаны их промпты: diff, история коммитов, источники требований, правила и формат результата. Зарегистрированные роли и `subagent_type` не заданы. Аналогично справочник `codebase-design/DESIGN-IT-TWICE.md` запускает 3+ проектировщиков с различными ограничениями в промптах. [code-review](https://github.com/mattpocock/skills/blob/main/skills/engineering/code-review/SKILL.md), [DESIGN-IT-TWICE.md](https://github.com/mattpocock/skills/blob/main/skills/engineering/codebase-design/DESIGN-IT-TWICE.md).

`agents/openai.yaml` внутри скилла описывает метаданные Codex, а не роль подагента: у `code-review` там только отображаемое имя и краткое описание. У пользовательского `implement` дополнительно запрещён неявный запуск через `policy.allow_implicit_invocation: false`. [code-review/openai.yaml](https://github.com/mattpocock/skills/blob/main/skills/engineering/code-review/agents/openai.yaml), [implement/openai.yaml](https://github.com/mattpocock/skills/blob/main/skills/engineering/implement/agents/openai.yaml).

**Общие материалы.** Правило автора: справочники живут внутри скилла-владельца; другим скиллам следует вызвать его по имени через Skill tool, а не открывать файл через `../other-skill/...`. Например, `grill-with-docs` состоит из инструкции вызвать `grilling` и `domain-modeling`. У `codebase-design` справочники находятся рядом с `SKILL.md`. [Правила зависимостей](https://github.com/mattpocock/skills/blob/main/.agents/invocation.md#dependencies-between-them), [grill-with-docs](https://github.com/mattpocock/skills/blob/main/skills/engineering/grill-with-docs/SKILL.md), [codebase-design](https://github.com/mattpocock/skills/blob/main/skills/engineering/codebase-design/SKILL.md).

Проектные настройки setup создаёт в целевом проекте: `docs/agents/issue-tracker.md`, `domain.md` и при необходимости `triage-labels.md`. Шаблоны лежат внутри setup-скилла. Это результат отдельного запуска, не автоматическое действие установщика. [setup-matt-pocock-skills](https://github.com/mattpocock/skills/blob/main/skills/engineering/setup-matt-pocock-skills/SKILL.md).

**Symlink.** `scripts/link-skills.sh` создаёт ссылки на исходные каталоги в `~/.claude/skills` и `~/.agents/skills`, поэтому обновление checkout меняет используемые скиллы. Скрипт явно помечен как dev-only, не поддерживаемый публичный установщик. [link-skills.sh](https://github.com/mattpocock/skills/blob/main/scripts/link-skills.sh).

В ADR автор отложил native Codex plugin: один путь `skills` не позволял выбрать две опубликованные группы без остальных. **По проверке автора**, промежуточная папка из symlink не помогла: при копировании плагина в кэш ссылки терялись. Рассматривались реструктуризация и генерируемая плоская копия; `skills.sh` остался способом установки. Это опыт автора, не наша повторная проверка текущего Codex. [ADR 0002](https://github.com/mattpocock/skills/blob/main/.agents/adr/0002-ship-as-a-claude-code-plugin.md).

**Сборка.** Генератора конфигураций подагентов здесь нет. Есть Changesets, синхронизация версий `package.json` и Claude-манифеста, release workflow для версионных PR и тегов. [package.json](https://github.com/mattpocock/skills/blob/main/package.json), [sync-plugin-version.mjs](https://github.com/mattpocock/skills/blob/main/scripts/sync-plugin-version.mjs), [release.yml](https://github.com/mattpocock/skills/blob/main/.github/workflows/release.yml).

### Ограничения проверки

- Просмотр исходников не подтверждает прогон мультиагентных сценариев во всех клиентах.
- Формулировка Skill tool является соглашением автора, а не доказанным универсальным API. Текущий `implement/SKILL.md` даже сохраняет `/tdd` и `/code-review`, хотя правила рекомендуют явные вызовы инструмента. [implement](https://github.com/mattpocock/skills/blob/main/skills/engineering/implement/SKILL.md), [invocation.md](https://github.com/mattpocock/skills/blob/main/.agents/invocation.md).
- Вызов другого скилла в инструкции не доказывает автоматическую доставку зависимости через `npx skills add` при выборочной установке.
- Проверены публичные исходники `main` и полное дерево GitHub API. Поведение установщиков, права подагентов и перенос symlink локально не проверялись.

### Наши выводы по примеру Matt

Генератор зарегистрированных ролей не является обязательной основой: обычному подагенту можно передать промпт из скилла. Для нашего набора отдельно решить, какие гарантии текущих четырёх ролей существенны: ограничения инструментов, выбор модели, продолжение конкретного исполнителя.

Набор можно распространять через общий `skills/` и Claude-плагин без обязательного native Codex plugin. Но внешние ссылки нашего набора `../_shared/` и `../../agents/` требуют адаптации к выборочной установке. Symlink полезен при разработке; конечную структуру после публичного установщика всё равно нужно проверить.

## anthropics/skills: роли внутри устанавливаемого скилла

Официальный набор Anthropic показывает самодостаточные каталоги скиллов. Особенно полезен пример `skills/skill-creator/`: внутри находятся `SKILL.md`, скрипты, справочники и `agents/grader.md`, `agents/comparator.md`, `agents/analyzer.md`. Главная инструкция предлагает читать соответствующий файл при запуске подагента; это промпты специализированных проверяющих, а не корневые регистрации ролей в каждом клиенте. [SKILL.md](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md#reference-files), [каталог ролей](https://github.com/anthropics/skills/tree/main/skills/skill-creator/agents).

```text
skills/skill-creator/
  SKILL.md
  agents/
    grader.md
    comparator.md
    analyzer.md
  references/
  scripts/
```

README описывает установку наборов через Claude marketplace: `/plugin marketplace add anthropics/skills`, затем, например, `/plugin install example-skills@anthropic-agent-skills`. Манифест выбирает каталоги скиллов явным массивом путей. Это заявление о Claude-установке: наличие переносимого формата само по себе не доказывает поддержку всех шагов skill-creator в Codex или OpenCode. [README](https://github.com/anthropics/skills/blob/main/README.md#claude-code), [marketplace.json](https://github.com/anthropics/skills/blob/main/.claude-plugin/marketplace.json).

**Вывод для нас:** роли, используемые одним workflow, можно включать в его каталог. Тогда установщик отдельного скилла доставит их вместе с остальными ресурсами. Папка `agents/` внутри скилла может содержать обычные промпты; `agents/openai.yaml` имеет другое назначение — метаданные скилла.

## obra/superpowers: общие скиллы, промпты ролей, интеграции клиентов

На момент просмотра Codex-манифест содержит версию 6.4.2 и `"skills": "./skills/"`. Общий каталог используется разными клиентами. Руководство по портированию разделяет содержимое скиллов, соответствие действий инструментам клиента и загрузку начальных инструкций. [Манифест](https://github.com/obra/superpowers/blob/main/.codex-plugin/plugin.json), [руководство](https://github.com/obra/superpowers/blob/main/docs/porting-to-a-new-harness.md).

Самый близкий нам пример — `subagent-driven-development` с `implementer-prompt.md`, `task-reviewer-prompt.md` и `re-review-prompt.md`. Отдельный `requesting-code-review` запускает обычного подагента и передаёт ему шаблон `code-reviewer.md`. [Исполнитель](https://github.com/obra/superpowers/blob/main/skills/subagent-driven-development/implementer-prompt.md), [ревьюер задачи](https://github.com/obra/superpowers/blob/main/skills/subagent-driven-development/task-reviewer-prompt.md), [запуск code-review](https://github.com/obra/superpowers/blob/main/skills/requesting-code-review/SKILL.md).

Авторы прямо описывают устранённое дублирование: персона и чеклист раньше расходились между `agents/code-reviewer.md` и шаблоном скилла. Их объединили в `skills/requesting-code-review/code-reviewer.md`, удалили именованного агента и перешли к обычному подагенту. Поэтому генерация трёх нативных описаний роли здесь не требуется. [Code Review Consolidation](https://github.com/obra/superpowers/blob/main/RELEASE-NOTES.md#code-review-consolidation).

Текущая установка:

| Клиент | Способ, указанный авторами |
|---|---|
| Claude Code | `/plugin install superpowers@claude-plugins-official` |
| Codex | Каталог плагинов; в CLI `/plugins` → Superpowers |
| OpenCode V1 | В конфигурации `"plugin": ["superpowers@git+https://github.com/obra/superpowers.git"]` |
| OpenCode V2 | `"plugins": ["superpowers@git+https://github.com/obra/superpowers.git"]`, требуется V2 2.0.4+ |

Источники: [README](https://github.com/obra/superpowers#installation), [OpenCode INSTALL](https://github.com/obra/superpowers/blob/main/.opencode/INSTALL.md). Команды перечислены как документация проекта; мы их не запускали.

OpenCode-плагин подключает общие скиллы и таблицу соответствия инструментов для конкретного клиента. Его инструкция содержит миграцию со старой установки через clone + symlink на git-backed plugin. Для Codex есть свой документ соответствия инструментов. Это адаптация workflow; сами инструкции стороннего проекта не являются официальной спецификацией API клиента. [OpenCode-плагин](https://github.com/obra/superpowers/blob/main/.opencode/plugins/superpowers.js), [Codex mapping](https://github.com/obra/superpowers/blob/main/skills/using-superpowers/references/codex-tools.md).

Пакет всё же связан: `subagent-driven-development` обращается к соседнему `requesting-code-review` и вызывает другие скиллы. Поэтому установленный отдельно каталог не обязательно даёт весь процесс. `npx skills add` не указан авторами как основной способ полной установки. [Workflow](https://github.com/obra/superpowers/blob/main/skills/subagent-driven-development/SKILL.md), [README](https://github.com/obra/superpowers#installation).

**Вывод для нас:** это прецедент в пользу промптов ролей и небольшого адаптера инструментов. Для связанного набора установка целого плагина сохраняет зависимости. Текстовая инструкция «не редактируй» требует отдельной оценки: она не тождественна принудительному ограничению прав клиента.

## GSD Core: общие исходники и преобразование при установке

Старый `gsd-build/get-shit-done` архивирован и направляет в `open-gsd/gsd-core`. Рассмотрен поддерживаемый преемник, в том числе файлы его ветки `main`; страница репозитория по умолчанию показывает `next`. Эти снимки и npm `latest` не следует считать автоматически одним коммитом. [Архивный проект](https://github.com/gsd-build/get-shit-done), [GSD Core](https://github.com/open-gsd/gsd-core).

```text
agents/*.md
commands/gsd/*.md
gsd-core/workflows/
gsd-core/references/
gsd-core/templates/
bin/install.js
```

Архитектура хранит общие определения агентов и процессов; установщик адаптирует их под клиент. Например, входная команда запуска фазы отсылает к общему workflow, а исполнитель описан одним Markdown-файлом. [Архитектура](https://github.com/open-gsd/gsd-core/blob/main/docs/ARCHITECTURE.md), [execute-phase](https://github.com/open-gsd/gsd-core/blob/main/commands/gsd/execute-phase.md), [gsd-executor](https://github.com/open-gsd/gsd-core/blob/main/agents/gsd-executor.md).

Текущая документированная установка:

```bash
npx @opengsd/gsd-core@latest --claude --global
npx @opengsd/gsd-core@latest --codex --global
npx @opengsd/gsd-core@latest --opencode --global
```

Есть проектный режим `--local`. Авторы объясняют необходимость установщика различием схем и расположения файлов; прямое копирование исходных `agents/` и `commands/` обходит преобразования. Это собственный npm-пакет GSD, а не команда `skills add`. Также документирован дополнительный Claude plugin путь с отличающимися предпосылками и поведением install-time config. [Инструкция установки](https://github.com/open-gsd/gsd-core/blob/main/docs/how-to/install-on-your-runtime.md).

В `bin/install.js` проверены конкретные функции:

- `generateCodexAgentToml`: читает метаданные и тело роли, формирует TOML и настройки sandbox.
- `getCodexSkillAdapterHeader`: добавляет инструкции по адаптации вопросов и делегирования.
- `convertClaudeToOpencodeFrontmatter`: меняет пути, названия инструментов и frontmatter; для агентов удаляет исходное поле `tools`.

Следовательно, преобразование существует в коде, но это не доказывает одинаковые ограничения и поведение во всех клиентах. [Установщик](https://github.com/open-gsd/gsd-core/blob/main/bin/install.js).

**Вывод для нас:** генератор обоснован, если нужны зарегистрированные роли, нативная настройка моделей и разрешений, интеграция конфигов и жизненного цикла. Этот путь существенно шире распространения Markdown-скиллов.

## Что фактически делает npx skills add

README Vercel различает установку через symlink и копирование. В коде `installSkillForAgent` режим symlink сначала копирует `skill.path` в канонический каталог `.agents/skills/<name>`, затем создаёт ссылки для клиентов, которым они нужны. Это общий установленный экземпляр, а не живая ссылка на исходный checkout. Локальное редактирование исходного репозитория само по себе такую копию не обновляет. [README CLI](https://github.com/vercel-labs/skills#installation-methods), [installer.ts](https://github.com/vercel-labs/skills/blob/main/src/installer.ts#L272).

Единица копирования — каталог скилла. Соседний `../_shared/` или корневой `../../agents/` не попадёт внутрь только от упоминания пути в Markdown. Но вложенные symlink-ресурсы обрабатываются иначе: `copyDirectory` вызывает `cp` с `dereference: true, recursive: true`, материализуя доступную цель ссылки; битые ссылки пропускаются с предупреждением. Это найденное поведение текущей ветки `main`, а не результат нашего запуска npm-релиза. [copyDirectory](https://github.com/vercel-labs/skills/blob/main/src/installer.ts#L464).

Необходимо различать:

| Механизм | Что получаем |
|---|---|
| Dev-symlink на checkout, как у Matt | Клиент читает редактируемый исходник |
| Symlink-режим `skills add` | Клиенты используют общую установленную копию |
| Symlink ресурса внутри исходного скилла | Этот CLI превращает доступную цель в обычный файл/каталог при копировании |
| Ссылка в тексте `../other-skill/file.md` | Инструкция чтения; сама по себе ничего не устанавливает |

В `skills add` выбор `--agent codex` означает целевой клиент. Он не означает регистрацию кастомной роли `implementer` из нашего корневого `agents/`. Проверенный парсер находит `SKILL.md`; наличие других скиллов в инструкции не является автоматической установкой зависимостей. [Парсер и discovery](https://github.com/vercel-labs/skills/blob/main/src/skills.ts), [опции CLI](https://github.com/vercel-labs/skills#install-a-skill).

## Что меняется в нашей предварительной рекомендации

Это наши выводы по изученным примерам, а не требования стандарта или готовая миграция.

1. **Не начинать с генератора трёх наборов агентов.** У Matt, Anthropic и Superpowers делегирование работает по модели «обычный подагент + промпт роли». У нас `implementer` и `task-verifier` можно рассмотреть как ресурсы `run-task`, `idea-skeptic` — как ресурс `ai-ideas`. Общему `spec-critic` потребуется явный владелец или способ упаковки для нескольких скиллов.
2. **Сохранить один исходный каталог skills.** Его содержимое потребуется адаптировать: клиентские вызовы, пути, шаблоны и описания. Разделение на три вручную редактируемых копии не требуется.
3. **Выбрать поддерживаемую единицу установки.** Для целого курса удобно сохранить plugin-поставку и общие ресурсы. Для выборочного `npx skills add` каждый выбранный скилл должен получить свои ресурсы и нужные другие скиллы. Нельзя обещать эти варианты эквивалентными до проверки.
4. **Для общих справочников возможны две схемы.** Оформить отдельный скилл-владелец и явно учитывать зависимость, как у Matt; либо хранить один исходный справочник и материализовать его в поставляемых каталогах. Вложенный symlink подходит для проверенной схемы копирования Vercel, но это не универсальное обещание для plugin cache или ZIP-установки.
5. **Разделить текст роли и её принудительные права.** Текущие `spec-critic` и `idea-skeptic` ограничены полем `tools`. Обычный подагент с текстом роли не гарантирует тот же доступ. Если эти ограничения нужны как техническая гарантия, должны остаться нативные настройки клиента; тогда вариант с адаптерами/генератором имеет смысл.
6. **Проверить именно наш цикл.** Свежий тестировщик без истории исполнителя, возврат замечаний тому же исполнителю, запрет правки кода тестировщиком, поиск общих форматов и отсутствие повторного обнаружения скиллов. Эти свойства не следуют из успешной установки файлов.

Первый практический шаг после выбора способа поставки — небольшой пробный перенос `run-task` с двумя ролями и форматом задачи, плюс одного самостоятельного скилла. Проверить целый пакет и выборочную установку в чистых каталогах; затем распространять решение на остальные скиллы. В рамках этого исследования адаптация и установка не выполнялись.
