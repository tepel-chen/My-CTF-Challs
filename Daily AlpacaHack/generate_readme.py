#!/home/tchen/venv/bin/python

from __future__ import annotations

import argparse
import re
from pathlib import Path
from urllib.parse import quote

import yaml


SUMMARY_RE = re.compile(r"<summary>(.*?)</summary>")


def trim_blank_lines(lines: list[str]) -> list[str]:
    start = 0
    end = len(lines)

    while start < end and not lines[start].strip():
        start += 1
    while end > start and not lines[end - 1].strip():
        end -= 1

    return lines[start:end]


def normalize_blank_lines(lines: list[str]) -> list[str]:
    normalized: list[str] = []
    previous_blank = False

    for line in lines:
        is_blank = not line.strip()
        if is_blank and previous_blank:
            continue
        normalized.append("" if is_blank else line.rstrip())
        previous_blank = is_blank

    return trim_blank_lines(normalized)


def render_description(description: str) -> str:
    lines = description.strip().splitlines()
    output: list[str] = []
    index = 0

    while index < len(lines):
        current = lines[index].rstrip()
        stripped = current.strip()

        if stripped == "<details>":
            index += 1
            while index < len(lines) and not lines[index].strip():
                index += 1

            if index >= len(lines):
                break

            match = SUMMARY_RE.fullmatch(lines[index].strip())
            if match is None:
                raise ValueError(f"Invalid summary line: {lines[index]!r}")

            title = match.group(1)
            body: list[str] = []
            index += 1

            while index < len(lines) and lines[index].strip() != "</details>":
                body.append(lines[index].rstrip())
                index += 1

            body = trim_blank_lines(body)

            if output and output[-1] != "":
                output.append("")
            output.append(f"### {title}")
            if body:
                output.append("")
                output.extend(body)
            output.append("")

            if index < len(lines) and lines[index].strip() == "</details>":
                index += 1
            continue

        output.append(current)
        index += 1

    return "\n".join(normalize_blank_lines(output))


def build_readme(
    *,
    name: str,
    description_heading: str,
    description: str,
    writeup_heading: str,
    flag_heading: str,
    flag: str,
    language_link: str,
) -> str:
    parts = [
        f"# {name}",
        "",
        language_link,
        "",
        f"## {description_heading}",
        "",
        render_description(description),
        "",
        f"## {writeup_heading}",
        "",
        f"## {flag_heading}",
        "",
        f"`{flag}`",
    ]

    return "\n".join(parts).rstrip() + "\n"


def to_title_category(category: str) -> str:
    mapping = {
        "web": "Web",
        "misc": "Misc",
        "rev": "Rev",
        "crypto": "Crypto",
        "pwn": "Pwn",
        "forensics": "Forensics",
    }
    return mapping.get(category.lower(), category.title())


def encode_path_for_link(path: Path) -> str:
    return "/" + "/".join(quote(part) for part in path.parts)


def upsert_table_row(lines: list[str], row: str, row_match: str, insert_at: int) -> list[str]:
    for index, line in enumerate(lines):
        if row_match in line:
            lines[index] = row
            return lines

    lines.insert(insert_at, row)
    return lines


def update_daily_readme(*, readme_path: Path, category: str, name: str, challenge_link: str, website: str) -> None:
    lines = readme_path.read_text(encoding="utf-8").splitlines()
    row = f"|{category}|[{name}]({challenge_link})|[Link]({website})|"
    row_match = f"[{name}]({challenge_link})"

    insert_at = 4 if len(lines) >= 4 else len(lines)
    updated = upsert_table_row(lines, row, row_match, insert_at)
    readme_path.write_text("\n".join(updated) + "\n", encoding="utf-8")


def update_root_readme(
    *,
    readme_path: Path,
    category: str,
    name: str,
    challenge_link: str,
    difficulty: str,
) -> None:
    lines = readme_path.read_text(encoding="utf-8").splitlines()
    row_match = f"[{name}]({challenge_link})"
    section_header = f"## {category}"

    section_start = None
    for index, line in enumerate(lines):
        if line.strip() == section_header:
            section_start = index
            break

    if section_start is None:
        raise ValueError(f"Section not found in {readme_path}: {section_header}")

    insert_at = section_start + 3
    for index in range(section_start + 1, len(lines)):
        if lines[index].startswith("## "):
            break

    for index, line in enumerate(lines):
        if row_match not in line:
            continue

        parts = line.split("|")
        existing_difficulty = parts[3] if len(parts) > 3 else ""
        row = f"|Daily AlpacaHack|[{name}]({challenge_link})|{difficulty or existing_difficulty}|"
        lines[index] = row
        readme_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return

    row = f"|Daily AlpacaHack|[{name}]({challenge_link})|{difficulty}|"
    lines.insert(insert_at, row)
    readme_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", default="task.yml")
    parser.add_argument("--output-dir", default=".")
    args = parser.parse_args()

    task_path = Path(args.task)
    output_dir = Path(args.output_dir)
    readme_en_path = output_dir / "README.md"
    readme_ja_path = output_dir / "README-ja.md"
    repo_dir = Path(__file__).resolve().parent
    root_readme_path = repo_dir.parent / "README.md"
    daily_readme_path = repo_dir / "README.md"

    task = yaml.safe_load(task_path.read_text(encoding="utf-8"))
    category = to_title_category(task["categories"][0])
    challenge_dir = output_dir.resolve().relative_to(repo_dir.resolve())
    challenge_link = encode_path_for_link(repo_dir.name and Path(repo_dir.name) / challenge_dir)
    website = f"https://alpacahack.com/daily/challenges/{task['canonicalName']}"
    difficulty = task.get("difficulty", "★")

    readme_en = build_readme(
        name=task["name"],
        description_heading="Description",
        description=task["description"],
        writeup_heading="Writeup",
        flag_heading="Flag",
        flag=task["flag"],
        language_link="[日本語はこちら](./README-ja.md)",
    )
    readme_ja = build_readme(
        name=task["name"],
        description_heading="問題文",
        description=task["descriptionJa"],
        writeup_heading="Writeup",
        flag_heading="フラグ",
        flag=task["flag"],
        language_link="[English](./README.md)",
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    readme_en_path.write_text(readme_en, encoding="utf-8")
    readme_ja_path.write_text(readme_ja, encoding="utf-8")
    update_daily_readme(
        readme_path=daily_readme_path,
        category=category,
        name=task["name"],
        challenge_link=challenge_link,
        website=website,
    )
    update_root_readme(
        readme_path=root_readme_path,
        category=category,
        name=task["name"],
        challenge_link=challenge_link,
        difficulty=difficulty,
    )


if __name__ == "__main__":
    main()
