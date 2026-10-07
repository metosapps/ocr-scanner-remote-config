# OCR Scanner remote configuration

Public configuration for **OCR Scanner – PDF & Text**, Android package `com.chandra.ocr.offline`, Galaxy Store edition only. Public AdMob identifiers are configuration values, not credentials. This repository contains no keys, customer data, signing material, code to be downloaded by the app, or OCR documents.

Endpoint: `https://raw.githubusercontent.com/metosapps/ocr-scanner-remote-config/main/config_galaxy.json`

This release uses **Google demonstration Native, App Open, and Interstitial ad units exclusively**, including signed release builds. `production_ads_enabled` must remain `false`. A remote change cannot turn these builds into production advertising. Production ads require a later reviewed build, unit IDs for this exact application, a live store release, and explicit authorization.

## Editing

1. Edit `config_galaxy.json` and increase `revision` for each meaningful change.
2. Preserve `schema_version`, `package_name`, `store`, `admob_app_id`, and the three official demo unit IDs.
3. Run `python3 validate.py` and inspect the diff before committing.
4. After publishing, verify the raw endpoint. Installed 1.2.0 clients refresh every five minutes and when the app requests a refresh. GitHub propagation and offline clients can delay a change.

To stop all ad requests, set either `kill_switches.ads_enabled` or `ads.enabled` to `false`, and increase `revision`. After a validated fetch, the client immediately invalidates ad eligibility and discards loaded ads. Per-placement `enabled` switches stop individual formats. `test_ads_enabled=false` stops ads too; it does not select production ads.

Frequency values can reduce ad frequency. Compiled minimums prevent Native refresh below 60 seconds; App Open cooldown below 300 seconds or background duration below 30 seconds; Interstitial cooldown below 120 seconds or fewer than three completed document exits; and shared full-screen spacing below 120 seconds. Loaded ads expire within one hour. Consent, Pro entitlement, document flow, lifecycle, and purchases remain local hard gates.

The client permits only HTTPS requests to the fixed raw endpoint, refuses redirects, limits each response to 64 KiB, validates the full payload, and uses five-second network timeouts. Last-good config remains usable for at most 24 hours. Expired or missing config disables advertising while OCR stays available. A lower revision is rejected. A device already offline cannot receive a new kill switch until reconnecting.

## Updates and links

`update_mode` is currently `none`: version 1.2.0 is in preparation, so no user is forced to update. Never activate a force update until the target version is publicly available in the intended Galaxy Store regions. `min_supported_version_code` controls the force threshold, while `latest_version_code` supports an optional update suggestion. The app opens the official store page; it never downloads or installs APKs from config.

Maintenance is disabled. Messages and feature flags are data, not executable code. Links remain restricted to this application's GitHub Pages site, its public support email, and its exact Samsung listing.

## Rollback

`config_galaxy_ads_disabled.json` is a prepared all-ads-off template. Before promoting it to `config_galaxy.json`, set `revision` above the latest deployed revision. Do not roll back the revision counter or activate update/maintenance gates as part of an advertising rollback.

Documentation for Google's demo unit IDs: https://developers.google.com/admob/android/test-ads
