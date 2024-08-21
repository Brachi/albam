import os


APPS = [
    ("re0", "Resident Evil 0", "", 0),
    ("re1", "Resident Evil 1", "", 1),
    ("re5", "Resident Evil 5", "", 2),
    ("re6", "Resident Evil 6", "", 3),
    ("rev1", "Resident Evil: Revelations 1", "", 4),
    ("rev2", "Resident Evil: Revelations 2", "", 5),
    ("dd", "Dragon's Dogma", "", 11),
]

REENGINE_APPS = [
    None,
    ("re2", "Resident Evil 2", "", 6),
    ("re2_non_rt", "Resident Evil 2 (dx11 non rt)", "", 7),
    ("re3", "Resident Evil 3", "", 8),
    ("re3_non_rt", "Resident Evil 3 (dx11 non rt)", "", 9),
    ("re8", "Resident Evil 8", "", 10),
]


if os.getenv("ALBAM_ENABLE_REEN"):
    APPS.extend(REENGINE_APPS)
