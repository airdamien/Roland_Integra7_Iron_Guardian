# MIDI GM1 to Integra-7 SuperNATURAL Converter

This tool converts General MIDI (GM1) MIDI files to use Roland Integra-7's SuperNATURAL sounds where available, falling back to GM2 sounds where there are no suitable SuperNATURAL equivalents.

## Features

- Converts GM1 instruments to SuperNATURAL sounds where available
- Maintains GM2 compatibility for instruments without SuperNATURAL equivalents
- Properly handles drum channels with GM2 drum kits
- Preserves all MIDI timing, expression, and controller data
- Supports batch processing of multiple files
- Handles files with spaces in names
- Maintains original mix volumes and expression

## Requirements

- Python 3.6 or higher
- `mido` library (`pip install mido`)
- Roland Integra-7 synthesizer

## Installation

1. Clone this repository or download the script
2. Install the required Python package:
```bash
pip install mido
```

## Usage

Basic usage:
```bash
python gm1tosn.py "input.mid"
```

Process multiple files:
```bash
python gm1tosn.py "file1.mid" "file2.mid" "file3.mid"
```

Using wildcards:
```bash
python gm1tosn.py "*.mid"
```

The script will create new files with "SN" prefixed to the original filename.

## Sound Mappings

### SuperNATURAL Acoustic (SN-A)
- Piano -> Concert Piano
- Strings -> Individual String Instruments
- Brass -> Individual Brass Instruments
- Guitar -> Classical and Steel String
- Bass -> Acoustic Bass
- Wind -> Individual Wind Instruments

### GM2 Fallbacks
- Electric Pianos
- Synth sounds
- Effect sounds
- Most percussion instruments

### Drum Kits
- Uses GM2 drum kits by default
- Automatically maps to appropriate SuperNATURAL drum kits when available

## Technical Details

### Bank Selection
- SN-A (Acoustic): MSB=89, LSB=64
- SN-S (Synth): MSB=95, LSB=64
- SN-D (Drums): MSB=88, LSB=64
- GM2: MSB=121, LSB=0
- GM2 Drums: MSB=120, LSB=0

### MIDI Channel Handling
- Channel 10 (9 in zero-based numbering) is always treated as drums
- All other channels can use any instrument
- Original channel assignments are preserved

### Controller Data
- Preserves all volume (CC#7) settings
- Maintains expression (CC#11) data
- Keeps pan (CC#10) positions
- Retains all other controller data except bank select messages

## Known Limitations

1. Some GM1 instruments don't have direct SuperNATURAL equivalents and fall back to GM2
2. Program changes within a track may cause brief interruptions due to bank changes
3. Some complex drum mappings may require manual adjustment

## Contributing

Feel free to submit issues and enhancement requests!

## License

MIT License - feel free to use this code in your own projects.

## Acknowledgments

- Roland Corporation for the Integra-7 MIDI implementation documentation
- The MIDI Association for the GM1/GM2 specifications 