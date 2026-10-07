#!/usr/bin/env python3
"""Local/CI check for package-isolated Galaxy ad configuration and safe modes."""
import json
import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
PACKAGE = "com.chandra.ocr.offline"
UNITS = {
    "native": "ca-app-pub-3940256099942544/2247696110",
    "app_open": "ca-app-pub-3940256099942544/9257395921",
    "interstitial": "ca-app-pub-3940256099942544/1033173712",
}

def validate(path):
    raw = path.read_bytes()
    assert len(raw) <= 65536, "Config exceeds 64 KiB"
    config = json.loads(raw)
    assert config["schema_version"] == 1
    assert type(config["revision"]) is int and config["revision"] >= 1
    assert config["package_name"] == PACKAGE and config["store"] == "galaxy_store"
    assert config["admob_app_id"] == "ca-app-pub-3289974964220873~9382181867"
    ads = config["ads"]
    test_mode = ads.get("test_ads_enabled", False)
    production_mode = ads.get("production_ads_enabled", False)
    assert type(test_mode) is bool and type(production_mode) is bool
    assert not (test_mode and production_mode), "Ambiguous ad mode"
    production_units = []
    for placement, unit in UNITS.items():
        assert ads[placement]["unit_id"] == unit
        assert type(ads[placement]["enabled"]) is bool
        production_unit = ads[placement].get("production_unit_id", "")
        assert type(production_unit) is str
        valid = bool(re.fullmatch(r"ca-app-pub-3289974964220873/[0-9]{10}", production_unit)) and production_unit.rsplit("/", 1)[-1] != "0000000000"
        assert not production_unit or valid, f"Invalid {placement} production unit"
        assert not (production_mode and ads[placement]["enabled"]) or valid, f"Missing {placement} production unit"
        if production_unit:
            production_units.append(production_unit)
    assert len(production_units) == len(set(production_units)), "Production units must be unique per format"
    assert type(ads["enabled"]) is bool
    assert ads["native"]["refresh_seconds"] >= 60
    assert ads["app_open"]["cooldown_seconds"] >= 300
    assert ads["app_open"]["minimum_background_seconds"] >= 30
    assert ads["interstitial"]["cooldown_seconds"] >= 120
    assert ads["interstitial"]["minimum_completed_document_exits"] >= 3
    assert ads["minimum_fullscreen_interval_seconds"] >= 120
    assert 1 <= ads["ad_lifetime_seconds"] <= 3600
    update = config["android"]["galaxy_store"]
    assert update["update_mode"] in ("none", "soft", "force")
    assert 1 <= update["min_supported_version_code"] <= update["latest_version_code"]
    assert update["update_url"] == "samsungapps://ProductDetail/" + PACKAGE
    assert config["links"]["rating"] == update["update_url"]
    assert config["links"]["support_email"] == "chennoufo11@gmail.com"
    for key in ("privacy_policy", "terms", "website", "help"):
        url = urlparse(config["links"][key])
        assert url.scheme == "https" and url.netloc == "metosapps.github.io"
        assert url.path.startswith("/ocr-scanner-website/") and ".." not in url.path and "%" not in url.path
        assert not url.query and not url.fragment
    for value in config["kill_switches"].values():
        assert type(value) is bool
    for value in config["features"].values():
        assert type(value) is bool
    assert type(config["global"]["maintenance_mode"]) is bool
    mode = "TEST" if test_mode else "PRODUCTION" if production_mode else "OFF"
    if not ads["enabled"] or not config["kill_switches"]["ads_enabled"]:
        mode = "OFF"
    print(f"Validated {path.name}: package={PACKAGE}, revision={config['revision']}, mode={mode}")

if __name__ == "__main__":
    for file in sorted(ROOT.glob("config_galaxy*.json")):
        validate(file)
