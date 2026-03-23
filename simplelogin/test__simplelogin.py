import unittest
from unittest.mock import patch, MagicMock
import io

# import sys
# import os
# import json
import yaml
from pathlib import Path
import tempfile

# Import the module directly
from simplelogin import cli


class SimpleLoginCLITests(unittest.TestCase):
    def setUp(self):
        # Create a temporary config file for testing
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_path = Path(self.temp_dir.name) / "config.yaml"
        self.test_config = {"api_key": "test_api_key_12345"}

        with open(self.config_path, "w") as f:
            yaml.dump(self.test_config, f)

        # Setup API response mocks
        self.mock_alias_list_response = {
            "aliases": [
                {
                    "id": 123,
                    "email": "test@example.com",
                    "name": "Test Alias",
                    "enabled": True,
                    "pinned": False,
                    "mailboxes": [{"email": "primary@example.com"}],
                    "latest_activity": {
                        "action": "forward",
                        "timestamp": "2023-01-01T12:00:00+00:00",
                    },
                    "nb_forward": 10,
                    "nb_reply": 5,
                    "nb_block": 1,
                    "note": "Test note",
                }
            ]
        }

        self.mock_domain_response = {
            "custom_domains": [
                {
                    "id": 456,
                    "domain_name": "testdomain.com",
                    "is_verified": True,
                    "catch_all": False,
                    "nb_alias": 5,
                    "mailboxes": [{"id": 789, "email": "user@example.com"}],
                    "creation_date": "2023-01-01T12:00:00+00:00",
                }
            ]
        }

        self.mock_mailbox_response = {
            "mailboxes": [
                {
                    "id": 789,
                    "email": "user@example.com",
                    "default": True,
                    "creation_date": "2023-01-01T12:00:00+00:00",
                }
            ]
        }

        self.mock_alias_options = {
            "can_create": True,
            "suffixes": [
                {
                    "suffix": "@example.com",
                    "signed_suffix": "signed_suffix_data",
                    "is_premium": False,
                }
            ],
        }

        self.mock_alias_creation_response = {
            "id": 124,
            "email": "new_alias@example.com",
        }

    def tearDown(self):
        self.temp_dir.cleanup()

    @patch("simplelogin.cli.get_config_file")
    def test_load_config(self, mock_get_config_file):
        mock_get_config_file.return_value = self.config_path
        config = cli.load_config()
        self.assertEqual(config, self.test_config)

    @patch("simplelogin.cli.get_config_file")
    def test_save_config(self, mock_get_config_file):
        mock_get_config_file.return_value = self.config_path
        new_config = {"api_key": "new_api_key"}
        cli.save_config(new_config)

        loaded_config = None
        with open(self.config_path, "r") as f:
            loaded_config = yaml.safe_load(f)

        self.assertEqual(loaded_config, new_config)

    def test_get_headers(self):
        # Test with config file API key
        headers = cli.get_headers(self.test_config)
        self.assertEqual(headers["Authentication"], "test_api_key_12345")

        # Test with environment variable
        with patch.dict("os.environ", {"SIMPLELOGIN_API_KEY": "env_api_key"}):
            headers = cli.get_headers({})
            self.assertEqual(headers["Authentication"], "env_api_key")

    def test_format_datetime(self):
        formatted = cli.format_datetime("2023-01-01T12:00:00+00:00")
        self.assertEqual(formatted, "2023-01-01 12:00:00")

        # Test with invalid format
        formatted = cli.format_datetime("invalid")
        self.assertEqual(formatted, "invalid")

    @patch("simplelogin.cli.requests.get")
    @patch("simplelogin.cli.get_headers")
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_list_aliases(self, mock_stdout, mock_get_headers, mock_get):
        mock_get_headers.return_value = {"Authentication": "test_api_key"}
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.mock_alias_list_response
        mock_get.return_value = mock_response

        cli.list_aliases(self.test_config, page=0)

        # Verify API call
        mock_get.assert_called_once_with(
            f"{cli.BASE_URL}/api/v2/aliases",
            headers={"Authentication": "test_api_key"},
            params={"page_id": 0},
            json=None,
            timeout=10,
        )

        # Check output contains expected data
        output = mock_stdout.getvalue()
        self.assertIn("test@example.com", output)
        self.assertIn("Test Alias", output)

    @patch("simplelogin.cli.requests.get")
    @patch("simplelogin.cli.get_headers")
    def test_get_alias_options(self, mock_get_headers, mock_get):
        mock_get_headers.return_value = {"Authentication": "test_api_key"}
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.mock_alias_options
        mock_get.return_value = mock_response

        result = cli.get_alias_options(self.test_config)

        # Verify API call
        mock_get.assert_called_once_with(
            f"{cli.BASE_URL}/api/v5/alias/options",
            headers={"Authentication": "test_api_key"},
            params={},
            timeout=10,
        )

        self.assertEqual(result, self.mock_alias_options)

    @patch("simplelogin.cli.requests.post")
    @patch("simplelogin.cli.get_alias_options")
    @patch("simplelogin.cli.get_headers")
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_create_custom_alias(
        self, mock_stdout, mock_get_headers, mock_get_options, mock_post
    ):
        mock_get_headers.return_value = {"Authentication": "test_api_key"}
        mock_get_options.return_value = self.mock_alias_options

        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = self.mock_alias_creation_response
        mock_post.return_value = mock_response

        cli.create_custom_alias(
            self.test_config,
            prefix="test",
            suffix_id=0,
            note="Test note",
            name="Test Name",
        )

        # Verify API call
        mock_post.assert_called_once_with(
            f"{cli.BASE_URL}/api/v3/alias/custom/new",
            headers={"Authentication": "test_api_key"},
            json={
                "alias_prefix": "test",
                "signed_suffix": "signed_suffix_data",
                "note": "Test note",
                "name": "Test Name",
            },
            timeout=10,
        )

        # Check output
        output = mock_stdout.getvalue()
        self.assertIn("Custom alias created", output)
        self.assertIn("new_alias@example.com", output)

    @patch("simplelogin.cli.requests.post")
    @patch("simplelogin.cli.get_headers")
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_create_random_alias(self, mock_stdout, mock_get_headers, mock_post):
        mock_get_headers.return_value = {"Authentication": "test_api_key"}

        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = self.mock_alias_creation_response
        mock_post.return_value = mock_response

        cli.create_random_alias(self.test_config, mode="word", note="Test note")

        # Verify API call
        mock_post.assert_called_once_with(
            f"{cli.BASE_URL}/api/alias/random/new",
            headers={"Authentication": "test_api_key"},
            json={"note": "Test note"},
            params={"mode": "word"},
            timeout=10,
        )

        # Check output
        output = mock_stdout.getvalue()
        self.assertIn("Random alias created", output)
        self.assertIn("new_alias@example.com", output)

    @patch("simplelogin.cli.requests.post")
    @patch("simplelogin.cli.requests.get")
    @patch("simplelogin.cli.get_headers")
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_toggle_alias(self, mock_stdout, mock_get_headers, mock_get, mock_post):
        mock_get_headers.return_value = {"Authentication": "test_api_key"}

        # Mock get alias info
        mock_get_response = MagicMock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = {
            "id": 123,
            "email": "test@example.com",
            "enabled": True,
        }
        mock_get.return_value = mock_get_response

        # Mock toggle
        mock_post_response = MagicMock()
        mock_post_response.status_code = 200
        mock_post.return_value = mock_post_response

        cli.toggle_alias(self.test_config, "123")

        # Verify API calls
        mock_get.assert_called_once_with(
            f"{cli.BASE_URL}/api/aliases/123",
            headers={"Authentication": "test_api_key"},
            timeout=10,
        )

        mock_post.assert_called_once_with(
            f"{cli.BASE_URL}/api/aliases/123/toggle",
            headers={"Authentication": "test_api_key"},
            timeout=10,
        )

        # Check output
        output = mock_stdout.getvalue()
        self.assertIn("test@example.com is now disabled", output)

    @patch("builtins.input", return_value="y")
    @patch("simplelogin.cli.requests.delete")
    @patch("simplelogin.cli.requests.get")
    @patch("simplelogin.cli.get_headers")
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_delete_alias(
        self, mock_stdout, mock_get_headers, mock_get, mock_delete, mock_input
    ):
        mock_get_headers.return_value = {"Authentication": "test_api_key"}

        # Mock get alias info
        mock_get_response = MagicMock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = {"id": 123, "email": "test@example.com"}
        mock_get.return_value = mock_get_response

        # Mock delete
        mock_delete_response = MagicMock()
        mock_delete_response.status_code = 200
        mock_delete.return_value = mock_delete_response

        cli.delete_alias(self.test_config, "123")

        # Verify API calls
        mock_get.assert_called_once_with(
            f"{cli.BASE_URL}/api/aliases/123",
            headers={"Authentication": "test_api_key"},
            timeout=10,
        )

        mock_delete.assert_called_once_with(
            f"{cli.BASE_URL}/api/aliases/123",
            headers={"Authentication": "test_api_key"},
            timeout=10,
        )

        # Check output
        output = mock_stdout.getvalue()
        self.assertIn("test@example.com deleted successfully", output)

    @patch("simplelogin.cli.requests.get")
    @patch("simplelogin.cli.get_headers")
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_alias_info(self, mock_stdout, mock_get_headers, mock_get):
        mock_get_headers.return_value = {"Authentication": "test_api_key"}

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": 123,
            "email": "test@example.com",
            "enabled": True,
            "creation_date": "2023-01-01T12:00:00",
            "note": "Test note",
            "mailbox": {"email": "primary@example.com"},
            "nb_forward": 10,
            "nb_reply": 5,
            "nb_block": 1,
        }
        mock_get.return_value = mock_response

        cli.alias_info(self.test_config, "123")

        # Verify API call
        mock_get.assert_called_once_with(
            f"{cli.BASE_URL}/api/aliases/123",
            headers={"Authentication": "test_api_key"},
            timeout=10,
        )

        # Check output
        output = mock_stdout.getvalue()
        self.assertIn("test@example.com", output)
        self.assertIn("Test note", output)
        self.assertIn("Forwarded emails: 10", output)

    @patch("simplelogin.cli.requests.get")
    @patch("simplelogin.cli.get_headers")
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_list_domains(self, mock_stdout, mock_get_headers, mock_get):
        mock_get_headers.return_value = {"Authentication": "test_api_key"}

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.mock_domain_response
        mock_get.return_value = mock_response

        cli.list_domains(self.test_config)

        # Verify API call
        mock_get.assert_called_once_with(
            f"{cli.BASE_URL}/api/custom_domains",
            headers={"Authentication": "test_api_key"},
            timeout=10,
        )

        # Check output
        output = mock_stdout.getvalue()
        self.assertIn("testdomain.com", output)

    @patch("simplelogin.cli.requests.get")
    @patch("simplelogin.cli.get_headers")
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_domain_info(self, mock_stdout, mock_get_headers, mock_get):
        mock_get_headers.return_value = {"Authentication": "test_api_key"}

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.mock_domain_response
        mock_get.return_value = mock_response

        cli.domain_info(self.test_config, "456")

        # Verify API call
        mock_get.assert_called_once_with(
            f"{cli.BASE_URL}/api/custom_domains",
            headers={"Authentication": "test_api_key"},
            timeout=10,
        )

        # Check output
        output = mock_stdout.getvalue()
        self.assertIn("testdomain.com", output)
        self.assertIn("Catch-all: Disabled", output)

    @patch("simplelogin.cli.requests.patch")
    @patch("simplelogin.cli.domain_info")  # Mock this to avoid duplicate testing
    @patch("simplelogin.cli.get_headers")
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_update_domain(
        self, mock_stdout, mock_get_headers, mock_domain_info, mock_patch
    ):
        mock_get_headers.return_value = {"Authentication": "test_api_key"}

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_patch.return_value = mock_response

        cli.update_domain(
            self.test_config,
            "456",
            catch_all="true",
            random_prefix="false",
            name="New Domain Name",
            mailboxes="789,790",
        )

        # Verify API call
        mock_patch.assert_called_once_with(
            f"{cli.BASE_URL}/api/custom_domains/456",
            headers={"Authentication": "test_api_key"},
            json={
                "catch_all": True,
                "random_prefix_generation": False,
                "name": "New Domain Name",
                "mailbox_ids": [789, 790],
            },
            timeout=10,
        )

        # Check output
        output = mock_stdout.getvalue()
        self.assertIn("Domain updated successfully", output)

    @patch("simplelogin.cli.requests.get")
    @patch("simplelogin.cli.get_headers")
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_list_mailboxes(self, mock_stdout, mock_get_headers, mock_get):
        mock_get_headers.return_value = {"Authentication": "test_api_key"}

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.mock_mailbox_response
        mock_get.return_value = mock_response

        cli.list_mailboxes(self.test_config)

        # Verify API call
        mock_get.assert_called_once_with(
            f"{cli.BASE_URL}/api/v2/mailboxes",
            headers={"Authentication": "test_api_key"},
            timeout=10,
        )

        # Check output
        output = mock_stdout.getvalue()
        self.assertIn("user@example.com", output)

    @patch("simplelogin.cli.save_config")
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_set_api_key(self, mock_stdout, mock_save_config):
        cli.set_api_key(self.test_config, "new_api_key")

        # Verify config was updated
        self.assertEqual(self.test_config["api_key"], "new_api_key")
        mock_save_config.assert_called_once_with(self.test_config)

        # Check output
        output = mock_stdout.getvalue()
        self.assertIn("API key saved successfully", output)

    @patch("simplelogin.cli.get_config_file")
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_view_config(self, mock_stdout, mock_get_config_file):
        mock_get_config_file.return_value = self.config_path

        cli.view_config(self.test_config)

        # Check output
        output = mock_stdout.getvalue()
        self.assertIn("API Key (from config file)", output)
        self.assertIn("test**********2345", output)

    @patch("simplelogin.cli.load_config")
    @patch("simplelogin.cli.list_aliases")
    def test_main_list_aliases(self, mock_list_aliases, mock_load_config):
        mock_load_config.return_value = self.test_config
        test_argv = ["simplelogin-cli", "aliases", "list", "--page=1", "--pinned"]
        with patch("sys.argv", test_argv):
            cli.main()

        mock_list_aliases.assert_called_once()
        args, kwargs = mock_list_aliases.call_args
        self.assertEqual(kwargs["page"], 1)
        self.assertTrue(kwargs["pinned"])

    @patch("simplelogin.cli.load_config")
    @patch("simplelogin.cli.create_custom_alias")
    def test_main_create_custom_alias(self, mock_create_alias, mock_load_config):
        mock_load_config.return_value = self.test_config
        test_argv = [
            "simplelogin-cli",
            "aliases",
            "create",
            "custom",
            "prefix",
            "0",
            "--mailboxes=1,2",
            "--note=Test",
            "--name=Test",
        ]
        with patch("sys.argv", test_argv):
            cli.main()

        mock_create_alias.assert_called_once()
        args, kwargs = mock_create_alias.call_args
        self.assertEqual(args[1], "prefix")
        self.assertEqual(args[2], 0)
        self.assertEqual(kwargs["mailbox_ids"], [1, 2])
        self.assertEqual(kwargs["note"], "Test")

    @patch("simplelogin.cli.load_config")
    @patch("simplelogin.cli.toggle_alias")
    def test_main_toggle_alias(self, mock_toggle, mock_load_config):
        mock_load_config.return_value = self.test_config
        test_argv = ["simplelogin-cli", "aliases", "toggle", "123"]
        with patch("sys.argv", test_argv):
            cli.main()

        mock_toggle.assert_called_once_with(unittest.mock.ANY, "123")


if __name__ == "__main__":
    unittest.main()
