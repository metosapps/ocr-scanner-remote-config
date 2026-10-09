#!/usr/bin/env python3
"""Validate package-isolated Galaxy configuration in local development and CI."""
import json
import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
PACKAGE = "com.chandra.ocr.offline"
APP_ID = "ca-app-pub-3289974964220873~9382181867"
STORE_URL = "samsungapps://ProductDetail/" + PACKAGE
UNITS = {
    "native": "ca-app-pub-3940256099942544/2247696110",
    "app_open": "ca-app-pub-3940256099942544/9257395921",
    "interstitial": "ca-app-pub-3940256099942544/1033173712",
}
SCREENS = {"home", "history", "favorites"}
CONFIG_FILES = ("config_galaxy.json", "config_galaxy_v2.json", "config_galaxy_ads_disabled.json", "rollback_ads_off_v2.json")

class ValidationError(ValueError):
    pass

def require(condition, message):
    if not condition:
        raise ValidationError(message)

def field(obj, key, kind):
    require(type(obj) is dict and key in obj, f"Missing {key}")
    value = obj[key]
    require(type(value) is kind, f"Invalid type for {key}")
    return value

def integer(obj, key, minimum, maximum):
    value = field(obj, key, int)
    require(minimum <= value <= maximum, f"{key} must be in {minimum}..{maximum}")
    return value

def new_integer(obj, key, minimum, maximum, schema):
    if schema == 2 or key in obj:
        integer(obj, key, minimum, maximum)

def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f"Duplicate JSON key: {key}")
        result[key] = value
    return result

def reject_constant(value):
    raise ValidationError(f"Non-finite JSON number: {value}")

def read_config(path):
    raw = Path(path).read_bytes()
    require(len(raw) <= 65536, "Config exceeds 64 KiB")
    try:
        return json.loads(raw.decode("utf-8"), object_pairs_hook=unique_object, parse_constant=reject_constant)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValidationError("Invalid UTF-8 JSON") from error

def validate_config(config):
    schema = integer(config, "schema_version", 1, 2)
    integer(config, "revision", 1, 9223372036854775807)
    require(field(config, "package_name", str) == PACKAGE, "Wrong package")
    require(field(config, "store", str) == "galaxy_store", "Wrong store")
    require(field(config, "admob_app_id", str) == APP_ID, "Wrong AdMob App ID")
    ads = field(config, "ads", dict)
    test_mode = ads.get("test_ads_enabled", False)
    production_mode = ads.get("production_ads_enabled", False)
    require(type(test_mode) is bool and type(production_mode) is bool, "Invalid mode flags")
    require(not (test_mode and production_mode), "Ambiguous ad mode")
    production_units = []
    for placement, unit in UNITS.items():
        placement_config = field(ads, placement, dict)
        require(field(placement_config, "unit_id", str) == unit, f"Wrong {placement} demo unit")
        enabled = field(placement_config, "enabled", bool)
        production_unit = placement_config.get("production_unit_id", "")
        require(type(production_unit) is str, f"Invalid {placement} production unit type")
        valid = bool(re.fullmatch(r"ca-app-pub-3289974964220873/[0-9]{10}", production_unit)) and production_unit.rsplit("/", 1)[-1] != "0000000000"
        require(not production_unit or valid, f"Invalid {placement} production unit")
        require(not (production_mode and enabled) or valid, f"Missing {placement} production unit")
        if production_unit:
            production_units.append(production_unit)
    require(len(production_units) == len(set(production_units)), "Production units must be unique per format")
    field(ads, "enabled", bool)
    integer(ads["native"], "refresh_seconds", 60, 86400)
    integer(ads["app_open"], "cooldown_seconds", 300, 86400)
    integer(ads["app_open"], "minimum_background_seconds", 30, 86400)
    integer(ads["interstitial"], "cooldown_seconds", 120, 86400)
    integer(ads["interstitial"], "minimum_completed_document_exits", 3, 100)
    integer(ads, "minimum_fullscreen_interval_seconds", 120, 86400)
    integer(ads, "ad_lifetime_seconds", 1, 3600)
    new_integer(ads, "load_retry_seconds", 30, 300, schema)
    new_integer(ads, "max_fullscreen_per_session", 0, 10, schema)
    new_integer(ads, "max_fullscreen_per_day", 0, 20, schema)
    for placement, floor in (("app_open", 300), ("interstitial", 120)):
        values = ads[placement]
        new_integer(values, "max_per_session", 0, 10, schema)
        new_integer(values, "max_per_day", 0, 20, schema)
        new_integer(values, "minimum_session_seconds", floor, 86400, schema)
    app_open = ads["app_open"]
    if schema == 2 or "allowed_screens" in app_open:
        screens = field(app_open, "allowed_screens", list)
        require(all(type(screen) is str and screen in SCREENS for screen in screens), "Invalid App Open screen")
        require(len(screens) == len(set(screens)), "App Open screens must be distinct")
    update = field(field(config, "android", dict), "galaxy_store", dict)
    require(field(update, "update_mode", str) in ("none", "soft", "flexible", "force", "immediate"), "Invalid update mode")
    minimum = integer(update, "min_supported_version_code", 1, 9223372036854775807)
    integer(update, "latest_version_code", minimum, 9223372036854775807)
    name = field(update, "latest_version_name", str)
    require(len(name) <= 20 and bool(re.fullmatch(r"[0-9]+(?:\.[0-9]+){1,3}", name)), "Invalid version name")
    require(field(update, "update_url", str) == STORE_URL, "Wrong update URL")
    links = field(config, "links", dict)
    require(field(links, "rating", str) == STORE_URL, "Wrong rating URL")
    require(field(links, "support_email", str) == "chennoufo11@gmail.com", "Wrong support email")
    for key in ("privacy_policy", "terms", "website", "help"):
        value = field(links, key, str)
        require(len(value) <= 500 and all(ord(char) >= 32 for char in value), f"Invalid {key} URL")
        url = urlparse(value)
        require(url.scheme == "https" and url.netloc == "metosapps.github.io", f"Unsafe {key} host")
        require(url.path.startswith("/ocr-scanner-website/") and ".." not in url.path and "%" not in url.path and "\\" not in url.path, f"Unsafe {key} path")
        require(not url.query and not url.fragment, f"Unsafe {key} suffix")
    switches = field(config, "kill_switches", dict)
    field(switches, "ads_enabled", bool)
    field(switches, "iap_enabled", bool)
    require(all(type(value) is bool for value in switches.values()), "Invalid kill switch")
    features = field(config, "features", dict)
    require(len(features) <= 32, "Too many feature flags")
    require(all(type(key) is str and re.fullmatch(r"[a-z][a-z0-9_]{0,63}", key) and type(value) is bool for key, value in features.items()), "Invalid feature flag")
    global_config = field(config, "global", dict)
    field(global_config, "maintenance_mode", bool)
    message = field(global_config, "maintenance_message", str)
    require(len(message) <= 500 and all(ord(char) >= 32 or char in "\n\t" for char in message), "Invalid maintenance message")
    mode = "TEST" if test_mode else "PRODUCTION" if production_mode else "OFF"
    if not ads["enabled"] or not switches["ads_enabled"] or not any(ads[key]["enabled"] for key in UNITS):
        mode = "OFF"
    return mode

def validate(path):
    config = read_config(path)
    mode = validate_config(config)
    print(f"Validated {Path(path).name}: schema={config['schema_version']}, package={PACKAGE}, revision={config['revision']}, mode={mode}")
    return config

if __name__ == "__main__":
    for name in CONFIG_FILES:
        validate(ROOT / name)
