# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# CDS-RDM is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-Videos transform step module."""
import csv
import datetime
import json
import logging
import os.path
import re
from collections import OrderedDict
from copy import deepcopy
from pathlib import Path

import arrow
import requests
from invenio_db import db
from invenio_rdm_migrator.streams.records.transform import (
    RDMRecordEntry,
    RDMRecordTransform,
)
from invenio_records_resources.proxies import current_service_registry
from invenio_vocabularies.contrib.names.models import NamesMetadata
from opensearchpy import RequestError
from sqlalchemy.exc import NoResultFound

from cds_migrator_kit.videos.weblecture_migration.transform import videos_migrator_marc21

from cds_migrator_kit.migration_config import VOCABULARIES_NAMES_SCHEMES
from cds_migrator_kit.rdm.migration.transform.xml_processing.dumper import CDSRecordDump
from cds_migrator_kit.rdm.migration.transform.xml_processing.errors import (
    LossyConversion,
    ManualImportRequired,
    MissingRequiredField,
    RecordFlaggedCuration,
    RestrictedFileDetected,
    UnexpectedValue,
)
from cds_migrator_kit.records.log import RDMJsonLogger

cli_logger = logging.getLogger("migrator")


class CDSToVideosRecordEntry(RDMRecordEntry):
    """Transform CDS record to CDS Videos record."""

    def __init__(
        self,
        partial=False,
        dry_run=False,
    ):
        """Constructor."""
        self.dry_run = dry_run
        super().__init__(partial)
        
    def _schema(self, entry):
        """Return JSONSchema of the record."""
        return 
        
    def _created(self, json_entry):
        try:
            return arrow.get(json_entry["_created"])
        except KeyError:
            return datetime.date.today().isoformat()

    def _updated(self, record_dump):
        """Returns the creation date of the record."""
        return record_dump.data["record"][0]["modification_datetime"]
    
    def _access(self, entry, record_dump):
        return 
    
    def _recid(self, record_dump):
        """Returns the recid of the record."""
        return str(record_dump.data["recid"])
    
    def _bucket_id(self, json_entry):
        return

    def _id(self, entry):
        return

    def _version_id(self, entry):
        return 
    
    def _index(self, entry):
        return

    def _pids(self, entry):
        return
    
    def _bucket_id(self, json_entry):
        return
    
    def _media_bucket_id(self, entry):
        return
    
    def _files(self, record_dump):
        """Transform the files of a record."""
        raise NotImplementedError("_files is not implemented for this class.")
    
    def _media_files(self, entry):
        return
    
    def _metadata(self, entry):
        """Transform the metadata of a record. """
        # TODO implement
        
        def reformat_date(json_data):
            """Reformat the date for the cds-videos data model."""
            dates = json_data.get("date", [])
            dates_set = {date for date in dates if date is not None}

            if len(dates_set) == 1: # Should be only one value
                return next(iter(dates_set))  # Get the single date from the set
            if len(dates_set) > 1:
                return next(iter(dates_set)) # return the first

            # print("No valid date found in record: {}.".format(json_data.get('recid')))
            raise UnexpectedValue("No valid date found in record: {}.".format(json_data.get('recid')))

        def description(json_data):
            """Reformat the description for the cds-videos data model."""
            if not json_data.get("description"):
                # print("\tNo description found, empty string added")
                return json_data.get("title").get("title")
            return json_data.get("description")
        
        metadata = {
            "title": entry["title"],
            "description": description(entry),
            # "publication_date": entry.get("publication_date"),
            "contributors": entry.get("contributors"),
            "languages": entry.get("language"),
            "date": reformat_date(entry)
        }
        # filter empty keys
        return {k: v for k, v in metadata.items() if v}
        
    
    def _custom_fields(self, entry):
        """Transform the custom fields of a record."""
        return
    
    def transform(self, entry):
        """Transform a record single entry."""
        record_dump = CDSRecordDump(
            data=entry,
            dojson_model=videos_migrator_marc21
        )
        migration_logger = RDMJsonLogger()

        record_dump.prepare_revisions()
        timestamp, json_data = record_dump.latest_revision
        
        # Put them in metadata method
        # json_data["date"] = reformat_date(json_data, logs)
        # json_data["description"] = reformat_description(json_data, logs)
        
        migration_logger.add_record(json_data)
        record_json_output = {
            "created": self._created(json_data),
            "updated": self._updated(record_dump),
            "metadata": self._metadata(json_data),
        }
        return {
            "created": self._created(json_data),
            "updated": self._updated(record_dump),
            "recid": self._recid(record_dump),
            "json": record_json_output,
            # keep the original extracted entry for storing it
            "_original_dump": entry,
        }

               
class CDSToVideosRecordTransform(RDMRecordTransform):
    """CDSToVideosRecordTransform."""

    def __init__(
        self,
        workers=None,
        throw=True,
        files_dump_dir=None,
        dry_run=False,
    ):
        """Constructor."""
        self.files_dump_dir = Path(files_dump_dir).absolute().as_posix()
        self.dry_run = dry_run
        super().__init__(workers, throw)
        
    def _parent(self, entry, record):
        parent = {
            "created": record["created"],  # same as the record
            "updated": record["updated"],  # same as the record
            "json": {
                # loader is responsible for creating/updating if the PID exists.
                # this part will be simply omitted
                "id": f'{record["recid"]}-parent',
            },
        }
        return parent
    
    def _record(self, entry):
        # TODO Copied from RDM/transform
        # could be in draft as well, depends on how we decide to publish
        return CDSToVideosRecordEntry(
            dry_run=self.dry_run,
        ).transform(entry)

    def _draft(self, entry):
        return None
    
    def _transform(self, entry):
        """Transform a single entry."""
        # creates the output structure for load step
        migration_logger = RDMJsonLogger()
        
        try:
            record = self._record(entry)
            original_dump = record.pop("_original_dump", {})
            if record:
                return {
                    "record": record,
                    "parent": self._parent(entry, record),
                    "_original_dump": original_dump,
                }
        except (
            LossyConversion,
            RestrictedFileDetected,
            UnexpectedValue,
            ManualImportRequired,
            MissingRequiredField,
        ) as e:
            migration_logger.add_log(e, record=entry)
            

    def run(self, entries):
        """Run transformation step."""
        return super().run(entries)