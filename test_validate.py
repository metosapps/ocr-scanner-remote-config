"""Regression tests for remote caps, identity isolation and the safe legacy bridge."""
from copy import deepcopy
from pathlib import Path
import json
import tempfile
import unittest

from validate import CONFIG_FILES, ROOT, UNITS, ValidationError, read_config, validate_config

class ConfigValidationTest(unittest.TestCase):
    def setUp(self):
        self.config = read_config(ROOT / "config_galaxy_v2.json")

    def test_all_four_repository_configs_validate_off(self):
        for name in CONFIG_FILES:
            with self.subTest(name=name):
                self.assertEqual("OFF", validate_config(read_config(ROOT / name)))

    def test_legacy_endpoint_and_rollback_remain_entirely_off(self):
        for name in ("config_galaxy.json", "config_galaxy_ads_disabled.json"):
            config = read_config(ROOT / name)
            self.assertEqual(1, config["schema_version"])
            self.assertFalse(config["kill_switches"]["ads_enabled"])
            ads = config["ads"]
            for key in ("enabled", "test_ads_enabled", "production_ads_enabled"):
                self.assertFalse(ads[key])
            for placement in UNITS:
                self.assertFalse(ads[placement]["enabled"])

    def test_two_endpoints_preserve_identity_units_and_no_force_update(self):
        legacy = read_config(ROOT / "config_galaxy.json")
        self.assertEqual(2, self.config["schema_version"])
        for config in (legacy, self.config):
            self.assertEqual(4, config["revision"])
            self.assertEqual("com.chandra.ocr.offline", config["package_name"])
            self.assertEqual("galaxy_store", config["store"])
            self.assertEqual("ca-app-pub-3289974964220873~9382181867", config["admob_app_id"])
            update = config["android"]["galaxy_store"]
            self.assertEqual((1, 10, "1.3.1", "none"), (update["min_supported_version_code"], update["latest_version_code"], update["latest_version_name"], update["update_mode"]))
            expected = {"native":"4604140089", "app_open":"5075658238", "interstitial":"4468408713"}
            for placement, suffix in expected.items():
                self.assertEqual("ca-app-pub-3289974964220873/" + suffix, config["ads"][placement]["production_unit_id"])

    def test_rollbacks_are_higher_revision_and_match_their_endpoint_schema(self):
        for source, rollback in (("config_galaxy.json", "config_galaxy_ads_disabled.json"), ("config_galaxy_v2.json", "rollback_ads_off_v2.json")):
            current = read_config(ROOT / source)
            disabled = read_config(ROOT / rollback)
            self.assertEqual(current["schema_version"], disabled["schema_version"])
            self.assertGreater(disabled["revision"], current["revision"])

    def test_legacy_schema_accepts_absent_new_controls(self):
        self.assertEqual("OFF", validate_config(read_config(ROOT / "config_galaxy.json")))

    def test_schema1_validates_new_controls_when_supplied(self):
        self.config["schema_version"] = 1
        self.assertEqual("OFF", validate_config(self.config))
        self.config["ads"]["app_open"]["max_per_session"] = 11
        with self.assertRaises(ValidationError):
            validate_config(self.config)

    def control_paths(self):
        return [
            (("ads", "load_retry_seconds"), 30, 300),
            (("ads", "max_fullscreen_per_session"), 0, 10),
            (("ads", "max_fullscreen_per_day"), 0, 20),
            (("ads", "app_open", "max_per_session"), 0, 10),
            (("ads", "app_open", "max_per_day"), 0, 20),
            (("ads", "app_open", "minimum_session_seconds"), 300, 86400),
            (("ads", "interstitial", "max_per_session"), 0, 10),
            (("ads", "interstitial", "max_per_day"), 0, 20),
            (("ads", "interstitial", "minimum_session_seconds"), 120, 86400),
        ]

    def target(self, config, path):
        target = config
        for key in path[:-1]:
            target = target[key]
        return target, path[-1]

    def test_new_control_boundaries_and_zero_caps_are_valid(self):
        for path, minimum, maximum in self.control_paths():
            for value in (minimum, maximum):
                with self.subTest(path=path, value=value):
                    config = deepcopy(self.config)
                    target, key = self.target(config, path)
                    target[key] = value
                    self.assertEqual("OFF", validate_config(config))

    def test_new_controls_reject_out_of_range_and_wrong_types(self):
        for path, minimum, maximum in self.control_paths():
            for value in (minimum - 1, maximum + 1, True, 1.5, "2", None):
                with self.subTest(path=path, value=value):
                    config = deepcopy(self.config)
                    target, key = self.target(config, path)
                    target[key] = value
                    with self.assertRaises(ValidationError):
                        validate_config(config)

    def test_schema2_requires_every_new_control(self):
        for path, _, _ in self.control_paths():
            with self.subTest(path=path):
                config = deepcopy(self.config)
                target, key = self.target(config, path)
                del target[key]
                with self.assertRaises(ValidationError):
                    validate_config(config)
        del self.config["ads"]["app_open"]["allowed_screens"]
        with self.assertRaises(ValidationError):
            validate_config(self.config)

    def test_distinct_screen_subsets_and_empty_disable_list_are_valid(self):
        for screens in ([], ["home"], ["history", "favorites"], ["home", "history", "favorites"]):
            self.config["ads"]["app_open"]["allowed_screens"] = screens
            self.assertEqual("OFF", validate_config(self.config))

    def test_screen_lists_reject_duplicates_unknown_routes_and_wrong_types(self):
        for value in (["home", "home"], ["settings"], ["document"], [True], "home", None):
            with self.subTest(value=value):
                self.config["ads"]["app_open"]["allowed_screens"] = value
                with self.assertRaises(ValidationError):
                    validate_config(self.config)

    def test_unchanged_frequency_floors_are_enforced(self):
        floors = [(('ads', 'native', 'refresh_seconds'), 60), (('ads', 'app_open', 'cooldown_seconds'), 300), (('ads', 'app_open', 'minimum_background_seconds'), 30), (('ads', 'interstitial', 'cooldown_seconds'), 120), (('ads', 'interstitial', 'minimum_completed_document_exits'), 3), (('ads', 'minimum_fullscreen_interval_seconds'), 120)]
        for path, floor in floors:
            config = deepcopy(self.config)
            target, key = self.target(config, path)
            target[key] = floor - 1
            with self.subTest(path=path), self.assertRaises(ValidationError):
                validate_config(config)

    def test_conflicting_modes_and_wrong_publisher_units_are_rejected(self):
        self.config["ads"].update(test_ads_enabled=True, production_ads_enabled=True)
        with self.assertRaises(ValidationError):
            validate_config(self.config)
        self.config = read_config(ROOT / "config_galaxy_v2.json")
        self.config["ads"]["native"]["production_unit_id"] = "ca-app-pub-1111111111111111/4604140089"
        with self.assertRaises(ValidationError):
            validate_config(self.config)

    def test_enabled_production_placement_requires_distinct_valid_unit(self):
        self.config["ads"]["production_ads_enabled"] = True
        self.config["ads"]["native"].update(enabled=True, production_unit_id="")
        with self.assertRaises(ValidationError):
            validate_config(self.config)
        self.config["ads"]["native"]["production_unit_id"] = self.config["ads"]["app_open"]["production_unit_id"]
        with self.assertRaises(ValidationError):
            validate_config(self.config)

    def test_wrong_package_store_app_id_and_schema_are_rejected(self):
        for key, value in (("package_name", "com.other.app"), ("store", "google_play"), ("admob_app_id", "ca-app-pub-1111111111111111~1111111111"), ("schema_version", 3), ("schema_version", True)):
            config = deepcopy(self.config)
            config[key] = value
            with self.subTest(key=key), self.assertRaises(ValidationError):
                validate_config(config)

    def test_unsafe_links_and_malformed_version_fields_are_rejected(self):
        for value in ("http://metosapps.github.io/ocr-scanner-website/privacy.html", "https://other.example/privacy.html", "https://metosapps.github.io/ocr-scanner-website/../other/", "https://metosapps.github.io/ocr-scanner-website/privacy.html?token=x", "https://metosapps.github.io/ocr-scanner-website/privacy.html\n"):
            config = deepcopy(self.config)
            config["links"]["privacy_policy"] = value
            with self.subTest(value=value), self.assertRaises(ValidationError):
                validate_config(config)
        self.config["android"]["galaxy_store"]["latest_version_code"] = True
        with self.assertRaises(ValidationError):
            validate_config(self.config)

    def test_json_rejects_duplicate_keys_nonfinite_values_and_oversize_input(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "invalid.json"
            for raw in (b'{"schema_version":1,"schema_version":2}', b'{"number":NaN}', b' ' * 65537, b'\xff'):
                path.write_bytes(raw)
                with self.subTest(raw=raw[:40]), self.assertRaises(ValidationError):
                    read_config(path)

if __name__ == "__main__":
    unittest.main()
