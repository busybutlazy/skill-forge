#!/usr/bin/env python3
"""
task-plan-core: Hierarchical project task manager
Manages docs/task-plan/task-plan.json (relative to CWD = project root)
"""

import sys
import json
import os
import datetime
import random
import string
import hashlib
from pathlib import Path

TASK_FILE = "docs/task-plan/task-plan.json"
MAX_DEPTH = 3  # order segments: 1, 1.1, 1.1.1


# ─── I/O helpers ─────────────────────────────────────────────────────────────

def load_data():
    if not os.path.exists(TASK_FILE):
        return {
            "version": "1.0",
            "project": os.path.basename(os.getcwd()),
            "updated_at": today(),
            "tasks": []
        }
    with open(TASK_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data):
    os.makedirs(os.path.dirname(TASK_FILE), exist_ok=True)
    data["updated_at"] = today()
    with open(TASK_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def today():
    return datetime.date.today().isoformat()


# ─── ID helpers ───────────────────────────────────────────────────────────────

def gen_id():
    chars = string.ascii_lowercase + string.digits
    return "".join(random.choices(chars, k=8))


def make_unique_id(data):
    existing = set(collect_field(data["tasks"], "id"))
    for _ in range(100):
        candidate = gen_id()
        if candidate not in existing:
            return candidate
    # Fallback: sha256-based
    return hashlib.sha256(os.urandom(16)).hexdigest()[:8]


# ─── Tree traversal ───────────────────────────────────────────────────────────

def collect_field(tasks, field):
    result = []
    for t in tasks:
        result.append(t[field])
        result.extend(collect_field(t.get("subtasks", []), field))
    return result


def flatten(tasks):
    result = []
    for t in tasks:
        result.append(t)
        result.extend(flatten(t.get("subtasks", [])))
    return result


def find_by_id(tasks, task_id):
    for t in tasks:
        if t["id"] == task_id:
            return t
        found = find_by_id(t.get("subtasks", []), task_id)
        if found:
            return found
    return None


def find_by_order(tasks, order):
    for t in tasks:
        if t["order"] == order:
            return t
        found = find_by_order(t.get("subtasks", []), order)
        if found:
            return found
    return None


def delete_by_id(tasks, task_id):
    """Return (new_list, was_deleted)."""
    new_tasks = []
    deleted = False
    for t in tasks:
        if t["id"] == task_id:
            deleted = True
            continue
        new_subs, sub_del = delete_by_id(t.get("subtasks", []), task_id)
        t = {**t, "subtasks": new_subs}
        new_tasks.append(t)
        if sub_del:
            deleted = True
    return new_tasks, deleted


# ─── Display helpers ──────────────────────────────────────────────────────────

STATUS_SYMBOL = {
    "todo":        "[ ]",
    "in_progress": "[~]",
    "done":        "[x]",
    "blocked":     "[!]",
    "skipped":     "[-]",
}

VALID_STATUSES = set(STATUS_SYMBOL.keys())


def sym(status):
    return STATUS_SYMBOL.get(status, "[ ]")


def order_depth(order):
    return order.count(".")


# ─── Commands ─────────────────────────────────────────────────────────────────

def cmd_ls(data, _args):
    all_tasks = flatten(data["tasks"])
    if not all_tasks:
        print("No tasks. Use: task-plan add -id <order> <title> [description]")
        return
    print(f"{'ORDER':<12} {'ID':<10} {'ST':<5} TITLE")
    print("─" * 62)
    for t in all_tasks:
        indent = "  " * order_depth(t["order"])
        print(f"{t['order']:<12} {t['id']:<10} {sym(t['status']):<5} {indent}{t['title']}")


def cmd_add(data, args):
    # task-plan add -id <order> <title> [description]
    if len(args) < 3 or args[0] != "-id":
        print("Usage: task-plan add -id <order> <title> [description]")
        sys.exit(1)

    order = args[1]
    title = args[2]
    description = args[3] if len(args) > 3 else ""

    # Validate order format
    parts = order.split(".")
    if not all(p.isdigit() and p != "" for p in parts):
        print(f"Error: order '{order}' must be dot-separated integers (e.g. 1, 1.2, 1.2.3).")
        sys.exit(1)

    if len(parts) > MAX_DEPTH:
        print(f"Error: maximum task depth is {MAX_DEPTH} levels (e.g. 1.2.3). Got {len(parts)} levels.")
        sys.exit(1)

    # Collision check
    existing_orders = collect_field(data["tasks"], "order")
    if order in existing_orders:
        occupant = find_by_order(data["tasks"], order)
        print(f"Warning: position '{order}' is already occupied.")
        print(f"  Existing: [{occupant['id']}] {occupant['title']} ({occupant['status']})")
        print(f"  To review   : task-plan check -id {occupant['id']}")
        print(f"  To relocate : task-plan update -id {occupant['id']} -o <new_order>")
        sys.exit(1)

    new_task = {
        "id": make_unique_id(data),
        "order": order,
        "title": title,
        "description": description,
        "status": "todo",
        "completion_note": "",
        "created_at": today(),
        "updated_at": today(),
        "subtasks": [],
    }

    if len(parts) == 1:
        data["tasks"].append(new_task)
    else:
        parent_order = ".".join(parts[:-1])
        parent = find_by_order(data["tasks"], parent_order)
        if parent is None:
            print(f"Error: parent task at '{parent_order}' does not exist. Create it first.")
            sys.exit(1)
        parent["subtasks"].append(new_task)

    save_data(data)
    print(f"Added [{new_task['id']}] at {order}: {title}")


def cmd_done(data, args):
    # task-plan done -id <task_id> [note]
    if len(args) < 2 or args[0] != "-id":
        print("Usage: task-plan done -id <task_id> [completion_note]")
        sys.exit(1)

    task_id = args[1]
    note = args[2] if len(args) > 2 else ""

    task = find_by_id(data["tasks"], task_id)
    if task is None:
        print(f"Error: task '{task_id}' not found.")
        sys.exit(1)

    task["status"] = "done"
    task["completion_note"] = note
    task["updated_at"] = today()

    save_data(data)
    print(f"Done: [{task_id}] {task['title']}")
    if note:
        print(f"  Note: {note}")


def cmd_check(data, args):
    if args and args[0] == "-id":
        # Single task detail
        if len(args) < 2:
            print("Usage: task-plan check -id <task_id>")
            sys.exit(1)
        task_id = args[1]
        task = find_by_id(data["tasks"], task_id)
        if task is None:
            print(f"Error: task '{task_id}' not found.")
            sys.exit(1)
        print(f"Order   : {task['order']}")
        print(f"ID      : {task['id']}")
        print(f"Title   : {task['title']}")
        print(f"Status  : {task['status']} {sym(task['status'])}")
        print(f"Note    : {task['completion_note'] or '(none)'}")
        print(f"Detail  : {task['description'] or '(none)'}")
        print(f"Created : {task['created_at']}")
        print(f"Updated : {task['updated_at']}")
        if task.get("subtasks"):
            print(f"Subtasks: {len(task['subtasks'])} direct child(ren)")
    else:
        # Full status overview
        all_tasks = flatten(data["tasks"])
        if not all_tasks:
            print("No tasks found.")
            return

        done_tasks = [t for t in all_tasks if t["status"] == "done"]
        last_done = done_tasks[-1] if done_tasks else None

        print(f"{'ORDER':<12} {'ID':<10} {'STATUS':<12} TITLE")
        print("─" * 72)
        for t in all_tasks:
            indent = "  " * order_depth(t["order"])
            note_suffix = ""
            if t["completion_note"]:
                note_suffix = f"  — {t['completion_note'][:40]}"
            label = f"{sym(t['status'])} {t['status']}"
            print(f"{t['order']:<12} {t['id']:<10} {label:<12} {indent}{t['title']}{note_suffix}")

        total = len(all_tasks)
        n_done = len(done_tasks)
        print()
        print(f"Progress: {n_done}/{total} done")
        if last_done:
            print(f"Last completed: [{last_done['id']}] {last_done['title']}")
            if last_done["completion_note"]:
                print(f"  Note: {last_done['completion_note']}")


def cmd_detail(data, args):
    # task-plan detail -id <task_id> <description>
    if len(args) < 3 or args[0] != "-id":
        print("Usage: task-plan detail -id <task_id> <description>")
        sys.exit(1)

    task_id = args[1]
    description = args[2]

    task = find_by_id(data["tasks"], task_id)
    if task is None:
        print(f"Error: task '{task_id}' not found.")
        sys.exit(1)

    task["description"] = description
    task["updated_at"] = today()

    save_data(data)
    print(f"Updated detail for [{task_id}] '{task['title']}'.")


def cmd_del(data, args):
    # task-plan del -id <task_id>
    if len(args) < 2 or args[0] != "-id":
        print("Usage: task-plan del -id <task_id>")
        sys.exit(1)

    task_id = args[1]
    task = find_by_id(data["tasks"], task_id)
    if task is None:
        print(f"Error: task '{task_id}' not found.")
        sys.exit(1)

    title = task["title"]
    subtask_count = len(flatten(task.get("subtasks", [])))

    new_tasks, deleted = delete_by_id(data["tasks"], task_id)
    if not deleted:
        print(f"Error: could not delete '{task_id}'.")
        sys.exit(1)

    data["tasks"] = new_tasks
    save_data(data)
    msg = f"Deleted [{task_id}] '{title}'"
    if subtask_count:
        msg += f" (and {subtask_count} subtask(s))"
    print(msg + ".")


def cmd_update(data, args):
    # task-plan update -id <task_id> [-o <order>] [-state <status>] [-detail <desc>]
    if not args or args[0] != "-id":
        print("Usage: task-plan update -id <task_id> [-o <order>] [-state <status>] [-detail <description>]")
        sys.exit(1)

    if len(args) < 2:
        print("Error: task_id required after -id.")
        sys.exit(1)

    task_id = args[1]
    task = find_by_id(data["tasks"], task_id)
    if task is None:
        print(f"Error: task '{task_id}' not found.")
        sys.exit(1)

    i = 2
    new_order = None
    new_state = None
    new_detail = None

    while i < len(args):
        flag = args[i]
        if flag == "-o" and i + 1 < len(args):
            new_order = args[i + 1]
            i += 2
        elif flag == "-state" and i + 1 < len(args):
            new_state = args[i + 1]
            i += 2
        elif flag == "-detail" and i + 1 < len(args):
            new_detail = args[i + 1]
            i += 2
        else:
            print(f"Warning: unknown flag '{flag}', skipping.")
            i += 1

    if new_order is None and new_state is None and new_detail is None:
        print("No changes specified. Available flags: -o <order>  -state <status>  -detail <description>")
        sys.exit(0)

    changed = []

    if new_order is not None:
        existing_orders = collect_field(data["tasks"], "order")
        if new_order in existing_orders and new_order != task["order"]:
            occupant = find_by_order(data["tasks"], new_order)
            print(f"Warning: position '{new_order}' is already occupied by [{occupant['id']}] '{occupant['title']}'.")
            print(f"  Move that task first: task-plan update -id {occupant['id']} -o <other_order>")
            sys.exit(1)
        parts = new_order.split(".")
        if not all(p.isdigit() and p != "" for p in parts):
            print(f"Error: order '{new_order}' must be dot-separated integers.")
            sys.exit(1)
        if len(parts) > MAX_DEPTH:
            print(f"Error: maximum depth is {MAX_DEPTH} levels.")
            sys.exit(1)
        task["order"] = new_order
        changed.append(f"order → {new_order}")

    if new_state is not None:
        if new_state not in VALID_STATUSES:
            print(f"Error: invalid status '{new_state}'. Must be one of: {', '.join(sorted(VALID_STATUSES))}")
            sys.exit(1)
        task["status"] = new_state
        changed.append(f"status → {new_state}")

    if new_detail is not None:
        task["description"] = new_detail
        changed.append("description updated")

    task["updated_at"] = today()
    save_data(data)
    print(f"Updated [{task_id}] '{task['title']}': {', '.join(changed)}")


# ─── Help ─────────────────────────────────────────────────────────────────────

HELP = """\
task-plan — Hierarchical project task manager
File: docs/task-plan/task-plan.json (auto-created on first add)

COMMANDS
  ls
      List all tasks: order, id, status, title

  add -id <order> <title> [description]
      Add a task at the given hierarchy position.
      order uses dot-notation: 1  |  1.2  |  1.2.3  (max 3 levels)
      Warns and aborts if position is already occupied.

  done -id <task_id> [completion_note]
      Mark a task as done. Optionally record what was completed.

  check
      Overview of all tasks with status and last completed task.

  check -id <task_id>
      Full detail for one task.

  detail -id <task_id> <description>
      Update the description / goal of a task.

  del -id <task_id>
      Delete a task and all its subtasks.

  update -id <task_id> [options]     (all options optional)
      -o <order>            Move task to a new position
      -state <status>       Set status: todo | in_progress | done | blocked | skipped
      -detail <description> Replace description

STATUS VALUES
  [ ] todo        Task not started
  [~] in_progress Task is being worked on
  [x] done        Task completed
  [!] blocked     Task is blocked
  [-] skipped     Task deliberately skipped

IDs
  task_id: auto-generated 8-char alphanumeric, unique within the file
  order:   dot-notation position you assign (determines hierarchy)
"""


# ─── Entry point ─────────────────────────────────────────────────────────────

def _check_project_root():
    cwd = Path(os.getcwd())
    has_git = (cwd / ".git").exists()
    has_docs = (cwd / "docs").exists()
    has_task_file = (cwd / TASK_FILE).exists()
    if not has_git and not has_docs and not has_task_file:
        print(
            f"Warning: current directory does not look like a project root: {cwd}\n"
            "  Expected '.git', 'docs/', or 'docs/task-plan/task-plan.json' here.\n"
            "  Run this script from the project root.",
            file=sys.stderr,
        )


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("help", "--help", "-h"):
        print(HELP)
        return

    command = args[0]
    rest = args[1:]

    _check_project_root()
    data = load_data()

    dispatch = {
        "ls":     cmd_ls,
        "add":    cmd_add,
        "done":   cmd_done,
        "check":  cmd_check,
        "detail": cmd_detail,
        "del":    cmd_del,
        "update": cmd_update,
    }

    if command not in dispatch:
        print(f"Error: unknown command '{command}'.")
        print("Run 'task-plan help' for usage.")
        sys.exit(1)

    dispatch[command](data, rest)


if __name__ == "__main__":
    main()
