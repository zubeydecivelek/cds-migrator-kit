# -*- coding: utf-8 -*-
#
# This file is part of CDS.
# Copyright (C) 2025 CERN.
#
# cds-migrator-kit is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""CDS-Videos migration tests."""

from os.path import dirname, join

import pytest

from cds_migrator_kit.rdm.migration.transform.xml_processing.dumper import CDSRecordDump
from cds_migrator_kit.rdm.migration.transform.xml_processing.errors import (
    MissingRequiredField,
    UnexpectedValue,
)
from cds_migrator_kit.videos.weblecture_migration.transform import (
    videos_migrator_marc21,
)
from cds_migrator_kit.videos.weblecture_migration.transform.transform import (
    CDSToVideosRecordEntry,
)
from tests.helpers import add_tag_to_marcxml, load_json, remove_tag_from_marcxml


@pytest.fixture()
def datadir():
    """Get data directory."""
    return join(dirname(__file__), "data")


def test_transform_rules_reqired_metadata(datadir, base_app):
    """Test migration rules."""
    with base_app.app_context():
        data = load_json(datadir, "lecture.json")
        dump = CDSRecordDump(data=data[0], dojson_model=videos_migrator_marc21)
        dump.prepare_revisions()
        created_date, res = dump.latest_revision

        assert res["legacy_recid"] == 2233152
        assert res["recid"] == "2233152"
        assert res["language"] == "en"
        assert res["contributors"] == [
            {
                "name": "Brodski, Michael",
                "role": "Speaker",
                "affiliations": ["Rheinisch-Westfaelische Tech. Hoch. (DE)"],
            },
            {"name": "Dupont, Niels", "role": "Speaker", "affiliations": ["CERN"]},
            {"name": "Esposito, William", "role": "Speaker", "affiliations": ["CERN"]},
            {
                "name": "Brodski, Michael",
                "role": "Speaker",
                "affiliations": ["Rheinisch-Westfaelische Tech. Hoch. (DE)"],
            },
            {"name": "Dupont, Niels", "role": "Speaker", "affiliations": ["CERN"]},
            {"name": "Esposito, William", "role": "Speaker", "affiliations": ["CERN"]},
        ]
        assert res["title"] == {
            "title": "Glimos Instructions for CMS Underground Guiding - in english"
        }
        assert "2016-10-24" in res["date"]
        assert res["description"].startswith(
            "<!--HTML--><p>In this <strong>presentation in english</strong>"
        )


def test_transform_required_metadata(datadir, base_app):
    """Test migration transform."""
    with base_app.app_context():
        data = load_json(datadir, "lecture.json")
        dump = CDSRecordDump(data=data[0], dojson_model=videos_migrator_marc21)
        dump.prepare_revisions()
        created_date, res = dump.latest_revision

        # Transform record
        record_entry = CDSToVideosRecordEntry()
        metadata = record_entry._metadata(res)
        assert metadata["title"] == {
            "title": "Glimos Instructions for CMS Underground Guiding - in english"
        }
        assert metadata["date"] == "2016-10-24"
        # It should be same with the title
        assert metadata["description"].startswith(
            "<!--HTML--><p>In this <strong>presentation in english</strong>"
        )
        assert metadata["contributors"] == [
            {
                "name": "Brodski, Michael",
                "role": "Speaker",
                "affiliations": ["Rheinisch-Westfaelische Tech. Hoch. (DE)"],
            },
            {"name": "Dupont, Niels", "role": "Speaker", "affiliations": ["CERN"]},
            {"name": "Esposito, William", "role": "Speaker", "affiliations": ["CERN"]},
        ]
        assert metadata["language"] == "en"


def test_transform_description(datadir, base_app):
    """Test that the description field `520` is correctly transformed."""
    with base_app.app_context():
        # Load test data
        data = load_json(datadir, "lecture.json")

        # Remove the 520 tag (description) from MARCXML
        modified_data = data[0]
        modified_data["record"][-1]["marcxml"] = remove_tag_from_marcxml(
            modified_data["record"][-1]["marcxml"], "520"
        )

        dump = CDSRecordDump(data=modified_data, dojson_model=videos_migrator_marc21)
        dump.prepare_revisions()
        _, res = dump.latest_revision

        # Ensure json_converted_record don't have the description
        assert "description" not in res

        # Transform record
        record_entry = CDSToVideosRecordEntry()
        metadata = record_entry._metadata(res)

        # Ensure description exists and matches the title
        assert metadata["description"] == metadata["title"]["title"]


def test_transform_date(datadir, base_app):
    """Test that the date field is correctly transformed."""
    with base_app.app_context():
        # Load test data
        data = load_json(datadir, "lecture.json")

        # Test case: Fail due to multiple dates
        modified_data = data[0]
        modified_data["record"][-1]["marcxml"] = add_tag_to_marcxml(
            modified_data["record"][-1]["marcxml"], "518", {"d": "2025-02-06"}
        )
        dump = CDSRecordDump(data=modified_data, dojson_model=videos_migrator_marc21)
        dump.prepare_revisions()
        _, res = dump.latest_revision

        # Transform record
        record_entry = CDSToVideosRecordEntry()
        with pytest.raises(UnexpectedValue):
            record_entry._metadata(res)

        # Test case: Fail due to missing dates
        modified_data["record"][-1]["marcxml"] = remove_tag_from_marcxml(
            modified_data["record"][-1]["marcxml"], "518"
        )
        modified_data["record"][-1]["marcxml"] = remove_tag_from_marcxml(
            modified_data["record"][-1]["marcxml"], "269"
        )

        dump = CDSRecordDump(data=modified_data, dojson_model=videos_migrator_marc21)
        dump.prepare_revisions()
        _, res = dump.latest_revision

        # Transform record
        with pytest.raises(MissingRequiredField):
            record_entry._metadata(res)


def test_transform_contributor(datadir, base_app):
    """Test that the date field is correctly transformed."""
    with base_app.app_context():
        # Load test data
        data = load_json(datadir, "lecture.json")

        # Test case: Fail due to missing contributor
        modified_data = data[0]
        modified_data["record"][-1]["marcxml"] = remove_tag_from_marcxml(
            modified_data["record"][-1]["marcxml"], "700"
        )
        modified_data["record"][-1]["marcxml"] = remove_tag_from_marcxml(
            modified_data["record"][-1]["marcxml"], "906"
        )

        dump = CDSRecordDump(data=modified_data, dojson_model=videos_migrator_marc21)
        dump.prepare_revisions()
        _, res = dump.latest_revision

        # Transform record it should fail (no contributor)
        record_entry = CDSToVideosRecordEntry()
        with pytest.raises(MissingRequiredField):
            record_entry._metadata(res)
