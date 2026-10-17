# Breaking Changes

## Version 1.7.0

### Minimum Home Assistant version is now 2024.11.0

**Breaking Change**: This integration now requires Home Assistant **2024.11.0** or newer.
Previously `hacs.json` declared `2023.1.0`.

The JokeAPI language selector added in this release passes `config_entry=` to
`DataUpdateCoordinator`, which is the keyword Home Assistant expects integrations to
supply (newer cores log a deprecation warning when it is missing). That keyword does not
exist before **2024.11.0** — on an older core the integration fails to set up with a
`TypeError`.

#### What you need to do:

- **On Home Assistant 2024.11.0 or newer**: nothing. Update as usual.
- **On an older core**: update Home Assistant first, or stay on 1.6.0. HACS will no longer
  offer 1.7.0 to cores below the declared minimum.

#### Also in this release

- The `aiohttp>=3.8.0` requirement was removed from `manifest.json`. `aiohttp` ships with
  Home Assistant itself, so declaring it was both redundant and a hassfest error.
- **French and Portuguese are not offered in the JokeAPI language dropdown.** JokeAPI lists
  six joke languages, but this integration asks it for single-line jokes (`type=single`) and
  JokeAPI holds **no** single-line French or Portuguese jokes — every one of them is a
  two-part setup-and-punchline joke. Selecting either returned HTTP 400 on every call, which
  took `sensor.joke` permanently offline when JokeAPI was the only enabled provider. The
  dropdown now offers Czech, German, English and Spanish, which all return jokes. Supporting
  the other two means rendering two-part jokes; that is a feature change, not a fix, and is
  left for a later release. If an entry somehow holds a language code that is no longer
  offered, the integration now logs a warning and falls back to English rather than wedging.
- **Saving the options now clears the current joke explanation.** Options changes are applied
  by reloading the config entry, which recreates `sensor.joke_explanation` from scratch. Ask
  for a fresh explanation after changing settings. Previously the explanation survived, but
  only because the settings were not reliably applied at all.

## Version 1.2.0

### Sensor Entity ID Changed

**Breaking Change**: The sensor entity ID has been renamed from `sensor.dad_joke` to `sensor.joke`.

This change was made because the integration now fetches jokes from multiple sources beyond just "dad jokes" (including icanhazdadjoke.com, JokeAPI v2, and Official Joke API).

#### What you need to do:

1. **Update your automations, scripts, and dashboards** to use the new entity ID `sensor.joke` instead of `sensor.dad_joke`.

2. **Example updates needed:**
   - Old: `sensor.dad_joke`
   - New: `sensor.joke`

3. **Search your configuration for references:**
   - Check `automations.yaml`
   - Check Lovelace dashboards
   - Check scripts
   - Check template sensors

#### After updating the integration:

- The old entity `sensor.dad_joke` will no longer exist
- A new entity `sensor.joke` will be created
- All attributes remain the same: `joke`, `joke_id`, `source`, `last_updated`, `refresh_interval`
- The sensor will continue to work the same way, just with a new name

#### Why this change?

The integration name has been generalized from "Dad Jokes" to "Jokes" to better reflect that it now pulls from multiple joke sources, not just dad jokes from icanhazdadjoke.com. The sensor name has been updated to match this new scope.
