from .utils import is_ipv4, run_command


class WindowsNetworkManager:
    """
    All interaction with Windows network adapters and their DNS
    settings, via PowerShell. Kept behind a class so the UI layer
    (and tests) can depend on an interface rather than module-level
    functions — e.g. a test can subclass this and stub out
    `run_command`-backed behavior without touching a real adapter.
    """

    def get_active_adapters(self):

        command = [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            (
                "Get-NetAdapter | "
                "Where-Object {$_.Status -eq 'Up'} | "
                "Select-Object -ExpandProperty Name"
            )
        ]

        code, stdout, stderr = run_command(
            command
        )

        if code != 0:
            return []

        adapters = []

        for line in stdout.splitlines():

            line = line.strip()

            if line:
                adapters.append(line)

        return adapters

    def get_current_dns(self, adapter):

        command = [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            (
                f"(Get-DnsClientServerAddress "
                f"-InterfaceAlias '{adapter}' "
                f"-AddressFamily IPv4).ServerAddresses"
            )
        ]

        code, stdout, stderr = run_command(
            command
        )

        if code != 0:
            return []

        result = []

        for line in stdout.splitlines():

            line = line.strip()

            if is_ipv4(line):
                result.append(line)

        return result

    def set_dns(self, adapter, primary, secondary):

        servers = [primary]

        if secondary and is_ipv4(secondary):
            servers.append(secondary)

        ps_servers = ",".join(
            f"'{x}'"
            for x in servers
        )

        command = [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            (
                f"Set-DnsClientServerAddress "
                f"-InterfaceAlias '{adapter}' "
                f"-ServerAddresses @({ps_servers})"
            )
        ]

        code, stdout, stderr = run_command(
            command
        )

        if code == 0:

            # Flush DNS cache.
            run_command(
                [
                    "ipconfig",
                    "/flushdns"
                ]
            )

            return True, "DNS applied successfully."

        return False, (
            stderr
            or stdout
            or "Unknown Windows error."
        )

    def clear_dns(self, adapter):

        command = [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            (
                f"Set-DnsClientServerAddress "
                f"-InterfaceAlias '{adapter}' "
                f"-ResetServerAddresses"
            )
        ]

        code, stdout, stderr = run_command(
            command
        )

        if code == 0:

            run_command(
                [
                    "ipconfig",
                    "/flushdns"
                ]
            )

            return True, (
                "DNS was reset to Automatic/DHCP."
            )

        return False, (
            stderr
            or stdout
            or "Could not reset DNS."
        )
