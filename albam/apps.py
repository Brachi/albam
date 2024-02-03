import os


APPS = [
    ("re0", "Resident Evil 0", "", 0),
    ("re1", "Resident Evil 1", "", 1),
    ("re5", "Resident Evil 5", "", 6),
    ("rev1", "Resident Evil: Revelations 1", "", 8),
    ("rev2", "Resident Evil: Revelations 2", "", 9),
]

REENGINE_APPS = [
    None,
    ("re2", "Resident Evil 2", "", 2),
    ("re2_non_rt", "Resident Evil 2 (dx11 non rt)", "", 3),
    ("re3", "Resident Evil 3", "", 4),
    ("re3_non_rt", "Resident Evil 3 (dx11 non rt)", "", 5),
    ("re8", "Resident Evil 8", "", 7),
]


if os.getenv("ALBAM_ENABLE_REEN"):
    APPS.extend(REENGINE_APPS)
