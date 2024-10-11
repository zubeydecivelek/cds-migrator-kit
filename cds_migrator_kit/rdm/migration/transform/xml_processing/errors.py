# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# CDS-RDM is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-RDM migration errors module."""

from dojson.errors import DoJSONException


class LossyConversion(DoJSONException):
    """Data lost during migration."""

    description = "[Migration rule missing]"
    def __init__(self, missing=None, *args, **kwargs):
        """Exception custom initialisation."""
        self.missing = missing
        self.stage = "transform"
        self.field = self.missing
        self.type = self.__class__.__name__
        self.priority = "warning"
        super().__init__(*args)


class CDSMigrationException(DoJSONException):
    """CDSDoJSONException class."""

    description = None

    def __init__(
        self, message=None, field=None, subfield=None, value=None, stage=None,
        recid=None, exc=None, priority=None, *args, **kwargs
    ):
        """Constructor."""
        self.subfield = subfield
        self.field = field
        self.value = value
        self.stage = stage
        self.recid = recid
        self.type = str(self.__class__.__name__)
        self.exc = exc
        self.message = message
        self.priority = priority
        super(CDSMigrationException, self).__init__(*args)


class RecordModelMissing(CDSMigrationException):
    """Missing record model exception."""

    description = "[Record did not match any available model]"


class UnexpectedValue(CDSMigrationException):
    """The corresponding value is unexpected."""

    description = "[UNEXPECTED INPUT VALUE]"


class MissingRequiredField(CDSMigrationException):
    """The corresponding value is required."""

    description = "[MISSING REQUIRED FIELD]"


class ManualImportRequired(CDSMigrationException):
    """The corresponding field should be manually migrated."""

    description = "[MANUAL IMPORT REQUIRED]"


class RestrictedFileDetected(CDSMigrationException):

    description = "[Restricted file detected]"
