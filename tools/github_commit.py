#!/usr/bin/env python3
"""Add, change, or delete files on GitHub in one commit.

The Grok GitHub connector can read but not write. GitHub returns
403 Resource not accessible by integration unless the token has
repository Contents: write. A fine-grained personal access token for
only this repo works. Do not paste the token into chat.

  export GITHUB_TOKEN=github_pat_...
  python3 github_commit.py license --dry-run
  python3 github_commit.py license
  python3 github_commit.py commit --message "Update docs" \\
      --put README.md=./README.md \\
      --put tools/github_commit.py=./github_commit.py \\
      --delete OLD.txt
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field

API = "https://api.github.com"
OLD = "MIT licence"
NEW = "GPL 3 (GNU Affero General Public License v3)"


class GitHubError(Exception):
    def __init__(self, message: str, status: int | None = None):
        super().__init__(message)
        self.status = status


@dataclass
class Change:
    path: str
    content: bytes | None = None  # None deletes the file
    mode: str = "100644"


@dataclass
class Client:
    token: str
    owner: str = "anyones2019-cloud"
    repo: str = "Driver-control"
    branch: str = "main"
    opener: object = field(default=urllib.request.urlopen)

    def request(self, method: str, url: str, body: dict | None = None) -> tuple[int, dict, dict]:
        data = None if body is None else json.dumps(body).encode()
        req = urllib.request.Request(
            url,
            data=data,
            method=method,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
                "User-Agent": "github-commit",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )
        try:
            with self.opener(req) as resp:
                raw = resp.read()
                payload = json.loads(raw.decode()) if raw else {}
                return resp.status, payload, dict(resp.headers)
        except urllib.error.HTTPError as err:
            raw = err.read()
            try:
                payload = json.loads(raw.decode()) if raw else {}
            except json.JSONDecodeError:
                payload = {"message": raw.decode(errors="replace")}
            return err.code, payload, dict(err.headers)

    def repo_url(self, suffix: str) -> str:
        owner = urllib.parse.quote(self.owner, safe="")
        repo = urllib.parse.quote(self.repo, safe="")
        return f"{API}/repos/{owner}/{repo}/{suffix}"


def token_from_env() -> str:
    token = (os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or "").strip()
    if not token:
        raise GitHubError(
            "Not signed in. This only works when you are signed in as the repo owner.\n"
            "Set GITHUB_TOKEN to a personal access token for that account, with Contents: Read and write.\n"
            "https://github.com/settings/personal-access-tokens/new"
        )
    return token


def check_path(path: str) -> str:
    raw = path.replace("\\", "/")
    if raw.startswith("/"):
        raise GitHubError(f"Refusing absolute path {path!r}")
    parts = [part for part in raw.split("/") if part not in ("", ".")]
    if not parts or any(part == ".." for part in parts):
        raise GitHubError(f"Refusing path {path!r}")
    return "/".join(parts)


def decode_file(payload: dict) -> bytes:
    if payload.get("type") not in (None, "file"):
        raise GitHubError(f"Path is a {payload.get('type')}, not a file")
    encoding = payload.get("encoding") or "base64"
    content = payload.get("content")
    if not content:
        raise GitHubError("GitHub did not return file bytes. The file may be too large.")
    if encoding == "base64":
        return base64.b64decode(content)
    if encoding == "utf-8":
        return content.encode()
    raise GitHubError(f"Unsupported content encoding {encoding!r}")


def replace_once(text: str, old: str, new: str) -> str | None:
    if old not in text:
        return None
    return text.replace(old, new, 1)


def explain_status(status: int, payload: dict, headers: dict) -> str:
    message = payload.get("message") or "GitHub request failed"
    if status == 403:
        needed = headers.get("X-Accepted-GitHub-Permissions") or headers.get(
            "x-accepted-github-permissions", "contents=write"
        )
        return (
            f"GitHub refused the write (403 {message}).\n"
            f"Required permission: {needed}.\n"
            "A Grok connector token can read this repo and still cannot commit.\n"
            "Create a fine-grained token for Driver-control with Contents: Read and write.\n"
            "https://github.com/settings/personal-access-tokens/new"
        )
    if status == 409:
        return f"GitHub refused the update (409 {message}). The branch moved; run again."
    return f"GitHub HTTP {status}: {message}"


def _ok(status: int, payload: dict, headers: dict) -> dict:
    if status < 200 or status >= 300:
        raise GitHubError(explain_status(status, payload, headers), status)
    return payload


def require_signed_in_owner(client: Client) -> str:
    """Refuse to run unless the token is signed in as the repo owner."""
    status, payload, headers = client.request("GET", f"{API}/user")
    user = _ok(status, payload, headers)
    login = user.get("login") or ""
    if login != client.owner:
        who = login or "nobody"
        raise GitHubError(
            f"Signed in as {who}. This only works when you are signed in as {client.owner}."
        )
    return login


def get_file(client: Client, path: str) -> tuple[bytes, str]:
    path = check_path(path)
    quoted = urllib.parse.quote(path, safe="/")
    status, payload, headers = client.request(
        "GET", client.repo_url(f"contents/{quoted}?ref={urllib.parse.quote(client.branch, safe='')}")
    )
    if isinstance(payload, list) or payload.get("type") == "dir":
        raise GitHubError("Path is a directory, not a file")
    _ok(status, payload, headers)
    return decode_file(payload), payload["sha"]


def commit_changes(client: Client, message: str, changes: list[Change], dry_run: bool = False) -> str | None:
    message = message.strip()
    if not message:
        raise GitHubError("Commit message is empty")
    if not changes:
        raise GitHubError("No files to add, change, or delete")
    normalized: list[Change] = []
    seen: set[str] = set()
    for change in changes:
        path = check_path(change.path)
        if path in seen:
            raise GitHubError(f"Path listed twice: {path}")
        seen.add(path)
        normalized.append(Change(path=path, content=change.content, mode=change.mode))
    require_signed_in_owner(client)

    for change in normalized:
        action = "delete" if change.content is None else "put"
        size = 0 if change.content is None else len(change.content)
        print(f"{action} {change.path}" + ("" if change.content is None else f" ({size} bytes)"))
    if dry_run:
        print("Dry run only. No commit was made.")
        return None

    status, ref, headers = client.request("GET", client.repo_url(f"git/ref/heads/{client.branch}"))
    ref = _ok(status, ref, headers)
    head = ref["object"]["sha"]
    status, commit, headers = client.request("GET", client.repo_url(f"git/commits/{head}"))
    commit = _ok(status, commit, headers)
    tree_sha = commit["tree"]["sha"]

    tree = []
    for change in normalized:
        if change.content is None:
            tree.append({"path": change.path, "mode": change.mode, "type": "blob", "sha": None})
            continue
        status, blob, headers = client.request(
            "POST",
            client.repo_url("git/blobs"),
            {"content": base64.b64encode(change.content).decode("ascii"), "encoding": "base64"},
        )
        blob = _ok(status, blob, headers)
        tree.append({"path": change.path, "mode": change.mode, "type": "blob", "sha": blob["sha"]})

    status, new_tree, headers = client.request(
        "POST", client.repo_url("git/trees"), {"base_tree": tree_sha, "tree": tree}
    )
    new_tree = _ok(status, new_tree, headers)
    body = {"message": message, "tree": new_tree["sha"], "parents": [head]}
    commit_date = os.environ.get("COMMIT_DATE", "").strip()
    if commit_date:
        status, user, headers = client.request("GET", f"{API}/user")
        user = _ok(status, user, headers)
        email = user.get("email") or f"{user.get('id')}+{user.get('login')}@users.noreply.github.com"
        person = {"name": user.get("name") or user.get("login") or client.owner, "email": email, "date": commit_date}
        body["author"] = person
        body["committer"] = person
    status, new_commit, headers = client.request(
        "POST",
        client.repo_url("git/commits"),
        body,
    )
    new_commit = _ok(status, new_commit, headers)
    status, updated, headers = client.request(
        "PATCH", client.repo_url(f"git/refs/heads/{client.branch}"), {"sha": new_commit["sha"], "force": False}
    )
    _ok(status, updated, headers)
    url = new_commit.get("html_url") or new_commit["sha"]
    print(url)
    return url


def license_change(text: str, old: str = OLD, new: str = NEW) -> str:
    updated = replace_once(text, old, new)
    if updated is None:
        if new in text:
            raise GitHubError("already-updated")
        raise GitHubError(f"Did not find {old!r}. Refusing to guess.")
    return updated


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Commit adds, changes, and deletes to GitHub.")
    parser.add_argument("--owner", default="anyones2019-cloud")
    parser.add_argument("--repo", default="Driver-control")
    parser.add_argument("--branch", default="main")
    sub = parser.add_subparsers(dest="command", required=True)

    license_cmd = sub.add_parser("license", help="Change the MIT licence phrase in README.md to GPL 3")
    license_cmd.add_argument("--path", default="README.md")
    license_cmd.add_argument("--old", default=OLD)
    license_cmd.add_argument("--new", default=NEW)
    license_cmd.add_argument("--message", default="Change README licence from MIT to GPL 3")
    license_cmd.add_argument("--dry-run", action="store_true")
    license_cmd.add_argument(
        "--with-tool",
        action="store_true",
        help="Also add this program at tools/github_commit.py in the same commit",
    )

    commit_cmd = sub.add_parser("commit", help="Put and delete files in one commit")
    commit_cmd.add_argument("--message", required=True)
    commit_cmd.add_argument("--put", action="append", default=[], metavar="PATH=LOCAL", help="Add or replace a file")
    commit_cmd.add_argument("--delete", action="append", default=[], metavar="PATH", help="Delete a file")
    commit_cmd.add_argument("--dry-run", action="store_true")
    return parser


def parse_put(spec: str) -> Change:
    if "=" not in spec:
        raise GitHubError(f"--put needs PATH=LOCAL, got {spec!r}")
    path, local = spec.split("=", 1)
    with open(local, "rb") as handle:
        return Change(path=path, content=handle.read())


def client_from_args(args: argparse.Namespace) -> Client:
    return Client(token=token_from_env(), owner=args.owner, repo=args.repo, branch=args.branch)


def main(argv: list[str] | None = None) -> None:
    try:
        sys.stdout.reconfigure(line_buffering=True)
        sys.stderr.reconfigure(line_buffering=True)
    except (AttributeError, OSError):
        pass
    args = build_parser().parse_args(argv)
    try:
        client = client_from_args(args)
        if args.command == "license":
            raw, _sha = get_file(client, args.path)
            try:
                updated = license_change(raw.decode(), args.old, args.new)
            except GitHubError as err:
                if str(err) == "already-updated":
                    print(f"{args.path} already says the new licence text. Nothing to commit.")
                    return
                raise
            print(f"- {args.old}")
            print(f"+ {args.new}")
            changes = [Change(args.path, updated.encode())]
            if args.with_tool:
                with open(__file__, "rb") as handle:
                    changes.append(Change("tools/github_commit.py", handle.read()))
            commit_changes(client, args.message, changes, dry_run=args.dry_run)
            return
        if args.command == "commit":
            changes = [parse_put(spec) for spec in args.put]
            changes.extend(Change(path) for path in args.delete)
            commit_changes(client, args.message, changes, dry_run=args.dry_run)
            return
        raise GitHubError(f"Unknown command {args.command}")
    except GitHubError as err:
        print(str(err), file=sys.stderr)
        raise SystemExit(1) from err


if __name__ == "__main__":
    main()
