# Dad Jokes Integration

Bring some humor to your Home Assistant setup with random jokes from multiple sources!

## What it does

This integration fetches random jokes from three different joke APIs and makes them available as a sensor in Home Assistant. It randomly selects which provider to use and includes fault tolerance to automatically try alternative providers if one fails.

## Key Features

- 🎭 **Multiple Joke Sources**: Fetches from icanhazdadjoke.com, JokeAPI v2, and Official Joke API
- 🔀 **Random Selection**: Providers are randomly selected for variety
- 🛡️ **Fault Tolerance**: Automatically tries alternative providers if one fails
- 📊 **Sensor Entity**: Clean integration with Home Assistant's sensor platform
- 🏷️ **Rich Attributes**: Joke text, unique ID, source, and metadata stored as attributes
- ⏰ **Configurable Updates**: Set refresh interval from 1 minute to 24 hours
- ⚙️ **Easy Setup**: Simple configuration through the Home Assistant UI
- 🔄 **Options Flow**: Change settings without removing and re-adding the integration
- 🛡️ **Robust**: Handles network errors and API issues gracefully
- 📱 **HACS Ready**: Full HACS compliance for easy installation and updates

## Perfect for

- Adding humor to your dashboard
- Creating fun automations and notifications
- Entertaining family and guests
- Breaking the ice during home automation demos
- Adding personality to your smart home

## Technical Details

- **Entity**: `sensor.dad_joke` with state "OK" or "Error"
- **Attributes**: `joke`, `joke_id`, `source`, `last_updated`, `refresh_interval`
- **Icon**: 🙂 (mdi:emoticon-happy-outline)
- **Updates**: Configurable interval from 1-1440 minutes
- **APIs**: Uses icanhazdadjoke.com, JokeAPI v2 (safe mode), and Official Joke API (no API keys required)

Ready to add some humor to your smart home? Install now and let the laughs begin! 😄