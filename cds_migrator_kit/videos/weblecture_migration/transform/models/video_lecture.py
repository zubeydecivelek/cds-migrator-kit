# -*- coding: utf-8 -*-
#
# This file is part of CERN Document Server.
# Copyright (C) 2025 CERN.
#
# Invenio is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""CDS-Videos Video Lecture model."""

from cds_migrator_kit.transform.overdo import CdsOverdo

from .base import model as base_model


class VideoLecture(CdsOverdo):
    """Translation Index for CERN Video Lectures."""

    __query__ = '8567_.x:"Absolute master path" 8567_.d:/mnt/master_share* -980__.C:MIGRATED -980__.c:DELETED -5831_.a:digitized'

    __ignore_keys__ = {
        "003",
        # 340: Drop streaming video, anything else we copy over to curation field.
        "340__a",  # Physical medium -> curation field
        "340__d",  # Physical medium/recording technique -> curation field
        "340__9",  # Physical medium/CD-ROM -> curation field
        "340__k",  # Physical medium/ -> curation field
        "340__j",  # Physical medium/ -> curation field
        "340__8",  # Physical medium/id? -> curation field https://cds.cern.ch/record/2234827
        # check with JY
        "961__h",  # Hour? TODO? check with JY
        "961__l",  # Library? TODO? check with JY
        "961__a",  # ? TODO? check with JY
        "961__b",  # ? TODO? check with JY
        "964__a",  # Item owner TODO? check with JY
        "916__d",  # Status week? TODO? check with JY
        "901__u",  # Affiliation at Conversion? TODO? check with JY
        "583__a",  # Action note / curation TODO? check with JY
        "583__c",  # Action note / curation TODO? check with JY
        "583__z",  # Action note / curation TODO? check with JY
        "916__n",  # Status week TODO? check with JY
        "916__s",  # Status week TODO? check with JY
        "916__w",  # Status week TODO? check with JY
        "916__y",  # Status week TODO? check with JY
        "916__a",  # Status week TODO? check with JY
        "306__a",  # ? TODO? check with JY
        "336__a",  # ? TODO? check with JY
        "981__a",  # duplicate record id TODO? check with JY
        "916__a",  # Status week TODO? check with JY
        "916__d",  # Status week TODO? check with JY
        "916__e",  # Status week TODO? check with JY
        "916__s",  # Status week TODO? check with JY
        "916__w",  # Status week TODO? check with JY
        "916__y",  # Status week TODO? check with JY
        "960__a",  # Base?
        # Category, Collection, Series, Keywords
        "980__a",  # collection tag
        "980__b",  # Secondary collection indicator
        "65027a",  # TODO Subject category = Event?
        "490__a",  # TODO Series
        "490__v",  # Series: volume
        "650172",  # subject provenance
        "65017a",  # subject value
        "6531_9",  # keyword provenance
        "6531_a",  # keyword
        "690C_a",  # collection name
        # Conference Information/Indico
        "111__a",  # Title (indico)
        "111__9",  # Start date (indico)
        "111__g",  # Event id (indico)
        "111__z",  # End date (indico)
        "111__c",  # Video location (indico location)
        "084__a",  # Indico?
        "084__2",  # Indico?
        "518__r",  # Video/meeting location
        "518__g",  # Lectures: conference identification
        "970__a",  # alternative identifier, indico id?
        # Copyright/License
        "542__d",  # Copyright holder
        "542__g",  # Copyright date
        "542__3",  # Copyright materials
        "540__a",  # License
        "540__b",  # License person/organization
        "540__u",  # License URL
        "540__3",  # License material
        # Alternative identifiers
        "962__n",  # `Presented at` note (conference/linked document)
        "962__b",  # `Presented at` record (conference/linked document)
        "088__9",  # Report number (make it alternative identifier with cds reference?)
        "088__z",  # Report number (make it alternative identifier with cds reference?)
        "035__9",  # Inspire schema (Indico/AgendaMaker)
        "035__a",  # Inspire id value
        "088__a",  # Report Number --> alternative identifier with ds reference
        # Additional Title, Volume, Note
        "246__a",  # Additional title
        "246__i",  # Additional title/display text
        "246__b",  # Additional title remaining
        "246__n",  # Volume
        "246__p",  # Volume
        "500__a",  # Note (-> internal note)
        "500__b",  # Note (-> internal note)
        "500__9",  # Note/type (-> internal note) https://cds.cern.ch/record/1561636
        # Restricted
        "5061_f",
        "5061_d",
        "5061_5",
        "5061_a",
        "5061_2",
        # Location (Shelving/Library)
        "852__c",  # Location (Shelving/Library)
        "852__b",  # Location (Shelving/?)
        "852__8",  # Location (Shelving/id?) https://cds.cern.ch/record/2234827
        "852__h",  # Location (Shelving) example: https://cds.cern.ch/record/254588/
        "852__a",  # Location (Shelving) example: https://cds.cern.ch/record/558348
        "852__x",  # Location (Shelving/ type? DVD) example: https://cds.cern.ch/record/690000/
        "852__9",  # Location (Shelving/ note?) example: https://cds.cern.ch/record/2233722
        # Date/Extra Reduntant
        "260__c",  # Redundant (more detailed value is in 269__c imprint.pub_date)
        "260__a",
        "260__b",
        # Contributor?
        "110__a",  # corporate author
        "700__m",  # author's email
        "270__p",  # document contact --> add as a contributor with a correct role
        # Internal Note
        "595__a",  # Internal Note --> curation field
        "595__z",  # SOME RECORD HAVE UNCL as value, do we keep it? what does UNCL mean
        # Collaboration --> add new role to contributors
        "710__5",  # department / organisation author
        "710__a",  # organisation author
        "710__g",  # organisation author
        # Accelerator/Facility, Experiment, Project, Study
        "693__a",  # accelerator, create a custom field?
        "693__e",  # experiments
        "693__p",  # project
        "693__s",  # study
        # OAI
        "0248_a",  # oai identifier
        "0248_p",  # oai identifier
        "0248_q",
        # IGNORE
        "518__h",  # Lectures: Starting time
        "300__2",  # Imprint
        "300__b",  # Imprint
        "300__8",  # Imprint
        "300__a",  # Number of pages / duration
        "250__a",  # Edition
        "700__0",  # Author id (eg: AUTHOR|(CDS)2067852)
        "518__l",  # Lectures: length of speech
        "100__0",  # Author id (eg: AUTHOR|(CDS)2067852)
        "240__a",  # Decided to drop, (Streaming Video)
        "337__a",  # Decided to drop, (Video)
        "963__a",  # values: PUBLIC/RESTRICTED
        "8564_8",  # File: bibdoc id
        "8564_s",  # File: file size
        # IMPLEMENTED
        # "520__a",  # Note (-> description.type = abstract
        # "001",
        # "041__a",  # languages
        # "906__p",  # event speakers
        # "100__9",  # #BEARD# tag
        # "100__a",
        # "100__u",  # Author affiliation
        # "700__e",  # Contributor/Speaker role
        # "700__0",  # Contributors (cds author id)
        # "700__9",  # #BEARD# tag
        # "700__a",  # Contributors (full name)
        # "700__u",  # Contributors (affiliation)
        # "518__d",  # Full date/time
        # "269__c",  # Date (full date/year)
        # "269__b",  # CERN (checked for other values)
        # "269__a",  # Geneva (checked for other values)
        # "518__a",  # Date
        # "906__u", # Contributor Affiliation
        # "511__u",  # Contributor Affiliation
        # "8567_u",  # File url
        # "8567_y",  # File description
        # "8567_2",  # File system? 'MediaArchive'
        # "8564_q",  # File type (digitized)
        # "8564_8",  # Files system field
        # "8564_s",  # Files system field
        # "8564_u",  # Files
        # "8564_x",  # Files system field
        # "8564_y",  # Files
        # "961__x",  # Creation Date TODO? check with JY
        # "961__c",  # modification Date TODO? check with JY
        # "859__f",  # submitter email
        # "8560_f",  # submitter email
    }


model = VideoLecture(
    bases=(base_model,), entry_point_group="cds_migrator_kit.videos.rules.video_lecture"
)
