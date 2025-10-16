# BalletBot: Outbreak Dominion

A real-time, persistent multiplayer zombie survival simulator for Bale messenger. Players must scavenge resources, build shelters, craft weapons, and survive against both zombies and other players in a post-apocalyptic world.

## Features

### Core Gameplay
- **Character Classes**: Scavenger, Mechanic, Soldier with unique bonuses
- **Persistent World**: Real-time game state with day/night cycles
- **Resource Management**: Scavenge, craft, and trade items
- **Combat System**: Player vs Player and Player vs Zombie combat
- **Building System**: Enter buildings, clear floors, face zombie encounters
- **Decision Windows**: Quick-time decisions during encounters

### Advanced Systems
- **Offline Modes**: Set ambush or scavenge mode while offline
- **Vehicle System**: Drive vehicles with condition and fuel management
- **Construction**: Build heavy structures like tanks and warships
- **Radio Communication**: Anonymous frequency-based chat
- **Intelligence System**: Use spotters to gather intel on other players
- **Crafting**: Create weapons, tools, and equipment from resources

### World Features
- **Multiple Regions**: Forest, Urban, Downtown, Military, Coast
- **Dynamic Zombie Spawning**: Based on danger levels and noise
- **Map System**: Purchase detailed maps of regions
- **Weather Effects**: Day/night cycles affect gameplay

## Installation

### Prerequisites
- Python 3.10 or higher
- Bale messenger account and bot token

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd balletbot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the bot**
   - Edit `config.py` to adjust game settings
   - Set `TIME_MULTIPLIER` for faster/slower gameplay during testing
   - Configure `DATABASE_PATH` if needed

4. **Set up Bale API**
   - Replace the mock implementation in `bale_api.py` with actual Bale API
   - Add your bot token to the BaleAPI initialization

5. **Initialize the database**
   ```bash
   python main.py
   ```
   The database will be created automatically on first run.

## Usage

### Starting the Bot

```bash
python main.py
```

### Admin Commands (Group Chat)
- `/start_season` - Start a new game season
- `/announce <message>` - Broadcast announcement
- `/pause_world` - Pause the world
- `/resume_world` - Resume the world
- `/reset_world` - Reset the world (with confirmation)

### Player Commands (Private Messages)
- `/join <game_code>` - Join a game
- `/create_character <name> <class>` - Create character
- `/status` - Show player status
- `/map [region] [detailed]` - View map (costs resources)
- `/move <location>` - Move to new location
- `/loot` - Loot current area
- `/enter <building>` - Enter a building
- `/floor <n> <action>` - Enter building floor
- `/sneak` - Attempt to sneak past zombies
- `/attack <target>` - Attack target
- `/craft <item>` - Craft an item
- `/build <structure>` - Build a structure
- `/setmode <mode>` - Set offline mode (ambush/scavenge/none)
- `/seek [area]` - Search for players/zombies
- `/radio <freq> <message>` - Send radio message
- `/setfreq <freq>` - Tune radio frequency
- `/intel buy_spotter` - Buy spotter device
- `/intel use_spotter <target>` - Use spotter on target
- `/mine` - Mine resources
- `/chop` - Chop wood
- `/vehicle <action> <vehicle_id>` - Vehicle commands

## Game Mechanics

### Character Classes

**Scavenger**
- +10% loot yield
- +10 stealth bonus
- Best for resource gathering

**Mechanic**
- +15% crafting speed
- +10 intelligence gain
- Best for equipment creation

**Soldier**
- +10% weapon damage
- +10 health bonus
- Best for combat

### Combat System

- **Initiative**: Based on speed, class, and random factors
- **Damage**: Weapon damage + class bonuses + random variation
- **Critical Hits**: 5% base chance
- **Armor**: Reduces incoming damage
- **Ammo Management**: Weapons consume ammunition

### Building System

- **Floor Encounters**: Face zombies when entering building floors
- **Decision Windows**: 7 seconds to choose sneak or attack
- **Difficulty Scaling**: Higher floors have stronger zombies
- **Loot Rewards**: Clear floors to get better loot

### Offline Modes

**Ambush Mode**
- Set trap while offline
- Get first strike bonus if enemy enters your area
- Double damage on first attack

**Scavenge Mode**
- Passively gather resources
- Success depends on region danger and base defense
- Reduced armor effectiveness if attacked

### Vehicle System

- **Condition Management**: Repair vehicles with repair kits
- **Fuel System**: Consume fuel for long-distance travel
- **Storage**: Vehicles provide additional inventory space
- **Types**: Bikes, Jeeps, Trucks, Tanks, Helicopters, Warships

## Configuration

### Time Settings
```python
TIME_MULTIPLIER = 1  # 1 = normal speed, 0.1 = 10x faster, 10 = 10x slower
DAY_LENGTH_SECONDS = 1800 * TIME_MULTIPLIER  # 30 minutes per day
WORLD_TICK_SECONDS = 30  # Zombie processing interval
```

### Map Costs
```python
MAP_FIRST_COST = {"wood": 10, "stone": 10}
MAP_DETAILED_COST = {"wood": 50, "stone": 25, "metal": 10}
```

### Combat Settings
```python
COMBAT_CRITICAL_HIT_CHANCE = 5  # Percentage
COMBAT_ALERTED_BONUS = 15  # Damage bonus when alerted
COMBAT_AMBUSH_BONUS = 100  # Double damage for ambush
```

## Testing

### Run Simulation
```bash
python tests/simulate.py
```

This creates test players and simulates game activity for testing purposes.

### Test Commands
The simulation script will:
- Create 5 test players with different classes
- Simulate movement, looting, crafting, and combat
- Run for 2 minutes with 10-second ticks
- Display summary statistics

## Database Schema

The bot uses SQLite with the following main tables:
- `players` - Player characters and stats
- `inventories` - Player item inventories
- `items` - Item definitions and properties
- `world_regions` - World regions and zombie counts
- `buildings` - Buildings and floor information
- `vehicles` - Vehicle data and condition
- `pending_actions` - Time-based action queue
- `construction` - Ongoing construction projects
- `events` - Game event log
- `logs` - System logs

## Development

### Project Structure
```
balletbot/
├── main.py                 # Main entry point
├── bale_api.py            # Bale API wrapper
├── config.py              # Configuration settings
├── requirements.txt       # Dependencies
├── README.md             # This file
├── core/                 # Core game systems
│   ├── game_loop.py      # Message processing
│   ├── world_manager.py  # World state management
│   ├── scheduler.py      # Game timing
│   └── events.py         # Event system
├── systems/              # Game systems
│   ├── player_system.py  # Player management
│   ├── inventory_system.py # Item management
│   ├── combat_system.py  # Combat mechanics
│   ├── zombie_system.py  # Zombie AI
│   ├── building_system.py # Building encounters
│   ├── crafting_system.py # Item crafting
│   ├── vehicle_system.py # Vehicle management
│   ├── radio_system.py   # Radio communication
│   ├── spotter_system.py # Intelligence gathering
│   ├── offline_system.py # Offline modes
│   └── construction_system.py # Heavy construction
├── utils/                # Utilities
│   ├── db.py            # Database helpers
│   ├── helpers.py       # Helper functions
│   └── logger.py        # Logging setup
├── data/                # Game data
│   ├── world.sqlite     # Database file
│   ├── items.json       # Item definitions
│   ├── recipes.json     # Crafting recipes
│   └── assets/          # Map images
└── tests/               # Testing
    └── simulate.py      # Simulation script
```

### Adding New Features

1. **New Commands**: Add to `core/game_loop.py`
2. **New Systems**: Create in `systems/` directory
3. **New Items**: Add to `data/items.json`
4. **New Recipes**: Add to `data/recipes.json`
5. **Database Changes**: Update schema in `utils/db.py`

### Logging

The bot uses structured logging with different levels:
- `INFO`: General game events
- `WARNING`: Non-critical issues
- `ERROR`: Errors that don't stop the bot
- `CRITICAL`: Fatal errors

Logs are written to both console and `logs/balletbot.log`.

## Troubleshooting

### Common Issues

1. **Database locked**: Make sure only one instance is running
2. **Import errors**: Check Python path and dependencies
3. **Bale API errors**: Verify bot token and API implementation
4. **Memory issues**: Reduce `TIME_MULTIPLIER` for testing

### Debug Mode

Set `LOG_LEVEL = "DEBUG"` in `config.py` for detailed logging.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs in `logs/balletbot.log`
3. Create an issue on the repository

---

**BalletBot: Outbreak Dominion** - Survive the apocalypse, one decision at a time.