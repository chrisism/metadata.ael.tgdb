#!/usr/bin/python
# -*- coding: utf-8 -*-
# Updates the ROM count in the Offline Scraper

# Copyright (c) 2016-2017 Wintermute0110 <wintermute0110@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# --- Python standard library ---
from __future__ import unicode_literals
import os, sys

import pprint
import logging

logging.basicConfig(format = '%(asctime)s %(module)s %(levelname)s: %(message)s',
                datefmt = '%m/%d/%Y %I:%M:%S %p', level = logging.DEBUG)
logger = logging.getLogger(__name__)

from resources.lib.scraper import TheGamesDB, AKL_compact_platform_TGDB_mapping
from akl.utils import kodi, text, io
from akl import constants, platforms

# --- Constants -----------------------------------------------------------------------------------
CURRENT_DIR = io.FileName('./')
GAMEDB_DIR = io.FileName('./GameDBInfo/')
GAMEDB_JSON_BASE_NOEXT = 'GameDB_info'

# --- main() --------------------------------------------------------------------------------------
gamedb_info_dic = {}
for platform in platforms.AKL_platforms:
    # print('Processing platform "{0}"'.format(platform))

    # >> Open XML file and count ROMs
    xml_file = CURRENT_DIR.pjoin(AKL_compact_platform_TGDB_mapping[platform.compact_name] ).getPath()
    games = [] # TODO: audit_load_OfflineScraper_XML(xml_file)

    # >> Count ROMs and add to dictionary
    platform_info = {'numROMs' : 0 }
    platform_info['numROMs'] = len(games)
    gamedb_info_dic[platform] = platform_info
    # print('numROMs = {0}'.format(platform_info['numROMs']))
    
# >> Save JSON with ROM count
file = io.FileName(GAMEDB_DIR + GAMEDB_JSON_BASE_NOEXT + ".json")
file.writeJson(gamedb_info_dic)
sys.exit(0)
