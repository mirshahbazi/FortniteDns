"""
Entry point kept at the old filename/location so existing
shortcuts still work. All real logic now lives in the
`fortnite_dns` package (see fortnite_dns/ui/app.py for the Tkinter
app and fortnite_dns/testers.py for the DNS/Fortnite test logic).
"""

from fortnite_dns.app_main import main

if __name__ == "__main__":
    main()
