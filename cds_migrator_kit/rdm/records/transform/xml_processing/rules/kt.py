# -*- coding: utf-8 -*-
#
# Copyright (C) 2026 CERN.
#
# CDS-RDM is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-RDM KT (Knowledge Transfer) rules."""

from dojson.errors import IgnoreKey
from dojson.utils import for_each_value

from cds_migrator_kit.errors import UnexpectedValue
from cds_migrator_kit.transform.xml_processing.quality.parsers import StringValue

from ...models.kt import kt_model as model




@model.over("resource_type", "^980__", override=True)
def resource_type(self, key, value):
    """Translates resource_type."""
    value_a = value.get("a")
    if value_a:
        value_a = value_a.strip()
    allowed = {
        "Life Sciences Restricted Documents",
        "CERN-KT-POLICIES",
    }
    if value_a and value_a not in allowed:
        raise UnexpectedValue(
            "Unknown resource type (KT)", field=key, value=value_a
        )
    raise IgnoreKey("resource_type")
