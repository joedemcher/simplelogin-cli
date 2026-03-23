import unittest
from unittest.mock import patch, mock_open, MagicMock
import yaml
from pathlib import Path
import tempfile

from simplelogin import cli

class SimpleLoginCLITests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_path = Path(self.temp_dir.name) / 'config.yaml'
        self.test_config = {'api_key': 'test_api_key_12345'}

        with open(self.config_path, 'w') as f:
            yaml.dump(self.test_config, f)

        self.mock_alias_list_response = {
            "aliases": [
                {
                    "creation_date": "2020-04-06 17:57:14+00:00",
                    "creation_timestamp": 1586195834,
                    "email": "prefix1.cat@sl.lan",
                    "name": "A Name",
                    "enabled": True,
                    "id": 3,
                    "mailbox": {
                        "email": "a@b.c",
                        "id": 1
                    },
                    "mailboxes": [
                        {
                            "email": "m1@cd.ef",
                            "id": 2
                        },
                        {
                            "email": "john@wick.com",
                            "id": 1
                        }
                    ],
                    "latest_activity": {
                        "action": "forward",
                        "contact": {
                            "email": "c1@example.com",
                            "name": None,
                            "reverse_alias": "\"c1 at example.com\" <re1@SL>"
                        },
                        "timestamp": 1586195834
                    },
                    "nb_block": 7,
                    "nb_forward": 1,
                    "nb_reply": 0,
                    "note": "Take note",
                    "pinned": True
                }
            ]
        }

        self.mock_domain_response = {
            'custom_domains': [
                {
                    'id': 456,
                    'domain_name': 'testdomain.com',
                    'is_verified': True,
                    'catch_all': False,
                    'nb_alias': 5,
                    'mailboxes': [
                        {'id': 789, 'email': 'user@example.com'}
                    ],
                    'creation_date': '2023-01-01T12:00:00+00:00'
                }
            ]
        }

        self.mock_mailbox_response = {
            'mailboxes': [
                {
                    'id': 789,
                    'email': 'user@example.com',
                    'default': True,
                    'creation_date': '2023-01-01T12:00:00+00:00'
                }
            ]
        }

        self.mock_alias_options = {
            'can_create': True,
            'suffixes': [
                {'suffix': '@example.com', 'signed_suffix': 'signed_suffix_data', 'is_premium': False}
            ]
        }

        self.mock_alias_creation_response = {
            'id': 124,
            'email': 'new_alias@example.com'
        }

    def tearDown(self):
        self.temp_dir.cleanup()

    @patch('simplelogin.cli.get_config_file')
    def test_load_config(self, mock_get_config_file):
        mock_get_config_file.return_value = self.config_path
        config = cli.load_config()
        self.assertEqual(config, self.test_config)

if __name__ == '__main__':
    unittest.main()
