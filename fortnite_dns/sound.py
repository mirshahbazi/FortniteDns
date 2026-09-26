def play_sound(kind="success"):
    """
    Windows system sounds. Silently does nothing off Windows or if
    the sound subsystem is unavailable.
    """

    try:
        import winsound

        if kind == "success":
            winsound.MessageBeep(
                winsound.MB_ICONASTERISK
            )

        elif kind == "warning":
            winsound.MessageBeep(
                winsound.MB_ICONEXCLAMATION
            )

        elif kind == "error":
            winsound.MessageBeep(
                winsound.MB_ICONHAND
            )

        else:
            winsound.MessageBeep(
                winsound.MB_OK
            )

    except Exception:
        pass
