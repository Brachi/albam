"""Choosing a test's dataset entries at collection time.

A test that only applies to some files declares it with
`@applies_to(<fact>=<value>)`, where each fact is a key the dataset entry
records (`mod_version`, `has_armature`, `payload_extension`, ...). The
dataset's pytest_generate_tests then parametrizes it with only the entries
that match, via entries_for().

Without this, every test ran on every entry and skipped the ones it didn't
apply to, and a skip meant either "doesn't apply" or "no data to run on",
with nothing in the summary to tell them apart. Now a test that doesn't
apply to a file has no case for it, and a test left with no entries at all
is reported by pytest as an empty parameter set: a real gap in the data.
"""
import pytest


def applies_to(**facts):
    """Run the test only on entries whose facts match: a value must be
    equal, one of a set/tuple/list of values, or pass a predicate."""
    return pytest.mark.applies_to(**facts)


def entries_for(metafunc, dataset):
    marker = metafunc.definition.get_closest_marker("applies_to")
    if marker is None:
        return list(dataset)
    return [entry for entry in dataset if _matches(entry, marker.kwargs)]


def _matches(entry, facts):
    # A fact only has to be recorded on the entries the others already let
    # through: `has_models` lives on the .evd entries alone, and
    # @applies_to(payload_extension=".evd", has_models=True) never asks the
    # rest. An entry that matches everything else and lacks one is an error,
    # not a silent mismatch.
    missing = [key for key in facts if key not in entry]
    for key, wanted in facts.items():
        if key in entry and not _fact_matches(entry[key], wanted):
            return False
    if missing:
        raise KeyError(f"dataset entry {entry} records no {missing}, which @applies_to asks for")
    return True


def _fact_matches(value, wanted):
    if callable(wanted):
        return wanted(value)
    if isinstance(wanted, (set, frozenset, tuple, list)):
        return value in wanted
    return value == wanted
