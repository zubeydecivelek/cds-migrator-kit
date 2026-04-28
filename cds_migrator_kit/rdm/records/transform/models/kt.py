# -*- coding: utf-8 -*-
#
# Copyright (C) 2026 CERN.
#
# CDS-RDM is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-RDM KT (Knowledge Transfer) model."""
from cds_migrator_kit.rdm.records.transform.models.base_record import (
    rdm_base_record_model,
)
from cds_migrator_kit.transform.overdo import CdsOverdo


class KTModel(CdsOverdo):
    """Translation model for KT (Knowledge Transfer) records."""

    # MatchUnit is case-sensitive — all casing variants from the dump are listed.
    # Technology Transfer variants: 51x "Technology Transfer", 10x "technology transfer", 6x "Technology transfer"
    # Intellectual Property variants: 5x "Intellectual Property", 2x "intellectual property", 2x "Intellectual property"
    __query__ = """980__:KTT-LSCERNTALK OR
                   980__:KTT-PARTNERCERNTALK OR
                   980__:CERN-KT-POLICIES OR
                   6531_:"Technology Transfer" OR
                   6531_:"technology transfer" OR
                   6531_:"technology Transfer" OR
                   6531_:"Technology transfer" OR
                   6531_:"Intellectual Property" OR
                   6531_:"intellectual property" OR
                   6531_:"Intellectual property" OR
                   6531_:"intellectual Property"
                   """

    __ignore_keys__ = {
        "0247_9",
        # "0248_a",
        # "0248_p",
        # "0248_q",
        # "100__m",
        # "300__a",  # number of pages
        # "6531_9",  # keyword scheme
        # "700__m",
        # "7870_r",  # detailed description of record relation
        # "8564_8",
        # "8564_s",
        # "8564_x",
        # "8564_y",  # file description - done by files dump
        # "8564_z",
        # "960__a",  # base number
        # "961__c",  # CDS modification tag
        # "961__h",  # CDS modification tag
        # "961__l",  # CDS modification tag
        # "961__x",  # CDS modification tag
        # "980__a",
        # "981__a",  # duplicate record id
    }

    _default_fields = {
        # "resource_type": {"id": "publication-other"},
        "custom_fields": {},
    }


kt_model = KTModel(
    bases=(rdm_base_record_model,),
    entry_point_group="cds_migrator_kit.migrator.rules.kt",
)
