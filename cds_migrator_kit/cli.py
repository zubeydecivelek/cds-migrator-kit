# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 CERN.
#
# cds-migrator-kit is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.
"""cds-migrator-kit command line module."""

import importlib

import click


def import_module(module_name):
    """Try to import a module, return True if successful, otherwise False."""
    try:
        importlib.import_module(module_name)
        return True
    except ImportError:
        return False


@click.group()
def cli():
    """Base CLI command that loads the subcommands."""
    pass


# Check for `rdm` dependencies
if import_module("cds_rdm.__init__"):
    from cds_migrator_kit.rdm.cli import migration

    cli = migration

# Check for `videos` dependencies
if import_module("cds.version"):
    from cds_migrator_kit.videos.weblecture_migration.cli import videos

    cli.add_command(videos, "videos")
