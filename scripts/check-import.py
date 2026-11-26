#!/usr/bin/env python3
"""Prüft ein OpenBot-Import-Zip gegen die Regeln des Import-Formats.

Aufruf: scripts/check-import.py [pfad/zum.zip]
Ohne Argument wird dist/openbot-orchestrator-lead.zip geprüft.
"""

from __future__ import annotations

import json
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT = ROOT / "dist" / "openbot-orchestrator-lead.zip"

KEY = re.compile(r"^[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$")
SCHEDULE_KINDS = {"hourly", "daily", "weekdays", "weekly", "monthly", "interval", "custom"}
TIME = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")
FORBIDDEN_FILE = re.compile(r"(^|/)\.env|private.*key|\.(zip|tar|gz|7z|rar)$", re.IGNORECASE)

errors: list[str] = []
warnings: list[str] = []


def error(message: str) -> None:
    errors.append(message)


def check(condition: bool, message: str) -> None:
    if not condition:
        error(message)


def check_schedule(schedule: object, where: str) -> None:
    if not isinstance(schedule, dict) or schedule.get("kind") not in SCHEDULE_KINDS:
        error(f"{where}: ungültiger schedule {schedule!r}")
        return
    kind = schedule["kind"]
    if kind in {"daily", "weekdays", "weekly", "monthly"}:
        check(isinstance(schedule.get("time"), str) and TIME.match(schedule["time"]) is not None, f"{where}: Uhrzeit fehlt oder ist ungültig")
    if kind == "hourly":
        minute = schedule.get("minute")
        check(isinstance(minute, int) and 0 <= minute <= 59, f"{where}: minute fehlt")
    if kind == "weekly":
        day = schedule.get("weekday")
        check(isinstance(day, int) and 0 <= day <= 6, f"{where}: weekday fehlt")
    if kind == "monthly":
        day = schedule.get("day")
        check(isinstance(day, int) and 1 <= day <= 31, f"{where}: day fehlt")
    if kind == "interval":
        amount, unit = schedule.get("amount"), schedule.get("unit")
        check(isinstance(amount, int) and amount > 0, f"{where}: amount fehlt")
        check(unit in {"minutes", "hours", "days"}, f"{where}: unit fehlt")


def check_routines(values: object, where: str) -> None:
    if not isinstance(values, list):
        error(f"{where}: Routinen sind keine Liste")
        return
    check(len(values) <= 64, f"{where}: mehr als 64 Routinen")
    for index, routine in enumerate(values):
        label = f"{where} Routine {index + 1}"
        if not isinstance(routine, dict):
            error(f"{label}: ungültig")
            continue
        name = routine.get("name")
        check(isinstance(name, str) and 0 < len(name) <= 80, f"{label}: name fehlt oder ist zu lang")
        instruction = routine.get("instruction")
        check(isinstance(instruction, str) and instruction.strip() != "", f"{label}: instruction fehlt")
        check(isinstance(instruction, str) and len(instruction) <= 100_000, f"{label}: instruction zu lang")
        check(isinstance(routine.get("active"), bool), f"{label}: active fehlt (OpenBot setzt sonst true)")
        check(isinstance(routine.get("timezone"), str) and routine["timezone"] != "", f"{label}: timezone fehlt")
        check_schedule(routine.get("schedule"), label)


def check_frontmatter(text: str, where: str) -> None:
    if not text.startswith("---\n"):
        error(f"{where}: kein YAML-Frontmatter")
        return
    end = text.find("\n---", 4)
    if end == -1:
        error(f"{where}: Frontmatter nicht geschlossen")
        return
    values: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if not line.strip() or line.startswith((" ", "\t")):
            continue
        field, sep, value = line.partition(":")
        if sep:
            values[field.strip()] = value.strip().strip('"').strip("'")
    for field in ("name", "description"):
        if not values.get(field):
            error(f"{where}: Frontmatter ohne {field}")
    if len(values.get("name", "")) > 80:
        error(f"{where}: name über 80 Zeichen")
    if len(values.get("description", "")) > 500:
        error(f"{where}: description über 500 Zeichen")


def main() -> None:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT
    if not path.is_file():
        print(f"FEHLER: {path} fehlt. Erst scripts/build-import.sh ausführen.")
        raise SystemExit(1)

    with zipfile.ZipFile(path) as archive:
        names = [info.filename for info in archive.infolist() if not info.is_dir()]
        check(len(names) <= 200_000, "mehr als 200.000 Dateien")

        for name in names:
            if name.startswith("/") or ".." in Path(name).parts:
                error(f"unsicherer Pfad: {name}")
            if FORBIDDEN_FILE.search(name):
                error(f"verbotene Datei im Zip: {name}")

        if "openbot-import.json" not in names:
            print("FEHLER: openbot-import.json liegt nicht im Wurzelverzeichnis.")
            raise SystemExit(1)

        manifest = json.loads(archive.read("openbot-import.json"))
        check(manifest.get("format") == "openbot-agent-import", "format ist nicht openbot-agent-import")
        check(manifest.get("version") == 1, "version ist nicht 1")
        source = manifest.get("source") or {}
        check(isinstance(source.get("app"), str) and len(source["app"]) <= 64, "source.app fehlt oder ist zu lang")

        agents = manifest.get("agents") or []
        check(len(agents) > 0, "keine Agenten im Manifest")
        keys: set[str] = set()
        files_by_agent: dict[str, list[str]] = {}

        for agent in agents:
            key = agent.get("key", "")
            if not KEY.match(key) or len(key) > 64:
                error(f"ungültiger Agent-Key: {key!r}")
                continue
            if key in keys:
                error(f"doppelter Agent-Key: {key}")
            keys.add(key)

            name = agent.get("name", "")
            check(isinstance(name, str) and 0 < len(name) <= 80, f"{key}: name fehlt oder ist zu lang")
            check(isinstance(agent.get("title", ""), str) and len(agent.get("title", "")) <= 120, f"{key}: title zu lang")
            description = agent.get("description", "")
            check(isinstance(description, str) and description.strip() != "", f"{key}: description fehlt")
            check(isinstance(description, str) and len(description) <= 2000, f"{key}: description über 2000 Zeichen")

            prefix = f"agents/{key}/"
            for field in ("avatar", "files"):
                value = agent.get(field)
                if value is not None:
                    check(isinstance(value, str) and value.startswith(prefix), f"{key}: {field} liegt nicht unter {prefix}")

            skills = agent.get("skills") or []
            check(len(skills) <= 32, f"{key}: mehr als 32 Skills")
            for skill in skills:
                if not isinstance(skill, str) or not skill.startswith(prefix):
                    error(f"{key}: Skill-Pfad außerhalb {prefix}: {skill!r}")
                    continue
                entry = f"{skill}/SKILL.md"
                if entry not in names:
                    error(f"{key}: {entry} fehlt im Zip")
                    continue
                check_frontmatter(archive.read(entry).decode("utf-8"), entry)
                folder_files = [n for n in names if n.startswith(f"{skill}/")]
                check(len(folder_files) <= 200, f"{skill}: mehr als 200 Dateien")

            files_by_agent[key] = names

            memories = agent.get("memories") or []
            check(len(memories) <= 64, f"{key}: mehr als 64 Memories")
            for memory in memories:
                check(isinstance(memory, str) and len(memory) <= 500, f"{key}: Memory zu lang")

            check_routines(agent.get("routines") or [], key)

        for channel in manifest.get("channels") or []:
            key = channel.get("key", "")
            check(KEY.match(key) is not None, f"ungültiger Channel-Key: {key!r}")
            members = channel.get("members") or []
            check(len(members) > 0, f"Channel {key}: keine Mitglieder")
            for member in members:
                check(member in keys, f"Channel {key}: Mitglied {member!r} fehlt im Export")
            lead = channel.get("lead")
            check(lead is None or lead in members, f"Channel {key}: Lead ist kein Mitglied")
            check_routines(channel.get("routines") or [], f"Channel {key}")

    for line in warnings:
        print(f"WARNUNG: {line}")
    if errors:
        for line in errors:
            print(f"FEHLER: {line}")
        print(f"\n{len(errors)} Fehler in {path.name}")
        raise SystemExit(1)
    print(f"OK: {path.name} entspricht dem Import-Format ({len(names)} Dateien).")


if __name__ == "__main__":
    main()
