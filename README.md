# OCR Scanner remote configuration

Public configuration for **OCR Scanner – PDF & Text**, Android package `com.chandra.ocr.offline`, Galaxy Store edition. AdMob identifiers are public configuration values. No credentials, signing material, OCR documents, purchase receipts or customer data belong in this repository.

## Production enabled on the current endpoint

| Client | File / endpoint | Schema | Revision | Advertising |
| --- | --- | --- | --- | --- |
| Earlier APKs | [config_galaxy.json](https://raw.githubusercontent.com/metosapps/ocr-scanner-remote-config/main/config_galaxy.json) | 1 | 4 | Permanently OFF under this migration strategy |
| 1.3.1 (10) and later | [config_galaxy_v2.json](https://raw.githubusercontent.com/metosapps/ocr-scanner-remote-config/main/config_galaxy_v2.json) | 2 | 5 | PRODUCTION; bounded Native, App Open and Interstitial |

On 2026-10-10 the publisher explicitly authorized production activation. The current schema-2 endpoint sets `test_ads_enabled=false`, `production_ads_enabled=true`, both global ad switches true, and all three format switches true. The schema-1 endpoint and rollback templates keep every advertising switch false. Existing frequency, session/day caps, consent, Pro and debug restrictions continue to apply. This is remote request enablement; no physical-device ad fill or Galaxy publication is established by it. Maintenance is disabled. Version metadata is `latest_version_code=10`, `latest_version_name="1.3.1"`, `min_supported_version_code=1`, `update_mode="none"`. Version metadata does not prove Galaxy approval or publication and forces no update.

The separate schema-2 endpoint prevents old APKs from serving ads while ignoring new caps. Keep the schema-1 endpoint's advertising OFF. Any future authorized ad activation belongs only in `config_galaxy_v2.json`. Retaining schema 1 on the old endpoint preserves other supported remote settings for those installations. Publishing schema 2 to the old endpoint would make old clients reject the whole response.

The 1.3.1 client accepts legacy schema 1 with conservative defaults for missing new fields, validates any new fields supplied in schema 1, and requires every new field in schema 2. Earlier APKs reject schema 2. Never use this compatibility rule to activate ads for old clients. Remote configuration cannot add SDKs, alter manifest IDs or permissions, deliver executable code, grant Pro, or bypass consent.

## App-specific identifiers

Manifest App ID: `ca-app-pub-3289974964220873~9382181867`. The manifest value is fixed at build time.

| Format | Demo `unit_id` | Supplied `production_unit_id` (selected by eligible release clients) |
| --- | --- | --- |
| Native | `ca-app-pub-3940256099942544/2247696110` | `ca-app-pub-3289974964220873/4604140089` |
| App Open | `ca-app-pub-3940256099942544/9257395921` | `ca-app-pub-3289974964220873/5075658238` |
| Interstitial | `ca-app-pub-3940256099942544/1033173712` | `ca-app-pub-3289974964220873/4468408713` |

IDs alone cannot enable requests. TEST uses only the exact Google demo IDs. PRODUCTION selects validated publisher IDs in a capable release; Debug blocks PRODUCTION requests. Supplied production IDs must belong to publisher `3289974964220873`, have nonzero ten-digit suffixes, and be distinct across formats. Missing production IDs for enabled production placements are invalid. Both mode flags true invalidate the complete response. Both false select OFF.

The publisher explicitly requested this activation; store availability, published privacy messages and current Data Safety remain separate distribution/account responsibilities. AdMob readiness, demand, consent and Pro status determine whether eligible requests show ads. Test requests also contact Google services; test ads do not generate commercial revenue.

## Control keys

Values are bounded by the compiled app. Zero count caps disable the corresponding full-screen scope; an empty App Open screen list disables App Open. All other eligibility rules still apply.

| Key | Prepared value | Allowed range / effect |
| --- | --- | --- |
| `kill_switches.ads_enabled`, `ads.enabled` | `true`, `true` | Both global switches must be true to allow ads |
| `ads.test_ads_enabled`, `ads.production_ads_enabled` | `false`, `true` | TEST / PRODUCTION / OFF selection; never both true |
| `ads.native.enabled`, `ads.app_open.enabled`, `ads.interstitial.enabled` | `true` | Per-format switches |
| `ads.load_retry_seconds` | `30` | 30–300 seconds minimum interval between load attempts, including reloads after successful ads |
| `ads.max_fullscreen_per_session` | `5` | 0–10, shared App Open + Interstitial cap |
| `ads.max_fullscreen_per_day` | `8` | 0–20, shared full-screen daily cap |
| `ads.app_open.max_per_session` | `2` | 0–10 App Open shows per process session |
| `ads.app_open.max_per_day` | `4` | 0–20 App Open shows per UTC calendar day |
| `ads.app_open.minimum_session_seconds` | `300` | 300–86400 seconds of session age before eligibility |
| `ads.app_open.allowed_screens` | `["home","history","favorites"]` | Distinct subset of those routes; empty disables App Open |
| `ads.interstitial.max_per_session` | `3` | 0–10 Interstitial shows per process session |
| `ads.interstitial.max_per_day` | `6` | 0–20 Interstitial shows per UTC calendar day |
| `ads.interstitial.minimum_session_seconds` | `120` | 120–86400 seconds of session age before eligibility |
| `ads.native.refresh_seconds` | `60` | Existing floor: 60 seconds |
| `ads.app_open.cooldown_seconds` | `300` | Existing floor: 300 seconds |
| `ads.app_open.minimum_background_seconds` | `30` | Existing floor: 30 seconds; no cold-start pop-up |
| `ads.interstitial.cooldown_seconds` | `120` | Existing floor: 120 seconds |
| `ads.interstitial.minimum_completed_document_exits` | `3` | Existing floor: three completed-document exits |
| `ads.minimum_fullscreen_interval_seconds` | `120` | Existing shared spacing floor: 120 seconds |
| `ads.ad_lifetime_seconds` | `3600` | 1–3600 seconds; loaded ads expire within one hour |

Session counters live in process memory. Daily counters are stored privately on the device and use UTC calendar days; neither is uploaded as custom telemetry. Count only successful SDK shows, not loading, requests, failed shows or eligibility attempts. App Open and Interstitial each consume their own cap and the shared full-screen cap. Configuration changes do not replenish the daily budget. Native appears only on Home and remains subject to its refresh, consent, Pro, lifecycle and global/per-format gates.

`load_retry_seconds` applies to every load attempt, including successful-ad reloads and Native refresh. Setting it to 300 can delay a Native refresh configured at 60 seconds; both intervals must pass before the next load.

Safe local example below is a **controls fragment**, not a complete payload. Start from `config_galaxy_v2.json`, retain all required identity, unit IDs and other fields, and merge changes into it. This fragment keeps every request disabled:

```json
{
  "kill_switches": {"ads_enabled": false, "iap_enabled": true},
  "ads": {
    "enabled": false,
    "test_ads_enabled": false,
    "production_ads_enabled": false,
    "load_retry_seconds": 30,
    "max_fullscreen_per_session": 5,
    "max_fullscreen_per_day": 8,
    "native": {"enabled": false},
    "app_open": {
      "enabled": false,
      "max_per_session": 2,
      "max_per_day": 4,
      "minimum_session_seconds": 300,
      "allowed_screens": ["home", "history", "favorites"]
    },
    "interstitial": {
      "enabled": false,
      "max_per_session": 3,
      "max_per_day": 6,
      "minimum_session_seconds": 120
    }
  }
}
```

## Editing, tests and rollback

Increase the revision for meaningful changes. Each endpoint has its own schema and must retain the exact package, store, App ID and demo IDs. Run:

```sh
python3 validate.py
python3 -m unittest -v test_validate.py
```

The validator checks all four configurations, strict types, bounded values, schema-2 required controls, supplied schema-1 controls, identity/IDs/links, duplicate JSON keys and response size. Regression tests protect the all-OFF legacy bridge and caps against unsafe or malformed changes. Inspect the complete Git diff before committing. CI runs both commands.

| Endpoint | All-OFF rollback template | Prepared revision |
| --- | --- | --- |
| `config_galaxy.json` / schema 1 | `config_galaxy_ads_disabled.json` | 5 |
| `config_galaxy_v2.json` / schema 2 | `rollback_ads_off_v2.json` | 6 |

To roll back, promote the matching template to its endpoint with a revision **higher than that endpoint's deployed revision**, validate, and publish. Preserve version/update/maintenance settings; do not force updates as part of an ad rollback. Set either global ad switch false to stop requests; set a format switch false to stop that placement. A fetched valid shutdown clears loaded/pending ads. Loaded ads also become invalid when the selected ID, mode or eligibility changes. Invalid JSON is not a dependable shutdown: an unexpired last-good config may remain active.

A local file or commit is not deployment evidence. After publishing, verify both exact raw endpoints and confirm the fetched revision/mode in the installed app. GitHub propagation can take several minutes; offline devices receive new switches after reconnecting.

## Cache, updates and privacy

The client fetches only its compiled HTTPS endpoint, rejects redirects, limits UTF-8 responses to 64 KiB and uses five-second network timeouts. Refresh runs at startup, foreground/manual refresh and every five minutes. Ad requests require fresh validated remote configuration or cache. Last-good cache lasts less than 24 hours. Missing, future-dated or expired cache disables ads while OCR stays available; lower revisions are rejected. The new endpoint does not reset freshness requirements.

`update_mode` remains `none`. Never force an update until that build is publicly available in the intended Galaxy regions. Links stay on this app's GitHub Pages site, support address and exact Samsung listing. Remote JSON neither downloads nor installs an APK. No custom ad/device identifier telemetry or purchase data is added by these controls; provider SDK processing is documented separately in the app's Privacy Policy.

Official demo-unit reference: [Google Mobile Ads Next-Gen test ads](https://developers.google.com/admob/android/next-gen/test-ads).
