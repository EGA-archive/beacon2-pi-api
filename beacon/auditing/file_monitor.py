
import asyncio
import hashlib
import json
import os
import stat
import pwd

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from beacon.auditing.publisher import AuditPublisher


uid = os.getuid()
username = pwd.getpwuid(uid).pw_name

# Configure these paths for your container.
MONITORED_PATHS = [
    "/beacon/conf/conf.py",
    "/beacon/conf/conf_default.py"
]

# This file must persist across restarts and be protected from the API.
STATE_FILE = Path("/var/lib/permanent_files/state.json")

SCAN_INTERVAL_SECONDS = 5


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def file_snapshot(path_string: str) -> dict[str, Any]:
    """Return a fingerprint of a file without following symlinks."""
    path = Path(path_string)

    try:
        # Get metadata about the file to audit
        info = path.lstat()

        # if the path is a symlink, it records information about the link and returns without trying to hash the target file
        if stat.S_ISLNK(info.st_mode):
            return {
                "status": "symlink",
                "target": os.readlink(path),
                "mode": stat.S_IMODE(info.st_mode),
                "uid": info.st_uid,
                "gid": info.st_gid,
            }

        # if the path is not pointing to a file that has the extension of a modifiable file, return the inormation about it
        if not stat.S_ISREG(info.st_mode):
            return {
                "status": "not_regular_file",
                "target": path,
                "mode": stat.S_IMODE(info.st_mode),
                "uid": info.st_uid,
                "gid": info.st_gid,
            }

        digest = hashlib.sha256()

        # Open without following symlinks if supported by Linux.
        flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
        # Here finally we read the file
        fd = os.open(path, flags)

        try:
            # Get medatadata of the finally opened file
            opened_info = os.fstat(fd)

            # Ensure the opened file is the same object inspected above.
            if (
                opened_info.st_dev != info.st_dev
                or opened_info.st_ino != info.st_ino
                or not stat.S_ISREG(opened_info.st_mode)
            ):
                raise OSError("File changed while being inspected")

            # Hash the file to check the integrity of the file's content in case they change
            with os.fdopen(fd, "rb", closefd=False) as file:
                for chunk in iter(
                    lambda: file.read(1024 * 1024), b""
                ):
                    digest.update(chunk)

            # Check if the file changed while being hashed
            after = os.fstat(fd)

            if (
                after.st_size != opened_info.st_size
                or after.st_mtime_ns != opened_info.st_mtime_ns
                or after.st_ctime_ns != opened_info.st_ctime_ns
            ):
                raise OSError("File changed while being hashed")

        finally:
            os.close(fd)

        return {
            "status": "present",
            "sha256": digest.hexdigest(),
            "size": info.st_size,
            "mode": stat.S_IMODE(info.st_mode),
            "uid": info.st_uid,
            "gid": info.st_gid,
        }

    except FileNotFoundError:
        return {"status": "missing"}

    except (PermissionError, OSError) as exc:
        # Don't interpret an inspection failure as a deletion.
        return {
            "status": "inspection_error",
            "error": type(exc).__name__,
        }


def load_state() -> dict[str, Any] | None:
    try:
        with STATE_FILE.open(encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return None


def save_state(state: dict[str, Any]) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    temp = STATE_FILE.with_suffix(".tmp")

    with temp.open("w", encoding="utf-8") as file:
        json.dump(state, file, sort_keys=True)
        file.flush()
        os.fsync(file.fileno())

    os.replace(temp, STATE_FILE)


def classify_change(
    old: dict[str, Any],
    new: dict[str, Any],
) -> str | None:
    if old == new:
        return None

    old_status = old["status"]
    new_status = new["status"]

    # Inspection errors are not proof of a file change.
    if new_status == "inspection_error":
        return None

    if old_status == "inspection_error":
        return "file.observation_restored"

    if old_status == "missing" and new_status != "missing":
        return "file.created"

    if old_status != "missing" and new_status == "missing":
        return "file.deleted"

    if old_status == "present" and new_status == "present":
        if old.get("sha256") != new.get("sha256"):
            return "file.modified"

        if old != new:
            return "file.metadata_changed"

    if old != new:
        return "file.state_changed"

    return None


def make_event_id(
    path: str,
    old: dict[str, Any],
    new: dict[str, Any],
    event_type: str,
) -> str:
    # Generate a same id for an event with the same parameters to ensure it can't be repeated
    raw = json.dumps(
        [path, event_type, old, new],
        sort_keys=True,
        separators=(",", ":"),
    ).encode()

    return hashlib.sha256(raw).hexdigest()


class FileMonitor:
    def __init__(
        self,
        publisher: AuditPublisher,
        paths: list[str],
        interval: int = SCAN_INTERVAL_SECONDS,
    ):
        self.publisher = publisher
        self.paths = list(dict.fromkeys(
            str(Path(p).absolute()) for p in paths
        ))
        self.interval = interval
        self.state: dict[str, Any] = {}

    async def initialize(self) -> None:
        # First we load the state file of all the files to audit in a python dictionary
        loaded = await asyncio.to_thread(load_state)

        if loaded is None:
            # First run establishes whether the file was already existing or not, etc., not an audit of
            # historical changes. Review files before doing this.
            self.state = {
                path: await asyncio.to_thread(file_snapshot, path)
                for path in self.paths
            }
            await asyncio.to_thread(save_state, self.state)
            return

        self.state = loaded

        # Include paths added to the configuration after startup.
        for path in self.paths:
            if path not in self.state:
                self.state[path] = {"status": "missing"}

    async def scan_once(self) -> None:
        # Work against a copy; commit the new baseline only after
        # all detected events have been published successfully.
        next_state = dict(self.state)

        for path in self.paths:
            old = self.state.get(path, {"status": "missing"})

            new = await asyncio.to_thread(file_snapshot, path)

            if new["status"] == "inspection_error":
                print(
                    f"Cannot inspect monitored file {path}: "
                    f"{new['error']}",
                    flush=True,
                )
                event_type='file.inspection_error'
                event={}
                event["error"] = {
                    "type": "inspection_error",
                    "target": path,
                    "actor": username
                }
            else:

                event_type = classify_change(old, new)
                if event_type is None:
                    # if event type hasn't been classified, discard it (possible corner case errors not related to the file)
                    next_state[path] = new
                    continue

                event_id = make_event_id(path, old, new, event_type)


                event = {

                    "event_id": event_id,

                    "actor": username,

                    "auth": {
                        "method": 'auditd',
                        "uid": uid,
                    },

                    "source": 'localsystem file_monitor',

                    "target": path,

                    "previous_state": old,
                    "current_state": new,
                    "outcome": "observed"
                }



            # Let failures propagate. Do not advance the baseline
            # past a change that wasn't successfully published.
            await self.publisher.publish(event_type, event)

            next_state[path] = new

        await asyncio.to_thread(save_state, next_state)
        self.state = next_state

    async def run(self) -> None:
        await self.initialize()

        while True:
            await self.scan_once()
            await asyncio.sleep(self.interval)


async def main() -> None:
    rabbitmq_url = os.environ["RABBITMQ_URL"]

    publisher = AuditPublisher(rabbitmq_url)
    await publisher.connect()

    monitor = FileMonitor(
        publisher=publisher,
        paths=MONITORED_PATHS,
        interval=SCAN_INTERVAL_SECONDS,
    )

    try:
        await monitor.run()
    finally:
        await publisher.close()


if __name__ == "__main__":
    asyncio.run(main())
