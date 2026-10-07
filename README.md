# OCR Scanner remote configuration

Public configuration for **OCR Scanner – PDF & Text**, Android package `com.chandra.ocr.offline`, Galaxy Store edition only. Public AdMob identifiers are configuration values, not credentials. This repository contains no keys, customer data, signing material, downloaded executable code, purchase receipts or OCR documents.

Endpoint: `https://raw.githubusercontent.com/metosapps/ocr-scanner-remote-config/main/config_galaxy.json`

## Current state: OFF

Revision **3** disables all advertising: `test_ads_enabled=false`, `production_ads_enabled=false`, both global ad switches false and all placement switches false. The three official Google demo IDs remain in `unit_id` for compatibility; stored IDs alone cannot enable requests. The provided publisher ad units are stored separately in `production_unit_id`; adding these values **does not activate production ads**. The prepared 1.2.1 (8) release can select validated units from config. Debug builds always block production requests. The earlier 1.2.0 build uses demo units only and ignores the new fields.

| Format | Demo `unit_id` | Configured `production_unit_id` (inactive) |
| --- | --- | --- |
| Native | `ca-app-pub-3940256099942544/2247696110` | `ca-app-pub-3289974964220873/4604140089` |
| App Open | `ca-app-pub-3940256099942544/9257395921` | `ca-app-pub-3289974964220873/5075658238` |
| Interstitial | `ca-app-pub-3940256099942544/1033173712` | `ca-app-pub-3289974964220873/4468408713` |

## Modes and boundaries

- **TEST:** `test_ads_enabled=true`, `production_ads_enabled=false`. Every enabled placement uses its official demo unit, regardless of configured production values.
- **PRODUCTION:** `test_ads_enabled=false`, `production_ads_enabled=true`. Supported release builds select production IDs for enabled placements only. All supplied IDs must belong to publisher `3289974964220873`, have a nonzero ten-digit unit suffix, and be distinct per format. Empty IDs for enabled production placements are invalid. Debug cannot enter this mode.
- **OFF:** both mode flags false or missing, either global ad switch false, or no enabled placements. Both mode flags true are invalid and the entire response is rejected.

Test and production advertising are currently **OFF** following the publisher’s shutdown request. A future mode change requires explicit publisher authorization after this exact app/build is live and its AdMob setup is ready. The schema describes capability, not permission to activate it. Google test ads still use network services and do not create commercial advertising revenue. Consent, Pro, lifecycle, purchases and document-flow rules cannot be overridden remotely.

## Editing and rollback

1. Edit `config_galaxy.json` and increase `revision` for every meaningful change.
2. Preserve `schema_version`, `package_name`, `store`, `admob_app_id`, and the demo `unit_id` values. Update production IDs only for this exact app/publisher and their proper format.
3. Run `python3 validate.py` and inspect the diff before committing.
4. After publishing, verify the raw endpoint. Clients refresh every five minutes and on requested foreground refresh; GitHub propagation and offline devices can delay a change.

To stop all requests, set `kill_switches.ads_enabled=false` or `ads.enabled=false` and increase `revision`. A validated response immediately invalidates ad eligibility and cached loaded ads. Per-placement `enabled` switches stop individual formats. Changing a selected production ID invalidates earlier loaded/in-flight ads before another request can use that placement.

`config_galaxy_ads_disabled.json` is an all-ads-off rollback template at revision **4**. Before promoting it to `config_galaxy.json`, choose a revision higher than the latest deployed revision. Do not reduce revisions or activate update/maintenance gates as part of an ad rollback.

## Frequency and offline behavior

Compiled floors prevent Native refresh below 60 seconds; App Open cooldown below 300 seconds or background duration below 30 seconds; Interstitial cooldown below 120 seconds or fewer than three completed document exits; and shared full-screen spacing below 120 seconds. Loaded ads expire within one hour. Numeric changes may reduce frequency but cannot bypass these minimums.

The client uses HTTPS to the fixed raw endpoint, rejects redirects, limits UTF-8 responses to 64 KiB, validates the complete payload, and uses five-second network timeouts. Fresh validated config/cache is required before ad requests. Last-good configuration lasts less than 24 hours. Missing/expired config disables ads while OCR remains available. A lower revision is rejected. A device already offline cannot receive a new switch until it reconnects.

Malformed remote data preserves only unexpired last-good configuration. Use an explicit valid kill switch to stop ads; invalid JSON is not a reliable way to disable them.

## Updates and links

`update_mode` remains `none`: 1.2.1 (8) is being prepared, so no user is forced to update. Never enable a force update until the target release is live in the intended Galaxy regions. `min_supported_version_code` controls the force threshold; `latest_version_code` supports an optional suggestion. The app opens its official store listing and never downloads/installs an APK through config.

Maintenance is disabled. Messages and boolean feature flags are data, not code. Links remain restricted to this app's GitHub Pages site, public support email and exact Samsung listing.

Google demonstration unit documentation: https://developers.google.com/admob/android/test-ads
