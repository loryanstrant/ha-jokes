# Home Assistant Jokes Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![GitHub release](https://img.shields.io/github/release/loryanstrant/ha-jokes.svg)](https://github.com/loryanstrant/ha-jokes/releases)

A custom Home Assistant integration that fetches random jokes from multiple sources and provides them as a sensor entity.

<p align="center"><img width="256" height="256" alt="icon" src="https://github.com/user-attachments/assets/ec238fee-508a-4647-9071-d93bf83a9988" /></p>


## Features

- 🎭 Fetches random jokes from multiple joke APIs
- 🔀 Random provider selection for variety
- 🛡️ Fault tolerance - automatically tries alternative providers if one fails
- 📊 Creates a sensor entity with state "OK" when successful
- 🏷️ Stores joke text, ID, and source as attributes (no 255 character state limitation)
- ⏰ Configurable refresh interval (1-1440 minutes, default: 5 minutes)
- ⚙️ Easy configuration through Home Assistant UI
- 🔄 Supports options flow for changing settings
- 🛡️ Robust error handling and logging
- 📱 HACS compliant for easy installation

## Installation

### HACS (Recommended)

1. Open HACS in your Home Assistant instance
2. Find "Jokes" in the integration list and install it
3. Restart Home Assistant
4. Go to Configuration > Integrations
5. Click "+ Add Integration" and search for "Jokes"

Or open it directly from here:

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=loryanstrant&repository=ha-jokes&category=integration)


### Manual Installation

1. Download the latest release from the [releases page](https://github.com/loryanstrant/ha-jokes/releases)
2. Extract the contents
3. Copy the `custom_components/ha_jokes` folder to your Home Assistant `custom_components` directory
4. Restart Home Assistant
5. Go to Configuration > Integrations
6. Click "+ Add Integration" and search for "Jokes"

## Configuration

### Initial Setup

1. Go to **Settings** → **Devices & Services**
2. Click **"+ Add Integration"**
3. Search for **"Jokes"**
4. Set your desired refresh interval (1-1440 minutes, default: 5)
5. Click **"Submit"**

### Changing Options

1. Go to **Settings** → **Devices & Services**
2. Find the **Jokes** integration
3. Click **"Configure"**
4. Adjust the refresh interval as needed
5. Click **"Submit"**

## Usage

After installation, the integration creates a sensor entity:

- **Entity ID**: `sensor.joke`
- **State**: "OK" when successful, "Error" when failed
- **Icon**: 🙂 (mdi:emoticon-happy-outline)

### Attributes

The sensor provides the following attributes:

- `joke`: The complete joke text
- `joke_id`: Unique identifier for the joke
- `source`: The joke provider that supplied the joke
- `last_updated`: Timestamp of the last successful update
- `refresh_interval`: Current refresh interval in minutes

### Example Usage in Lovelace

#### Simple Entity Card
```yaml
type: entity
entity: sensor.joke
attribute: joke
name: "Joke of the Moment"
```

#### Markdown Card with last updated time
```yaml
type: markdown
content: |
  ## 😄 Joke
  {{ state_attr('sensor.joke', 'joke') }}
  
  *Last updated @ {{ as_datetime(state_attr('sensor.joke', 'last_updated')).strftime('%H:%M %d %b %Y') }}*
  *Source: {{ state_attr('sensor.joke', 'source') }}*
```
<img width="515" height="142" alt="image" src="https://github.com/user-attachments/assets/02296d98-f871-4a0f-93fe-df820ee80b16" />



#### Markdown Card with time since last update
```yaml
type: markdown
content: |
  ## 😄 Joke
  {{ state_attr('sensor.joke', 'joke') }}
  
  *Last updated: {{ relative_time(as_datetime(state_attr('sensor.joke', 'last_updated'))) }} ago*
  *Source: {{ state_attr('sensor.joke', 'source') }}*
```
<img width="518" height="147" alt="image" src="https://github.com/user-attachments/assets/076e83af-d8e4-43a6-bdd8-02635eb8f6cb" />


#### Custom Card with Conditional Display
```yaml
type: conditional
conditions:
  - entity: sensor.joke
    state: "OK"
card:
  type: markdown
  content: |
    ## 🎭 Today's Joke
    {{ state_attr('sensor.joke', 'joke') }}
    
    **Joke ID**: {{ state_attr('sensor.joke', 'joke_id') }}
    **Source**: {{ state_attr('sensor.joke', 'source') }}
    **Updated**: {{ state_attr('sensor.joke', 'last_updated') }}
```

#### Button Card Example (requires button-card from HACS)
```yaml
type: custom:button-card
entity: sensor.joke
name: Daily Joke
show_state: false
styles:
  card:
    - background-color: var(--primary-background-color)
    - padding: 20px
    - border-radius: 15px
  name:
    - font-size: 20px
    - font-weight: bold
    - color: var(--primary-text-color)
custom_fields:
  joke: |
    [[[
      return `<div style="font-size: 16px; line-height: 1.5; margin-top: 10px;">
        ${states['sensor.joke'].attributes.joke}
      </div>`
    ]]]
  source: |
    [[[
      return `<div style="font-size: 12px; color: var(--secondary-text-color); margin-top: 10px;">
        Source: ${states['sensor.joke'].attributes.source}
      </div>`
    ]]]
```

#### Entities Card
```yaml
type: entities
title: Joke
entities:
  - entity: sensor.joke
    type: attribute
    attribute: joke
    name: Current Joke
  - entity: sensor.joke
    type: attribute
    attribute: source
    name: Source
    icon: mdi:information-outline
  - entity: sensor.joke
    type: attribute
    attribute: last_updated
    name: Last Updated
    icon: mdi:clock-outline
```

### Automations

You can use the sensor in automations:

```yaml
automation:
  - alias: "Announce Joke"
    trigger:
      - platform: state
        entity_id: sensor.joke
        attribute: joke
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "New Joke!"
          message: "{{ state_attr('sensor.joke', 'joke') }}"
```

## API Information

This integration fetches jokes from three different sources, automatically selecting them in random order and providing fault tolerance if one source is unavailable:

### Joke Sources

1. **[icanhazdadjoke.com](https://icanhazdadjoke.com/)** - A curated collection of dad jokes
   - Provides free access to dad jokes
   - Returns jokes in JSON format with unique IDs
   - No API key required

2. **[JokeAPI v2](https://v2.jokeapi.dev/)** - A RESTful API serving jokes
   - Configured in safe mode (no explicit content)
   - Returns single-line jokes only
   - Free and open source
   - No API key required

3. **[Official Joke API](https://github.com/15Dkatz/official_joke_api)** - A simple joke API
   - Community-maintained joke collection
   - Returns setup/punchline format jokes
   - Free and open source
   - No API key required

The integration randomly selects which provider to use for each joke request. If a provider fails to respond, it automatically tries the next provider, ensuring you always get a joke as long as at least one service is available.

## Troubleshooting

### Common Issues

1. **Sensor shows "Error" state**
   - Check your internet connection
   - Verify that at least one joke API is accessible
   - Check Home Assistant logs for detailed error messages
   - The integration will automatically try alternative providers

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

## Development Approach

<img width="256" height="256" alt="Vibe Coding with GitHub Copilot 256x256" src="https://github.com/user-attachments/assets/c8360318-0c18-4152-be59-3f3dcf4964a1" />


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- [Issues](https://github.com/loryanstrant/ha-jokes/issues)
- [Home Assistant Community Forum](https://community.home-assistant.io/)

## Credits

- Jokes provided by:
  - [icanhazdadjoke.com](https://icanhazdadjoke.com/)
  - [JokeAPI v2](https://v2.jokeapi.dev/) by Sven Fehler
  - [Official Joke API](https://github.com/15Dkatz/official_joke_api) by David Katz
- Integration developed for the Home Assistant community
