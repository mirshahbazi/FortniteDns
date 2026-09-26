import json
import os

from .constants import CONFIG_FILE


class ConfigStore:
    """
    Everything that touches the on-disk JSON config file. Isolated
    behind a small class (instead of module-level load/save
    functions) so a test can point it at a temp file instead of the
    user's real home directory.
    """

    def __init__(self, path=None):
        self.path = path or CONFIG_FILE

    def load(self):

        try:

            if os.path.exists(self.path):

                with open(
                    self.path,
                    "r",
                    encoding="utf-8"
                ) as f:

                    return json.load(f)

        except Exception:
            pass

        return {}

    def save(self, data):

        try:
            with open(
                self.path,
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    data,
                    f,
                    indent=2,
                    ensure_ascii=False
                )

        except Exception:
            pass

    # ------------------------------------------------------------
    # Custom (manually added) DNS servers
    # ------------------------------------------------------------

    def get_custom_dns(self):

        data = self.load()

        records = []

        for item in data.get("custom_dns", []):

            if (
                isinstance(item, (list, tuple))
                and len(item) >= 2
            ):

                records.append(tuple(item))

        return records

    def set_custom_dns(self, records):

        data = self.load()

        data["custom_dns"] = [
            list(record)
            for record in records
        ]

        self.save(data)

    # ------------------------------------------------------------
    # Pending apply (resumed after a UAC elevation restart)
    # ------------------------------------------------------------

    def pop_pending_apply(self):
        """
        Reads and clears the pending-apply entry in one step, so a
        crash or a second launch can't replay it twice.
        """

        data = self.load()

        pending = data.pop(
            "pending_apply",
            None
        )

        if pending is not None:
            self.save(data)

        return pending

    def set_pending_apply(self, adapter, item):

        data = self.load()

        data["pending_apply"] = {
            "adapter": adapter,
            "item": {
                "name": item["name"],
                "primary": item["primary"],
                "secondary": item.get("secondary", "")
            }
        }

        self.save(data)

    # ------------------------------------------------------------
    # Last applied DNS (for reference / potential "undo" later)
    # ------------------------------------------------------------

    def record_applied(self, adapter, previous_dns, item):

        data = self.load()

        data["adapter"] = adapter

        data["previous_dns"] = previous_dns

        data["applied_dns"] = {
            "name": item["name"],
            "primary": item["primary"],
            "secondary": item.get("secondary", "")
        }

        self.save(data)
