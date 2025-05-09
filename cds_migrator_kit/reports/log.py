# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
#
# cds-migrator-kit is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""CDS Migrator Records loggers."""

import csv
import json
import logging
import os
from copy import deepcopy

from flask import current_app


class Singleton(type):
    """Temporary solution for this logger."""

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """Call."""
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class JsonLogger(metaclass=Singleton):
    """Log migration statistic to file controller."""

    logger = None

    @classmethod
    def initialize(cls, log_dir):
        """Constructor."""
        logger_migrator = logging.getLogger("migrator-rules")
        logger_users = logging.getLogger("users")
        logger_migrator.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - "
            "%(message)s - \n "
            "[in %(pathname)s:%(lineno)d]"
        )
        # errors to file
        fh = logging.FileHandler(log_dir / "error.log")
        fh.setLevel(logging.ERROR)
        fh.setFormatter(formatter)
        logger_migrator.addHandler(fh)
        fh = logging.FileHandler(log_dir / "users.log")
        fh.setFormatter(formatter)
        logger_users.addHandler(fh)
        # info to stream/stdout
        sh = logging.StreamHandler()
        sh.setFormatter(formatter)
        sh.setLevel(logging.INFO)
        logger_migrator.addHandler(sh)

        logger_matcher = logging.getLogger("cds_dojson.matcher.dojson_matcher")
        logger_matcher.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - "
            "%(message)s - \n "
            "[in %(pathname)s:%(lineno)d]"
        )
        mh = logging.FileHandler("matcher.log")
        mh.setFormatter(formatter)
        mh.setLevel(logging.DEBUG)
        logger_matcher.addHandler(mh)

    @classmethod
    def get_logger(cls):
        """Get migration logger."""
        return logging.getLogger("migrator-rules")

    def __init__(
        self, stats_filename, records_filename, records_state_filename, collection
    ):
        """Constructor."""
        self._logs_path = os.path.join(
            current_app.config["CDS_MIGRATOR_KIT_LOGS_PATH"], collection
        )
        self.STAT_FILEPATH = os.path.join(self._logs_path, stats_filename)
        self.RECORD_FILEPATH = os.path.join(self._logs_path, records_filename)
        self.RECORD_STATE_FILEPATH = os.path.join(
            self._logs_path, records_state_filename
        )
        self.collection = collection

        if not os.path.exists(self._logs_path):
            os.makedirs(self._logs_path)

        self.error_file = None
        self.record_dump_file = None
        self._success_state_cache = {}

    def start_log(self):
        """Initialize logging file descriptors."""
        # init log files
        self.error_file = open(self.STAT_FILEPATH, "w")
        self.record_dump_file = open(self.RECORD_FILEPATH, "w")
        self.records_state_dump_file = open(self.RECORD_STATE_FILEPATH, "w")
        self.error_file.truncate(0)
        self.record_dump_file.truncate(0)
        self.records_state_dump_file.truncate(0)
        columns = [
            "recid",
            "stage",
            "type",
            "error",
            "field",
            "value",
            "message",
            "clean",
            "priority",
        ]
        self.log_writer = csv.DictWriter(self.error_file, fieldnames=columns)
        self.log_writer.writeheader()
        self.record_dump_file.write("{\n")
        self.records_state_dump_file.write("[\n")

    def read_log(self):
        """Read error log file."""
        self.error_file = open(self.STAT_FILEPATH, "r")
        reader = csv.DictReader(self.error_file)
        for row in reader:
            yield row

    def load_record_dumps(self):
        """Load stats from file as json."""
        self.record_dump_file = open(self.RECORD_FILEPATH, "r")
        return json.load(self.record_dump_file)

    def finalise(self):
        """Finalise logging files."""
        self.error_file.close()
        # remove last comma and newline in the json dump
        self.record_dump_file.seek(self.record_dump_file.tell() - 2, os.SEEK_SET)
        # close the dict
        self.record_dump_file.write("}")
        self.record_dump_file.close()
        self.records_state_dump_file.seek(
            self.records_state_dump_file.tell() - 2, os.SEEK_SET
        )
        self.records_state_dump_file.write("]")
        self.records_state_dump_file.close()

    def add_record(self, record, **kwargs):
        """Add record to list of collected records."""
        recid = record["legacy_recid"]
        self.record_dump_file.write(f'"{recid}": {json.dumps(record)},\n')

    def add_record_state(self, record_state, **kwargs):
        """Add record state."""
        self.records_state_dump_file.write(f"{json.dumps(record_state)},\n")

    def add_log(self, exc, record=None, key=None, value=None):
        """Add exception log."""
        logger_migrator = logging.getLogger("migrator-rules")

        if record:
            recid = record.get("recid", None) or record.get("record", {}).get(
                "recid", {}
            )
        else:
            recid = getattr(exc, "recid", None)

        subfield = f"subfield: {exc.subfield}" if getattr(exc, "subfield", None) else ""
        error_format = {
            "recid": recid,
            "type": getattr(exc, "type", None),
            "error": getattr(exc, "description", None),
            "field": f"{getattr(exc, 'field', key)} {subfield}",
            "value": getattr(exc, "value", value),
            "stage": getattr(exc, "stage", None),
            "message": getattr(exc, "message", str(exc)),
            "priority": getattr(exc, "priority", None),
            "clean": False,
        }
        self.log_writer.writerow(error_format)
        logger_migrator.error(exc)

    def add_success_state(self, recid, state):
        """Save a temporary success state for recid.

        For example, we store affiliation warnings when we don't match.
        """
        if recid in self._success_state_cache:
            new_state = deepcopy(self._success_state_cache[recid])
            new_state["message"] = f"{new_state['message']}\n{state['message']}"
            new_state["value"] = f"{new_state['value']}\n{state['value']}"
            state = new_state
        self._success_state_cache[recid] = state

    def add_success(self, recid):
        """Log recid as success."""
        _state = self._success_state_cache.pop(recid, {})
        self.log_writer.writerow({"recid": recid, "clean": True, **_state})


class RDMJsonLogger(JsonLogger):
    """Log rdm record migration statistic to file controller."""

    def __init__(self, collection=None):
        """Constructor."""
        super().__init__(
            stats_filename="rdm_migration_errors.csv",
            records_filename="rdm_records_dump.json",
            records_state_filename="rdm_records_state.json",
            collection=collection,
        )
