# Home Assistant Dad Jokes Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![GitHub release](https://img.shields.io/github/release/loryanstrant/ha-jokes.svg)](https://github.com/loryanstrant/ha-jokes/releases)

A custom Home Assistant integration that fetches random dad jokes from [icanhazdadjoke.com](https://icanhazdadjoke.com/) and provides them as a sensor entity.

## Features

- 🎭 Fetches random dad jokes from the icanhazdadjoke.com API
- 📊 Creates a sensor entity with state "OK" when successful
- 🏷️ Stores joke text and ID as attributes (no 255 character state limitation)
- ⏰ Configurable refresh interval (1-1440 minutes, default: 5 minutes)
- ⚙️ Easy configuration through Home Assistant UI
- 🔄 Supports options flow for changing settings
- 🛡️ Robust error handling and logging
- 📱 HACS compliant for easy installation

## Installation

### HACS (Recommended)

1. Open HACS in your Home Assistant instance
2. Go to "Integrations"
3. Click the three dots menu and select "Custom repositories"
4. Add `https://github.com/loryanstrant/ha-jokes` as repository
5. Set category to "Integration"
6. Click "Add"
7. Find "Dad Jokes" in the integration list and install it
8. Restart Home Assistant
9. Go to Configuration > Integrations
10. Click "+ Add Integration" and search for "Dad Jokes"

### Manual Installation

1. Download the latest release from the [releases page](https://github.com/loryanstrant/ha-jokes/releases)
2. Extract the contents
3. Copy the `custom_components/ha_jokes` folder to your Home Assistant `custom_components` directory
4. Restart Home Assistant
5. Go to Configuration > Integrations
6. Click "+ Add Integration" and search for "Dad Jokes"

## Configuration

### Initial Setup

1. Go to **Configuration** → **Integrations**
2. Click **"+ Add Integration"**
3. Search for **"Dad Jokes"**
4. Set your desired refresh interval (1-1440 minutes, default: 5)
5. Click **"Submit"**

### Changing Options

1. Go to **Configuration** → **Integrations**
2. Find the **Dad Jokes** integration
3. Click **"Configure"**
4. Adjust the refresh interval as needed
5. Click **"Submit"**

## Usage

After installation, the integration creates a sensor entity:

- **Entity ID**: `sensor.dad_joke`
- **State**: "OK" when successful, "Error" when failed
- **Icon**: 🙂 (mdi:emoticon-happy-outline)

### Attributes

The sensor provides the following attributes:

- `joke`: The complete joke text
- `joke_id`: Unique identifier for the joke
- `last_updated`: Timestamp of the last successful update
- `refresh_interval`: Current refresh interval in minutes

### Example Usage in Lovelace

#### Simple Entity Card
```yaml
type: entity
entity: sensor.dad_joke
attribute: joke
name: "Dad Joke of the Moment"
```

#### Markdown Card
```yaml
type: markdown
content: |
  ## 😄 Dad Joke
  {{ state_attr('sensor.dad_joke', 'joke') }}
  
  *Last updated: {{ state_attr('sensor.dad_joke', 'last_updated') }}*
```

#### Custom Card with Conditional Display
```yaml
type: conditional
conditions:
  - entity: sensor.dad_joke
    state: "OK"
card:
  type: markdown
  content: |
    ## 🎭 Today's Dad Joke
    {{ state_attr('sensor.dad_joke', 'joke') }}
    
    **Joke ID**: {{ state_attr('sensor.dad_joke', 'joke_id') }}
    **Updated**: {{ state_attr('sensor.dad_joke', 'last_updated') }}
```

### Automations

You can use the sensor in automations:

```yaml
automation:
  - alias: "Announce Dad Joke"
    trigger:
      - platform: state
        entity_id: sensor.dad_joke
        attribute: joke
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "New Dad Joke!"
          message: "{{ state_attr('sensor.dad_joke', 'joke') }}"
```

## API Information

This integration uses the [icanhazdadjoke.com](https://icanhazdadjoke.com/) API, which:

- Provides free access to dad jokes
- Returns jokes in JSON format
- Includes unique IDs for each joke
- Has reasonable rate limits
- Requires no API key

## Troubleshooting

### Common Issues

1. **Sensor shows "Error" state**
   - Check your internet connection
   - Verify that icanhazdadjoke.com is accessible
   - Check Home Assistant logs for detailed error messages

2. **Integration not appearing**
   - Ensure you've restarted Home Assistant after installation
   - Check that the `custom_components/ha_jokes` folder is in the correct location
   - Verify all required files are present

3. **Jokes not updating**
   - Check the refresh interval setting
   - Verify the sensor state is "OK"
   - Check logs for any error messages

### Logs

To enable debug logging for this integration, add the following to your `configuration.yaml`:

```yaml
logger:
  logs:
    custom_components.ha_jokes: debug
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- [Issues](https://github.com/loryanstrant/ha-jokes/issues)
- [Home Assistant Community Forum](https://community.home-assistant.io/)

## Credits

- Dad jokes provided by [icanhazdadjoke.com](https://icanhazdadjoke.com/)
- Integration developed for the Home Assistant community
