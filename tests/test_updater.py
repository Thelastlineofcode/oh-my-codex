"""Tests for updater module."""
import pytest
import json
import subprocess
from unittest.mock import patch, MagicMock
from urllib.error import URLError
from orchestrator.updater import Updater, VersionInfo


class TestVersionInfo:
    def test_create(self):
        info = VersionInfo(current="1.0.0", latest="1.1.0", update_available=True)
        assert info.current == "1.0.0"
        assert info.latest == "1.1.0"
        assert info.update_available is True

    def test_defaults(self):
        info = VersionInfo(current="1.0.0", latest="1.0.0", update_available=False)
        assert info.changelog_url == ""


class TestUpdater:
    def test_current_version(self):
        u = Updater(current_version="1.0.0")
        assert u.current_version == "1.0.0"

    def test_current_version_property(self):
        updater = Updater(current_version="1.2.3")
        assert updater.current_version == "1.2.3"

    def test_current_version_default(self):
        updater = Updater()
        assert isinstance(updater.current_version, str)

    def test_compare_versions_equal(self):
        updater = Updater("1.0.0")
        assert updater._compare_versions("1.0.0", "1.0.0") is False

    def test_compare_versions_newer(self):
        u = Updater(current_version="0.1.0")
        assert u._compare_versions("0.1.0", "0.2.0") is True

    def test_compare_versions_newer_available(self):
        updater = Updater("1.0.0")
        assert updater._compare_versions("1.0.0", "1.1.0") is True

    def test_compare_versions_same(self):
        u = Updater(current_version="1.0.0")
        assert u._compare_versions("1.0.0", "1.0.0") is False

    def test_compare_versions_older(self):
        u = Updater(current_version="2.0.0")
        assert u._compare_versions("2.0.0", "1.0.0") is False

    def test_compare_versions_older_available(self):
        updater = Updater("2.0.0")
        assert updater._compare_versions("2.0.0", "1.9.9") is False

    def test_compare_versions_patch(self):
        u = Updater()
        assert u._compare_versions("1.0.0", "1.0.1") is True

    def test_compare_versions_different_lengths(self):
        updater = Updater("1.0")
        assert updater._compare_versions("1.0", "1.0.1") is True

    def test_compare_versions_pad_shorter(self):
        updater = Updater("1.0.0")
        assert updater._compare_versions("1.0.0", "1.0") is False

    def test_compare_versions_invalid(self):
        u = Updater()
        assert u._compare_versions("abc", "xyz") is False

    def test_compare_versions_major_minor_patch(self):
        updater = Updater("1.2.3")
        assert updater._compare_versions("1.2.3", "1.2.4") is True
        assert updater._compare_versions("1.2.3", "1.3.0") is True
        assert updater._compare_versions("1.2.3", "2.0.0") is True

    @patch("orchestrator.updater.urllib.request.urlopen")
    def test_check_update_available(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_resp.read.return_value = b'{"info": {"version": "9.9.9"}}'
        mock_resp.status = 200
        mock_urlopen.return_value = mock_resp
        u = Updater(current_version="0.1.0")
        info = u.check_update()
        assert info.update_available is True
        assert info.latest == "9.9.9"

    @patch("orchestrator.updater.urllib.request.urlopen")
    def test_check_update_success(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({
            "info": {"version": "1.5.0"}
        }).encode()
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock()
        mock_urlopen.return_value = mock_resp

        updater = Updater("1.0.0")
        info = updater.check_update()
        assert info.current == "1.0.0"
        assert info.latest == "1.5.0"
        assert info.update_available is True
        assert "releases" in info.changelog_url

    @patch("orchestrator.updater.urllib.request.urlopen")
    def test_check_update_current(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_resp.read.return_value = b'{"info": {"version": "0.2.0"}}'
        mock_urlopen.return_value = mock_resp
        u = Updater(current_version="0.2.0")
        info = u.check_update()
        assert info.update_available is False

    @patch("orchestrator.updater.urllib.request.urlopen")
    def test_check_update_network_error(self, mock_urlopen):
        mock_urlopen.side_effect = URLError("no network")
        u = Updater(current_version="0.1.0")
        info = u.check_update()
        assert info.update_available is False
        assert info.latest == "unknown"

    @patch("orchestrator.updater.urllib.request.urlopen")
    def test_check_update_invalid_json(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = b"not json"
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = lambda *args: None
        mock_urlopen.return_value = mock_resp

        updater = Updater("1.0.0")
        info = updater.check_update()
        assert info is not None
        assert info.update_available is False
        assert info.latest == "unknown"

    @patch("orchestrator.updater.subprocess.run")
    def test_update_success(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        u = Updater(current_version="0.1.0")
        success, msg = u.update(force=True)
        assert success is True

    @patch("orchestrator.updater.urllib.request.urlopen")
    @patch("orchestrator.updater.subprocess.run")
    def test_update_success_with_check(self, mock_run, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({
            "info": {"version": "2.0.0"}
        }).encode()
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock()
        mock_urlopen.return_value = mock_resp
        mock_run.return_value = MagicMock(returncode=0, stdout="Success", stderr="")

        updater = Updater("1.0.0")
        success, message = updater.update()
        assert success is True
        assert "Updated successfully" in message

    @patch("orchestrator.updater.urllib.request.urlopen")
    def test_update_already_current(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({
            "info": {"version": "1.0.0"}
        }).encode()
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock()
        mock_urlopen.return_value = mock_resp

        updater = Updater("1.0.0")
        success, message = updater.update()
        assert success is False
        assert "Already up to date" in message

    @patch("orchestrator.updater.subprocess.run")
    def test_update_failure(self, mock_run):
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="error")
        u = Updater(current_version="0.1.0")
        success, msg = u.update(force=True)
        assert success is False

    @patch("orchestrator.updater.urllib.request.urlopen")
    @patch("orchestrator.updater.subprocess.run")
    def test_update_failure_with_message(self, mock_run, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({
            "info": {"version": "2.0.0"}
        }).encode()
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock()
        mock_urlopen.return_value = mock_resp
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="Install failed")

        updater = Updater("1.0.0")
        success, message = updater.update()
        assert success is False
        assert "Update failed" in message

    @patch("orchestrator.updater.subprocess.run")
    def test_update_force(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="Success", stderr="")
        updater = Updater("1.0.0")
        success, message = updater.update(force=True)
        assert mock_run.called

    def test_format_update_notice_none(self):
        with patch.object(Updater, "check_update", return_value=VersionInfo(current="1.0.0", latest="1.0.0", update_available=False)):
            u = Updater(current_version="1.0.0")
            assert u.format_update_notice() == ""

    def test_format_update_notice_available(self):
        with patch.object(Updater, "check_update", return_value=VersionInfo(current="0.1.0", latest="0.2.0", update_available=True)):
            u = Updater(current_version="0.1.0")
            notice = u.format_update_notice()
            assert "0.2.0" in notice

    @patch("orchestrator.updater.urllib.request.urlopen")
    def test_format_update_notice_current(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({
            "info": {"version": "1.0.0"}
        }).encode()
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock()
        mock_urlopen.return_value = mock_resp

        updater = Updater("1.0.0")
        notice = updater.format_update_notice()
        assert notice == ""
