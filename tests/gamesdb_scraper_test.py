import unittest, os
import unittest.mock
from unittest.mock import MagicMock, patch

import json
import logging

from fakes import FakeProgressDialog, random_string

logging.basicConfig(format = '%(asctime)s %(module)s %(levelname)s: %(message)s',
                datefmt = '%m/%d/%Y %I:%M:%S %p', level = logging.DEBUG)
logger = logging.getLogger(__name__)

from resources.lib.scraper import TheGamesDB
from ael.scrapers import ScrapeStrategy, ScraperSettings

from ael.api import ROMObj
from ael import constants
from ael.utils import net, io

def read_file(path):
    f = io.FileName(path)
    return f.readAll()
    
def read_file_as_json(path):
    file_data = read_file(path)
    return json.loads(file_data, encoding = 'utf-8')

def mocked_gamesdb(url, url_clean=None):

    print(url)
    mocked_json_file = ''

    if '/Developers' in url:
        mocked_json_file = Test_gamesdb_scraper.TEST_ASSETS_DIR + "\\thegamesdb_developers.json"

    if '/Genres' in url:
        mocked_json_file = Test_gamesdb_scraper.TEST_ASSETS_DIR + "\\thegamesdb_genres.json"

    
    if '/Publishers' in url:
        mocked_json_file = Test_gamesdb_scraper.TEST_ASSETS_DIR + "\\thegamesdb_publishers.json"

    if '/Games/ByGameName' in url:
        mocked_json_file = Test_gamesdb_scraper.TEST_ASSETS_DIR + "\\thegamesdb_castlevania_list.json"
        
    if '/Games/ByGameID' in url:
        mocked_json_file = Test_gamesdb_scraper.TEST_ASSETS_DIR + "\\thegamesdb_castlevania.json"
        
    if '/Games/Images' in url:
        print('reading fake image file')
        mocked_json_file = Test_gamesdb_scraper.TEST_ASSETS_DIR + "\\thegamesdb_images.json"

    if 'cdn.thegamesdb.net/' in url:
        return read_file(Test_gamesdb_scraper.TEST_ASSETS_DIR + "\\test.jpg")

    if mocked_json_file == '':
        return net.get_URL(url)

    print('reading mocked data from file: {}'.format(mocked_json_file))
    return read_file(mocked_json_file), 200

class Test_gamesdb_scraper(unittest.TestCase):
    
    ROOT_DIR = ''
    TEST_DIR = ''
    TEST_ASSETS_DIR = ''

    @classmethod
    def setUpClass(cls):        
        cls.TEST_DIR = os.path.dirname(os.path.abspath(__file__))
        cls.ROOT_DIR = os.path.abspath(os.path.join(cls.TEST_DIR, os.pardir))
        cls.TEST_ASSETS_DIR = os.path.abspath(os.path.join(cls.TEST_DIR,'assets/'))
                
        print('ROOT DIR: {}'.format(cls.ROOT_DIR))
        print('TEST DIR: {}'.format(cls.TEST_DIR))
        print('TEST ASSETS DIR: {}'.format(cls.TEST_ASSETS_DIR))
        print('---------------------------------------------------------------------------')
    
    @patch('resources.lib.scraper.net.get_URL', side_effect = mocked_gamesdb)
    @patch('ael.api.client_get_rom')
    def test_scraping_metadata_for_game(self, api_rom_mock: MagicMock, mock_json_downloader):        
        # arrange
        settings = ScraperSettings()
        settings.scrape_metadata_policy = constants.SCRAPE_POLICY_SCRAPE_ONLY
        settings.scrape_assets_policy   = constants.SCRAPE_ACTION_NONE
        
        rom_id = random_string(5)
        rom = ROMObj({
            'id': rom_id,
            'scanned_data': { 'file':Test_gamesdb_scraper.TEST_ASSETS_DIR + '\\castlevania.zip'},
            'platform': 'Nintendo NES'
        })
        api_rom_mock.return_value = rom
        
        target = ScrapeStrategy(None, 0, settings, TheGamesDB(), FakeProgressDialog())

        # act
        actual = target.process_single_rom(rom_id)
                
        # assert
        self.assertTrue(actual)
        self.assertEqual(u'Castlevania - The Lecarde Chronicles', actual.get_name())
        print(actual.get_data_dic())
        
    # add actual gamesdb apikey above and comment out patch attributes to do live tests
    @patch('resources.lib.scraper.net.get_URL', side_effect = mocked_gamesdb)
    @patch('resources.lib.scraper.net.download_img')
    @patch('resources.lib.scraper.io.FileName.scanFilesInPath', autospec=True)
    @patch('ael.api.client_get_rom')
    def test_scraping_assets_for_game(self, api_rom_mock: MagicMock, scanner_mock, mock_img_downloader, mock_json_downloader):        
        # arrange
        settings = ScraperSettings()
        settings.scrape_metadata_policy = constants.SCRAPE_ACTION_NONE
        settings.scrape_assets_policy = constants.SCRAPE_POLICY_SCRAPE_ONLY
        settings.asset_IDs_to_scrape = [constants.ASSET_BANNER_ID, constants.ASSET_FANART_ID ]
        
        rom_id = random_string(5)
        rom = ROMObj({
            'id': rom_id,
            'scanned_data': { 'file':Test_gamesdb_scraper.TEST_ASSETS_DIR + '\\castlevania.zip'},
            'platform': 'Nintendo NES',
            'assets': {key: '' for key in constants.ROM_ASSET_ID_LIST},
            'asset_paths': {
                constants.ASSET_BANNER_ID: '/banners/',
                constants.ASSET_FANART_ID: '/fanarts/'
            }
        })
        api_rom_mock.return_value = rom
        
        target = ScrapeStrategy(None, 0, settings, TheGamesDB(), FakeProgressDialog())

        # act
        actual = target.process_single_rom(rom_id) 
                
        # assert
        self.assertTrue(actual) 
        logger.info(actual.get_data_dic()) 
        
        self.assertTrue(actual.entity_data['assets'][constants.ASSET_BANNER_ID], 'No banner defined')
        self.assertTrue(actual.entity_data['assets'][constants.ASSET_FANART_ID], 'No fanart defined')

if __name__ == '__main__':
    unittest.main()
