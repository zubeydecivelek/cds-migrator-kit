# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# CDS-Videos is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-Videos command line module."""
import logging
from pathlib import Path

from cds_migrator_kit.rdm.migration.runner import Runner
from cds_migrator_kit.videos.weblecture_migration.streams import RecordStreamDefinition
import click
from flask import current_app
from flask.cli import with_appcontext
from cds_migrator_kit.videos.weblecture_migration.transform import videos_migrator_marc21


import json
from os.path import join


cli_logger = logging.getLogger("migrator")

@click.group()
def weblecture_migration():
    """Migration CLI."""
    pass


@weblecture_migration.command()
@click.option(
    "--dry-run",
    is_flag=True,
)
@with_appcontext
def run(dry_run=False):
    """Run."""
    stream_config = current_app.config["CDS_MIGRATOR_KIT_STREAM_CONFIG_VIDEOS"]
    runner = Runner(
        stream_definitions=[RecordStreamDefinition],
        config_filepath=Path(stream_config).absolute(),
        dry_run=dry_run,
    )
    runner.run()
    
