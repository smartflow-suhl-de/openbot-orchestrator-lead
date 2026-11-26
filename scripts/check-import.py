#!/usr/bin/env python3
"""Check an OpenBot import zip against the rules of the import format.

Usage: scripts/check-import.py [path/to.zip]
Without an argument, dist/openbot-orchestrator-lead.zip is checked.
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
        error(f"{where}: invalid schedule {schedule!r}")
        return
    kind = schedule["kind"]
    if kind in {"daily", "weekdays", "weekly", "monthly"}:
        check(isinstance(schedule.get("time"), str) and TIME.match(schedule["time"]) is not None, f"{where}: time missing or invalid")
    if kind == "hourly":
        minute = schedule.get("minute")
        check(isinstance(minute, int) and 0 <= minute <= 59, f"{where}: minute missing")
    if kind == "weekly":
        day = schedule.get("weekday")
        check(isinstance(day, int) and 0 <= day <= 6, f"{where}: weekday missing")
    if kind == "monthly":
        day = schedule.get("day")
        check(isinstance(day, int) and 1 <= day <= 31, f"{where}: day missing")
    if kind == "interval":
        amount, unit = schedule.get("amount"), schedule.get("unit")
        check(isinstance(amount, int) and amount > 0, f"{where}: amount missing")
        check(unit in {"minutes", "hours", "days"}, f"{where}: unit missing")


def check_routines(values: object, where: str) -> None:
    if not isinstance(values, list):
        error(f"{where}: routines are not a list")
        return
    check(len(values) <= 64, f"{where}: more than 64 routines")
    for index, routine in enumerate(values):
        label = f"{where} routine {index + 1}"
        if not isinstance(routine, dict):
            error(f"{label}: invalid")
            continue
        name = routine.get("name")
        check(isinstance(name, str) and 0 < len(name) <= 80, f"{label}: name missing or too long")
        instruction = routine.get("instruction")
        check(isinstance(instruction, str) and instruction.strip() != "", f"{label}: instruction missing")
        check(isinstance(instruction, str) and len(instruction) <= 100_000, f"{label}: instruction too long")
        check(isinstance(routine.get("active"), bool), f"{label}: active missing (OpenBot otherwise sets true)")
        check(isinstance(routine.get("timezone"), str) and routine["timezone"] != "", f"{label}: timezone missing")
        check_schedule(routine.get("schedule"), label)


def check_frontmatter(text: str, where: str) -> None:
    if not text.startswith("---\n"):
        error(f"{where}: no YAML frontmatter")
        return
    end = text.find("\n---", 4)
    if end == -1:
        error(f"{where}: frontmatter not closed")
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
            error(f"{where}: frontmatter without {field}")
    if len(values.get("name", "")) > 80:
        error(f"{where}: name over 80 characters")
    if len(values.get("description", "")) > 500:
        error(f"{where}: description over 500 characters")


def main() -> None:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT
    if not path.is_file():
        print(f"ERROR: {path} is missing. Run scripts/build-import.sh first.")
        raise SystemExit(1)

    with zipfile.ZipFile(path) as archive:
        names = [info.filename for info in archive.infolist() if not info.is_dir()]
        check(len(names) <= 200_000, "more than 200,000 files")

        for name in names:
            if name.startswith("/") or ".." in Path(name).parts:
                error(f"unsafe path: {name}")
            if FORBIDDEN_FILE.search(name):
                error(f"forbidden file in the zip: {name}")

        if "openbot-import.json" not in names:
            print("ERROR: openbot-import.json is not at the zip root.")
            raise SystemExit(1)

        manifest = json.loads(archive.read("openbot-import.json"))
        check(manifest.get("format") == "openbot-agent-import", "format is not openbot-agent-import")
        check(manifest.get("version") == 1, "version is not 1")
        source = manifest.get("source") or {}
        check(isinstance(source.get("app"), str) and len(source["app"]) <= 64, "source.app missing or too long")

        agents = manifest.get("agents") or []
        check(len(agents) > 0, "no agents in the manifest")
        keys: set[str] = set()
        files_by_agent: dict[str, list[str]] = {}

        for agent in agents:
            key = agent.get("key", "")
            if not KEY.match(key) or len(key) > 64:
                error(f"invalid agent key: {key!r}")
                continue
            if key in keys:
                error(f"duplicate agent key: {key}")
            keys.add(key)

            name = agent.get("name", "")
            check(isinstance(name, str) and 0 < len(name) <= 80, f"{key}: name missing or too long")
            check(isinstance(agent.get("title", ""), str) and len(agent.get("title", "")) <= 120, f"{key}: title too long")
            description = agent.get("description", "")
            check(isinstance(description, str) and description.strip() != "", f"{key}: description missing")
            check(isinstance(description, str) and len(description) <= 2000, f"{key}: description over 2000 characters")

            prefix = f"agents/{key}/"
            for field in ("avatar", "files"):
                value = agent.get(field)
                if value is not None:
                    check(isinstance(value, str) and value.startswith(prefix), f"{key}: {field} is not under {prefix}")

            skills = agent.get("skills") or []
            check(len(skills) <= 32, f"{key}: more than 32 skills")
            for skill in skills:
                if not isinstance(skill, str) or not skill.startswith(prefix):
                    error(f"{key}: skill path outside {prefix}: {skill!r}")
                    continue
                entry = f"{skill}/SKILL.md"
                if entry not in names:
                    error(f"{key}: {entry} missing from the zip")
                    continue
                check_frontmatter(archive.read(entry).decode("utf-8"), entry)
                folder_files = [n for n in names if n.startswith(f"{skill}/")]
                check(len(folder_files) <= 200, f"{skill}: more than 200 files")

            files_by_agent[key] = names

            memories = agent.get("memories") or []
            check(len(memories) <= 64, f"{key}: more than 64 memories")
            for memory in memories:
                check(isinstance(memory, str) and len(memory) <= 500, f"{key}: memory too long")

            check_routines(agent.get("routines") or [], key)

        for channel in manifest.get("channels") or []:
            key = channel.get("key", "")
            check(KEY.match(key) is not None, f"invalid channel key: {key!r}")
            members = channel.get("members") or []
            check(len(members) > 0, f"channel {key}: no members")
            for member in members:
                check(member in keys, f"channel {key}: member {member!r} is missing from the export")
            lead = channel.get("lead")
            check(lead is None or lead in members, f"channel {key}: lead is not a member")
            check_routines(channel.get("routines") or [], f"channel {key}")

    for line in warnings:
        print(f"WARNING: {line}")
    if errors:
        for line in errors:
            print(f"ERROR: {line}")
        print(f"\n{len(errors)} errors in {path.name}")
        raise SystemExit(1)
    print(f"OK: {path.name} matches the import format ({len(names)} files).")


if __name__ == "__main__":
    main()
