# -*- coding: utf-8 -*-
#
# TGDB Scraper for AEL
#
# --- Python standard library ---
from __future__ import unicode_literals
from __future__ import division

import sys
import argparse
import logging
import json
    
# --- Kodi stuff ---
import xbmcaddon

# AEL main imports
from ael import constants
from ael.utils import kodilogging, io, kodi
from ael.scrapers import ScraperSettings, ScrapeStrategy

# Local modules
from resources.lib.scraper import TheGamesDB

kodilogging.config() 
logger = logging.getLogger(__name__)

# --- Addon object (used to access settings) ---
addon           = xbmcaddon.Addon()
addon_id        = addon.getAddonInfo('id')
addon_version   = addon.getAddonInfo('version')

# ---------------------------------------------------------------------------------------------
# This is the plugin entry point.
# ---------------------------------------------------------------------------------------------
def run_plugin():
    # --- Some debug stuff for development ---
    logger.info('------------ Called Advanced Emulator Launcher Plugin: TGDB Scraper ------------')
    logger.info('addon.id         "{}"'.format(addon_id))
    logger.info('addon.version    "{}"'.format(addon_version))
    logger.info('sys.platform     "{}"'.format(sys.platform))
    if io.is_android(): logger.info('OS               "Android"')
    if io.is_windows(): logger.info('OS               "Windows"')
    if io.is_osx():     logger.info('OS               "OSX"')
    if io.is_linux():   logger.info('OS               "Linux"')
    for i in range(len(sys.argv)): logger.info('sys.argv[{}] "{}"'.format(i, sys.argv[i]))
    
    parser = argparse.ArgumentParser(prog='script.ael.defaults')
    parser.add_argument('--cmd', help="Command to execute", choices=['launch', 'scan', 'scrape', 'configure'])
    parser.add_argument('--type',help="Plugin type", choices=['LAUNCHER', 'SCANNER', 'SCRAPER'], default=constants.AddonType.LAUNCHER.name)
    parser.add_argument('--romcollection_id', type=str, help="ROM Collection ID")
    parser.add_argument('--rom_id', type=str, help="ROM ID")
    parser.add_argument('--launcher_id', type=str, help="Launcher configuration ID")
    parser.add_argument('--rom', type=str, help="ROM data dictionary")
    parser.add_argument('--rom_args', type=str)
    parser.add_argument('--settings', type=str)
    parser.add_argument('--is_non_blocking', type=bool, default=False)
    
    try:
        args = parser.parse_args()
    except Exception as ex:
        logger.error('Exception in plugin', exc_info=ex)
        kodi.dialog_OK(text=parser.usage)
        return
    
    if args.type != constants.AddonType.SCRAPER.name:
        kodi.dialog_OK('Only supporting SCRAPER')
        return
    
    if args.cmd != 'scrape':
        kodi.dialog_OK('Only supporting scrape cmd')
        return
    
    if args.rom_id is not None:
        run_rom_scraper(args)
    else:
        run_collection_scraper(args)
    
    logger.debug('Advanced Emulator Launcher Plugin: TGDB Scraper -> exit')

# ---------------------------------------------------------------------------------------------
# Scraper methods.
# ---------------------------------------------------------------------------------------------
def run_rom_scraper(args):
    logger.debug('TGDB scraper: Starting ...')
    settings    = json.loads(args.settings)
    rom_dic     = json.loads(args.rom)
    rom_id      = args.rom_id

    logger.debug('========== run_scraper() BEGIN ==================================================')
    progress_dialog     = kodi.ProgressDialog()
    scraper_settings    = ScraperSettings.from_settings_dict(settings)
    scraper_strategy    = ScrapeStrategy(scraper_settings, TheGamesDB())
    
    scraped_rom_data = scraper_strategy.process_ROM()
    logger.info('run_rom_scraper(): rom scraping done')
    progress_dialog.endProgress()
    
    scraper_strategy.store_scraped_rom(args.romd_id, scraped_rom_data)
    progress_dialog.close()
    kodi.notify('ROMs scraping done')
                                 
def run_collection_scraper(args):
    pass
        
# ---------------------------------------------------------------------------------------------
# RUN
# ---------------------------------------------------------------------------------------------
try:
    run_plugin()
except Exception as ex:
    logger.fatal('Exception in plugin', exc_info=ex)
    kodi.notify_error("General failure")
    