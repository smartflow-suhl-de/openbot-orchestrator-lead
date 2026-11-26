# Orchestrator Lead für OpenBot

Importierbares Agenten-Paket für einen selbst gehosteten OpenBot-Server: die
veröffentlichten Instruktionen, sieben Skills und zwei pausierte Routinen als
ein Zip, das OpenBot unter **Server-Einstellungen → Importieren** einliest.

Ein Agent, ein Zweck: Software-Auslieferung über spezialisierte Subagenten
(SPEC, Worker, QA, Code Review, Security Review, Incident RCA) hinweg
orchestrieren, statt einen großen Coding-Chat zu führen. Merges, Deploys und
Store-Veröffentlichungen bleiben beim Owner.

## Herkunft

Der Agent wurde von **Fellipe** als öffentliche Share-Seite veröffentlicht und
am 26.11.2026 von dort übernommen:

- Share-Seite: <https://openbot.run/agents/xwDzXa5f7bdgNuenppquGQ>
- Stand der Vorlage: 2026-11-24T19:48:18Z

Das Repo ist eine Arbeitskopie für Import, Pflege und Weitergabe im eigenen
Server, keine eigene Erfindung und kein Marketplace-Listing. Rechte am Text
liegen beim Autor; die OpenBot-App selbst steht unter PolyForm Noncommercial
1.0.0. Nicht als eigenes Produkt ausgeben.

Nicht Teil der Share-Seite und damit auch nicht hier: der private
System-Prompt, Modell-Einstellungen, Gespräche und Workspace-Dateien des
Erstellers.

## Was drin ist

| Pfad | Inhalt |
|---|---|
| `AGENT.md` | die veröffentlichte Agenten-Beschreibung (Quelle für `description` im Import) |
| `skills/orchestrator-lead-getting-started/` | Erstgespräch: Name, Sprache, Harness, Modell-Matrix pro Rolle, Repos, PR-Normen, Zeitzone, Routinen |
| `skills/multi-model-spec/` | SPEC-Subagent, read-only: Recherche, Architektur, prüfbarer Plan |
| `skills/multi-model-worker/` | Worker im eigenen Git-Worktree: Umsetzung, Simplify Pass, Verifikation, JSON-Handoff |
| `skills/multi-model-qa/` | diff-getriebene Funktionsprüfung an der echten Oberfläche mit Vorher/Nachher-Beleg |
| `skills/multi-model-code-review/` | zweistufiges P0–P3-Review, Inline-Kommentare oder kurzes LGTM, nie ein Approval |
| `skills/multi-model-security-review/` | STRIDE, OWASP Top 10 + LLM Top 10, Supply Chain, `[security]`-Kommentare P0–P3 |
| `skills/multi-model-incident-rca/` | read-only Ursachenanalyse aus CI-, Sentry- oder Prod-Alarme |
| `routines/issues-prs-daily-chase.txt` | Routine „Issues & PRs Daily Chase“, Mo–Fr 09:00, pausiert |
| `routines/ci-dependencies-errors-watch.txt` | Routine „CI, Dependencies & Errors Watch“, Mo–Fr 14:00, pausiert |
| `import/openbot-import.json` | generiertes Manifest des Import-Pakets |
| `dist/openbot-orchestrator-lead.zip` | fertiges Import-Paket |
| `scripts/build-import.py` | baut Manifest und Zip aus den Dateien oben, prüft die Formatgrenzen |
| `scripts/check-import.py` | prüft ein fertiges Zip gegen die Import-Regeln |

Quelle der Wahrheit sind `AGENT.md`, `skills/` und `routines/`. Das Manifest
und das Zip werden daraus gebaut und nicht von Hand gepflegt.

## Bauen

```bash
./scripts/build-import.sh
./scripts/check-import.py
```

Ergebnis: `dist/openbot-orchestrator-lead.zip` mit
`openbot-import.json` und `agents/orchestrator-lead/skills/…` im
Wurzelverzeichnis, so wie OpenBot es erwartet.

## In OpenBot installieren

Der Import läuft auf dem OpenBot-Rechner, nichts wird hochgeladen.

1. `dist/openbot-orchestrator-lead.zip` auf den Rechner kopieren, auf dem
   OpenBot läuft (oder die Datei dort herunterladen).
2. In OpenBot **Server-Einstellungen → Importieren** öffnen.
3. **Datei wählen…**, das Zip auswählen und den angezeigten Agenten
   „Orchestrator Lead“ importieren.
4. OpenBot legt eine Kopie an: Instruktionen, die sieben Skills und die zwei
   Routinen. Nicht übernommen werden Gespräche, Erinnerungen, Modell,
   Provider und Workspace-Dateien des Erstellers.

Ein zweiter Import derselben Datei überschreibt die vorhandene Kopie nicht,
sondern legt eine weitere an (bzw. benennt kollidierende Skills um). Vorher
entscheiden, ob die alte Kopie gelöscht werden soll.

### Nach dem Import

1. **Modell und Provider setzen.** Neue Agenten starten sonst leicht auf
   `codex`; ohne ChatGPT-Login scheitert der erste Turn. Für den Anfang
   `provider: opencode` mit einem im Katalog vorhandenen Modell und
   passendem Reasoning-Effort wählen, dazu ein Backup-Modell.
2. **Zugänge freigeben, aber nur die nötigen.** Der Agent erwartet GitHub
   (`gh` oder GitHub-MCP), einen Issue-Tracker und optional Sentry/MCP für
   Incident RCA. MCP-Server werden serverweit definiert und pro Agent
   freigegeben; `computerUse` nur, wenn wirklich eine GUI gebraucht wird.
3. **Routinen pausiert lassen**, bis ein Owner und ein echter Bedarf da sind,
   und die Zeitzone prüfen: das Paket bringt `Europe/Berlin` mit
   (`routines/` und `scripts/build-import.py`).
4. **Erstgespräch führen.** Der erste echte Turn startet
   `orchestrator-lead-getting-started`: Name, Sprache, Harness (OpenCode,
   Paseo, Orca, T3 Code oder eigene CLIs), Modell-Matrix pro Rolle, Repos,
   PR-Normen, Zeitzone. Daraus schreibt der Agent sein `AGENTS.md` in den
   Workspace.
5. **Klein testen.** Eine kleine echte Aufgabe über SPEC → Worker → QA →
   Review laufen lassen und am Artefakt prüfen, bevor der Agent in einen
   Kanal oder eine Routine kommt.
6. **Grenzen bestätigen.** Kein Merge, Deploy oder Store-Release ohne
   ausdrückliche schriftliche Freigabe des Owners im Chat; ein OK eines
   anderen Agenten zählt nicht.

### Ohne Zip installieren

1. Repo in den Workspace des Agenten klonen, z. B. nach
   `Agents/<name>/openbot-orchestrator-lead`.
2. `AGENT.md` als Agenten-Beschreibung einsetzen (Text ab „You are
   Orchestrator Lead …“; maximal 2.000 Zeichen).
3. Dem Agenten den Auftrag geben, die sieben Ordner aus `skills/` mit seinen
   lokalen Skill-Werkzeugen (`create_skill`) zu registrieren. Nicht die
   installierten Kopien unter `.agents/skills` von Hand überschreiben.
4. Routinen aus `routines/` von Hand anlegen, pausiert, Mo–Fr 09:00 bzw.
   14:00 in der eigenen Zeitzone.

## Pflege

- Skill-Text ändern: `skills/<name>/SKILL.md` bearbeiten (Frontmatter `name`
  muss zum Ordnernamen passen), dann `./scripts/build-import.sh` und
  `./scripts/check-import.py`.
- Routine ändern: Datei in `routines/` bearbeiten; Name, Uhrzeit und
  Zeitzone stehen in `scripts/build-import.py`.
- Neue Fassung einspielen: neu bauen, importieren, danach erneut testen.
  Keine ungetestete Aktualisierung in einem laufenden Kanal.

Grenzen des Formats, die das Skript prüft: Agenten-Beschreibung 2.000
Zeichen, Name 80, Titel 120, 32 Skills je Agent, 64 Routinen, 80 Zeichen
Routinenname, 200 Dateien je Skill-Ordner, keine `.env`-Dateien, Schlüssel
oder verschachtelten Archive im Zip.
