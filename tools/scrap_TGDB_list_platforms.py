#!/usr/bin/python -B
# -*- coding: utf-8 -*-
#
# Get all TGDB platform IDs and outputs JSON and CSV files.
#

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

# --- configuration ------------------------------------------------------------------------------
txt_fname = 'data/TGDB_platforms.txt'
csv_fname = 'data/TGDB_platforms.csv'

# --- main ---------------------------------------------------------------------------------------

# --- Create scraper object ---
scraper_obj = TheGamesDB()
scraper_obj.set_verbose_mode(False)
scraper_obj.set_debug_file_dump(True, os.path.join(os.path.dirname(__file__), 'assets'))
status_dic = kodi.new_status_dic('Scraper test was OK')

# --- Get platforms ---
# Call to this function will write file 'assets/TGDB_get_platforms.json'
json_data = scraper_obj.debug_get_platforms(status_dic)
if not status_dic['status']:
    print('SCRAPER ERROR: "' + status_dic['msg'] + '"')
    sys.exit(0)
platforms_dic = json_data['data']['platforms']
pname_dic = {platforms_dic[platform]['name'] : platform for platform in platforms_dic}
# pprint.pprint(platforms_dic)

# --- Print list ---
sl = []
sl.append('Number of TGDB platforms {}'.format(len(platforms_dic)))
sl.append('')
table_str = [
    ['left', 'left', 'left'],
    ['ID', 'Name', 'Short name'],
]
for pname in sorted(pname_dic, reverse = False):
    platform = platforms_dic[pname_dic[pname]]
    # print('{0} {1} {2}'.format(platform['id'], platform['name'], platform['alias']))
    try:
        table_str.append([
            platform['id'],
            platform['name'],
            platform['alias']
        ])
    except UnicodeEncodeError as ex:
        print('Exception UnicodeEncodeError')
        print('ID {0}'.format(platform['id']))
        sys.exit(0)
table_str_list = text.render_table_str(table_str)
sl.extend(table_str_list)
text_str = '\n'.join(sl)
print('\n'.join(table_str_list))

# --- Output file in TXT format ---
print('\nWriting file "{}"'.format(txt_fname))
text_file = open(txt_fname, 'w')
text_file.write(text_str.encode('utf8'))
text_file.close()

# --- Output file in CSV format ---
text_csv_slist = text.render_table_CSV_slist(table_str)
text_csv = '\n'.join(text_csv_slist)
print('Writing file "{}"'.format(csv_fname))
text_file = open(csv_fname, 'w')
text_file.write(text_csv.encode('utf8'))
text_file.close()
