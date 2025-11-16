# Breaking Changes

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
