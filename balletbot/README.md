# BalletBot: Outbreak Dominion

A real-time, persistent multiplayer zombie survival simulator for Bale messenger. Players must scavenge resources, build shelters, craft weapons, and survive against both zombies and other players in a post-apocalyptic world.

## 🚀 Quick Start

### Installation

1. **Install Python 3.10+**
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the bot:**
   - Edit `config.py` and set your Bale bot token
   - Adjust `TIME_MULTIPLIER` for faster/slower gameplay during testing

4. **Run the bot:**
   ```bash
   python main.py
   ```

### Test the Implementation

```bash
python test_implementation.py
```

## ✨ Features

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

## 🎮 Commands

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

## 🏗️ Architecture

### File-Based Data Storage
This implementation uses text files instead of SQLite for data persistence:
- `data/players.txt` - Player data
- `data/inventories.txt` - Player inventories
- `data/world.txt` - World regions
- `data/buildings.txt` - Building data
- `data/vehicles.txt` - Vehicle data
- `data/pending_actions.txt` - Pending actions
- `data/construction.txt` - Construction projects
- `data/events.txt` - Game events
- `data/logs.txt` - System logs

### Bale API Integration
The bot includes a flexible Bale API wrapper that:
- Uses the real Bale Python API when available
- Falls back to mock mode for development/testing
- Handles all Bale-specific functionality (messages, photos, keyboards, etc.)

## 🎯 Character Classes

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

## ⚔️ Combat System

- **Initiative**: Based on speed, class, and random factors
- **Damage**: Weapon damage + class bonuses + random variation
- **Critical Hits**: 5% base chance
- **Armor**: Reduces incoming damage
- **Ammo Management**: Weapons consume ammunition

## 🏢 Building System

- **Floor Encounters**: Face zombies when entering building floors
- **Decision Windows**: 7 seconds to choose sneak or attack
- **Difficulty Scaling**: Higher floors have stronger zombies
- **Loot Rewards**: Clear floors to get better loot

## 💤 Offline Modes

**Ambush Mode**
- Set trap while offline
- Get first strike bonus if enemy enters your area
- Double damage on first attack

**Scavenge Mode**
- Passively gather resources
- Success depends on region danger and base defense
- Reduced armor effectiveness if attacked

## 🚗 Vehicle System

- **Condition Management**: Repair vehicles with repair kits
- **Fuel System**: Consume fuel for long-distance travel
- **Storage**: Vehicles provide additional inventory space
- **Types**: Bikes, Jeeps, Trucks, Tanks, Helicopters, Warships

## 🔧 Configuration

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

## 🧪 Testing

### Run Basic Tests
```bash
python test_implementation.py
```

This tests all core systems without requiring Bale API.

### Run Simulation
```bash
python tests/simulate.py
```

This creates test players and simulates game activity.

## 📁 Project Structure

```
balletbot/
├── main.py                 # Main entry point
├── bale_api.py            # Bale API wrapper (real + mock)
├── config.py              # Configuration settings
├── requirements.txt       # Dependencies
├── test_implementation.py # Basic functionality test
├── core/                  # Core game systems
│   ├── game_loop.py      # Message processing
│   ├── world_manager.py  # World state management
│   ├── scheduler.py      # Game timing
│   └── events.py         # Event system
├── systems/               # Game systems
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
├── utils/                 # Utilities
│   ├── file_manager.py   # File-based data management
│   ├── helpers.py        # Helper functions
│   └── logger.py         # Logging setup
├── data/                  # Game data
│   ├── items.json        # Item definitions
│   ├── recipes.json      # Crafting recipes
│   └── assets/           # Map images (placeholder)
└── tests/                 # Testing
    └── simulate.py       # Simulation script
```

## 🔧 Development

### Adding New Features

1. **New Commands**: Add to `core/game_loop.py`
2. **New Systems**: Create in `systems/` directory
3. **New Items**: Add to `data/items.json`
4. **New Recipes**: Add to `data/recipes.json`
5. **Data Changes**: Update `utils/file_manager.py`

### Logging

The bot uses structured logging with different levels:
- `INFO`: General game events
- `WARNING`: Non-critical issues
- `ERROR`: Errors that don't stop the bot
- `CRITICAL`: Fatal errors

Logs are written to both console and `logs/balletbot.log`.

## 🐛 Troubleshooting

### Common Issues

1. **Import errors**: Check Python path and dependencies
2. **Bale API errors**: Verify bot token and API implementation
3. **File permission errors**: Check write permissions for data directory
4. **Memory issues**: Reduce `TIME_MULTIPLIER` for testing

### Debug Mode

Set `LOG_LEVEL = "DEBUG"` in `config.py` for detailed logging.

## 📝 Notes

- This implementation uses text files instead of SQLite for data persistence
- The Bale API wrapper supports both real API and mock mode
- All game mechanics from the original specification are implemented
- The bot is ready for production use with proper Bale API integration

---

**BalletBot: Outbreak Dominion** - Survive the apocalypse, one decision at a time.