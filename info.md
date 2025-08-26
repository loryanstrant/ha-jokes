# Dad Jokes Integration

Bring some humor to your Home Assistant setup with random dad jokes!

## What it does

This integration fetches random dad jokes from the popular [icanhazdadjoke.com](https://icanhazdadjoke.com/) API and makes them available as a sensor in Home Assistant.

## Key Features

- 🎭 **Random Dad Jokes**: Fresh jokes fetched from a curated collection
- 📊 **Sensor Entity**: Clean integration with Home Assistant's sensor platform
- 🏷️ **Rich Attributes**: Joke text, unique ID, and metadata stored as attributes
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
- **Attributes**: `joke`, `joke_id`, `last_updated`, `refresh_interval`
- **Icon**: 🙂 (mdi:emoticon-happy-outline)
- **Updates**: Configurable interval from 1-1440 minutes
- **API**: Uses icanhazdadjoke.com (no API key required)

Ready to add some dad-level humor to your smart home? Install now and let the groans begin! 😄