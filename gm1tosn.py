import mido
import time
import argparse
import os
from glob import glob
from pathlib import Path

# --- Bank Constants ---
GM2_MSB = 121      # GM2 Bank MSB for melodic instruments
GM2_DRUM_MSB = 120 # GM2 Bank MSB for drums
GM2_LSB = 0        # GM2 Bank LSB

# --- Integra-7 Supernatural Mapping (Complete) ---
SUPERNATURAL_MAP = {
    # Piano (0-7)
    0: (1, "SN-A.Piano"),    # Acoustic Grand Piano -> Concert Piano (Program 1)
    1: (2, "SN-A.Piano"),    # Bright Acoustic Piano -> Grand Piano 1 (Program 2)
    2: (2, "GM2"),           # Electric Grand Piano -> GM2 Electric Grand Piano (no good SN equivalent)
    3: (4, "SN-A.Piano"),    # Honky-tonk Piano -> Grand Piano 3 (Program 4)
    4: (4, "GM2"),           # Electric Piano 1 -> GM2 Electric Piano 1 (no good SN equivalent)
    5: (5, "GM2"),           # Electric Piano 2 -> GM2 Electric Piano 2 (no good SN equivalent)
    6: (6, "GM2"),           # Harpsichord -> GM2 Harpsichord (no good SN equivalent)
    7: (7, "GM2"),           # Clavi -> GM2 Clavi (no good SN equivalent)
    
    # Chromatic Percussion (8-15)
    8: (8, "GM2"),           # Celesta -> GM2 Celesta (no good SN equivalent)
    9: (9, "GM2"),           # Glockenspiel -> GM2 Glockenspiel (no good SN equivalent)
    10: (10, "GM2"),         # Music Box -> GM2 Music Box (no good SN equivalent)
    11: (11, "GM2"),         # Vibraphone -> GM2 Vibraphone (no good SN equivalent)
    12: (12, "GM2"),         # Marimba -> GM2 Marimba (no good SN equivalent)
    13: (13, "GM2"),         # Xylophone -> GM2 Xylophone (no good SN equivalent)
    14: (14, "GM2"),         # Tubular Bells -> GM2 Tubular Bells (no good SN equivalent)
    15: (15, "GM2"),         # Dulcimer -> GM2 Dulcimer (no good SN equivalent)
    
    # Organ (16-23)
    16: (16, "GM2"),         # Drawbar Organ -> GM2 Drawbar Organ (no good SN equivalent)
    17: (17, "GM2"),         # Percussive Organ -> GM2 Percussive Organ (no good SN equivalent)
    18: (18, "GM2"),         # Rock Organ -> GM2 Rock Organ (no good SN equivalent)
    19: (19, "GM2"),         # Church Organ -> GM2 Church Organ (no good SN equivalent)
    20: (20, "GM2"),         # Reed Organ -> GM2 Reed Organ (no good SN equivalent)
    21: (21, "GM2"),         # Accordion -> GM2 Accordion (no good SN equivalent)
    22: (22, "GM2"),         # Harmonica -> GM2 Harmonica (no good SN equivalent)
    23: (23, "GM2"),         # Tango Accordion -> GM2 Tango Accordion (no good SN equivalent)

    # Guitar (24-31)
    24: (1, "SN-NylonGtr"),   # Nylon String Guitar -> Classical Guitar (Program 1)
    25: (2, "SN-SteelGtr"),   # Steel String Guitar -> Folk Guitar (Program 2)
    26: (26, "GM2"),          # Electric Jazz Guitar -> GM2 Jazz Guitar (no good SN equivalent)
    27: (27, "GM2"),          # Electric Clean Guitar -> GM2 Clean Guitar (no good SN equivalent)
    28: (28, "GM2"),          # Electric Muted Guitar -> GM2 Muted Guitar (no good SN equivalent)
    29: (29, "GM2"),          # Overdriven Guitar -> GM2 Overdriven Guitar (no good SN equivalent)
    30: (30, "GM2"),          # Distortion Guitar -> GM2 Distortion Guitar (no good SN equivalent)
    31: (31, "GM2"),          # Guitar Harmonics -> GM2 Guitar Harmonics (no good SN equivalent)

    # Bass (32-39)
    32: (1, "SN-A.Bass"),     # Acoustic Bass -> Acoustic Bass (Program 1)
    33: (33, "GM2"),          # Electric Finger Bass -> GM2 Finger Bass (no good SN equivalent)
    34: (34, "GM2"),          # Electric Pick Bass -> GM2 Pick Bass (no good SN equivalent)
    35: (35, "GM2"),          # Fretless Bass -> GM2 Fretless Bass (no good SN equivalent)
    36: (36, "GM2"),          # Slap Bass 1 -> GM2 Slap Bass 1 (no good SN equivalent)
    37: (37, "GM2"),          # Slap Bass 2 -> GM2 Slap Bass 2 (no good SN equivalent)
    38: (38, "GM2"),          # Synth Bass 1 -> GM2 Synth Bass 1 (no good SN equivalent)
    39: (39, "GM2"),          # Synth Bass 2 -> GM2 Synth Bass 2 (no good SN equivalent)

    # Strings (40-47)
    40: (1, "SN-Violin"),     # Violin -> Violin (Program 1)
    41: (2, "SN-Viola"),      # Viola -> Viola (Program 2)
    42: (3, "SN-Cello"),      # Cello -> Cello (Program 3)
    43: (4, "SN-Contrabass"), # Contrabass -> Contrabass (Program 4)
    44: (44, "GM2"),          # Tremolo Strings -> GM2 Tremolo Strings (no good SN equivalent)
    45: (45, "GM2"),          # Pizzicato Strings -> GM2 Pizzicato Strings (no good SN equivalent)
    46: (46, "GM2"),          # Orchestral Harp -> GM2 Orchestral Harp (no good SN equivalent)
    47: (47, "GM2"),          # Timpani -> GM2 Timpani (no good SN equivalent)

    # Ensemble (48-55)
    48: (48, "GM2"),          # String Ensemble 1 -> GM2 String Ensemble 1 (no good SN equivalent)
    49: (49, "GM2"),          # String Ensemble 2 -> GM2 String Ensemble 2 (no good SN equivalent)
    50: (50, "GM2"),          # Synth Strings 1 -> GM2 Synth Strings 1 (no good SN equivalent)
    51: (51, "GM2"),          # Synth Strings 2 -> GM2 Synth Strings 2 (no good SN equivalent)
    52: (52, "GM2"),          # Choir Aahs -> GM2 Choir Aahs (no good SN equivalent)
    53: (53, "GM2"),          # Voice Oohs -> GM2 Voice Oohs (no good SN equivalent)
    54: (54, "GM2"),          # Synth Voice -> GM2 Synth Voice (no good SN equivalent)
    55: (55, "GM2"),          # Orchestra Hit -> GM2 Orchestra Hit (no good SN equivalent)

    # Brass (56-63)
    56: (1, "SN-Trumpet"),    # Trumpet -> Trumpet (Program 1)
    57: (2, "SN-Trombone"),   # Trombone -> Trombone (Program 2)
    58: (3, "SN-Tuba"),       # Tuba -> Tuba (Program 3)
    59: (4, "SN-MutedTrumpet"), # Muted Trumpet -> Muted Trumpet (Program 4)
    60: (5, "SN-FrenchHorn"), # French Horn -> French Horn (Program 5)
    61: (61, "GM2"),          # Brass Section -> GM2 Brass Section (no good SN equivalent)
    62: (62, "GM2"),          # Synth Brass 1 -> GM2 Synth Brass 1 (no good SN equivalent)
    63: (63, "GM2"),          # Synth Brass 2 -> GM2 Synth Brass 2 (no good SN equivalent)

    # Reed (64-71)
    64: (1, "SN-SopranoSax"), # Soprano Sax -> Soprano Sax (Program 1)
    65: (2, "SN-AltoSax"),    # Alto Sax -> Alto Sax (Program 2)
    66: (3, "SN-TenorSax"),   # Tenor Sax -> Tenor Sax (Program 3)
    67: (4, "SN-BaritoneSax"), # Baritone Sax -> Baritone Sax (Program 4)
    68: (1, "SN-Oboe"),       # Oboe -> Oboe (Program 1)
    69: (2, "SN-EnglishHorn"), # English Horn -> English Horn (Program 2)
    70: (3, "SN-Bassoon"),    # Bassoon -> Bassoon (Program 3)
    71: (4, "SN-Clarinet"),   # Clarinet -> Clarinet (Program 4)

    # Pipe (72-79)
    72: (1, "SN-Piccolo"),    # Piccolo -> Piccolo (Program 1)
    73: (2, "SN-Flute"),      # Flute -> Flute (Program 2)
    74: (74, "GM2"),          # Recorder -> GM2 Recorder (no good SN equivalent)
    75: (75, "GM2"),          # Pan Flute -> GM2 Pan Flute (no good SN equivalent)
    76: (76, "GM2"),          # Blown Bottle -> GM2 Blown Bottle (no good SN equivalent)
    77: (77, "GM2"),          # Shakuhachi -> GM2 Shakuhachi (no good SN equivalent)
    78: (78, "GM2"),          # Whistle -> GM2 Whistle (no good SN equivalent)
    79: (79, "GM2"),          # Ocarina -> GM2 Ocarina (no good SN equivalent)

    # Synth Lead (80-87)
    80: (80, "GM2"),          # Square Lead -> GM2 Square Lead (no good SN equivalent)
    81: (81, "GM2"),          # Sawtooth Lead -> GM2 Sawtooth Lead (no good SN equivalent)
    82: (82, "GM2"),          # Calliope Lead -> GM2 Calliope Lead (no good SN equivalent)
    83: (83, "GM2"),          # Chiff Lead -> GM2 Chiff Lead (no good SN equivalent)
    84: (84, "GM2"),          # Charang Lead -> GM2 Charang Lead (no good SN equivalent)
    85: (85, "GM2"),          # Voice Lead -> GM2 Voice Lead (no good SN equivalent)
    86: (86, "GM2"),          # Fifths Lead -> GM2 Fifths Lead (no good SN equivalent)
    87: (87, "GM2"),          # Bass + Lead -> GM2 Bass + Lead (no good SN equivalent)

    # Synth Pad (88-95)
    88: (88, "GM2"),          # New Age Pad -> GM2 New Age Pad (no good SN equivalent)
    89: (89, "GM2"),          # Warm Pad -> GM2 Warm Pad (no good SN equivalent)
    90: (90, "GM2"),          # Polysynth Pad -> GM2 Polysynth Pad (no good SN equivalent)
    91: (91, "GM2"),          # Choir Pad -> GM2 Choir Pad (no good SN equivalent)
    92: (92, "GM2"),          # Bowed Pad -> GM2 Bowed Pad (no good SN equivalent)
    93: (93, "GM2"),          # Metallic Pad -> GM2 Metallic Pad (no good SN equivalent)
    94: (94, "GM2"),          # Halo Pad -> GM2 Halo Pad (no good SN equivalent)
    95: (95, "GM2"),          # Sweep Pad -> GM2 Sweep Pad (no good SN equivalent)

    # Synth Effects (96-103)
    96: (96, "GM2"),          # Rain -> GM2 Rain (no good SN equivalent)
    97: (97, "GM2"),          # Soundtrack -> GM2 Soundtrack (no good SN equivalent)
    98: (98, "GM2"),          # Crystal -> GM2 Crystal (no good SN equivalent)
    99: (99, "GM2"),          # Atmosphere -> GM2 Atmosphere (no good SN equivalent)
    100: (100, "GM2"),        # Brightness -> GM2 Brightness (no good SN equivalent)
    101: (101, "GM2"),        # Goblins -> GM2 Goblins (no good SN equivalent)
    102: (102, "GM2"),        # Echoes -> GM2 Echoes (no good SN equivalent)
    103: (103, "GM2"),        # Sci-Fi -> GM2 Sci-Fi (no good SN equivalent)

    # Ethnic (104-111)
    104: (104, "GM2"),        # Sitar -> GM2 Sitar (no good SN equivalent)
    105: (105, "GM2"),        # Banjo -> GM2 Banjo (no good SN equivalent)
    106: (106, "GM2"),        # Shamisen -> GM2 Shamisen (no good SN equivalent)
    107: (107, "GM2"),        # Koto -> GM2 Koto (no good SN equivalent)
    108: (108, "GM2"),        # Kalimba -> GM2 Kalimba (no good SN equivalent)
    109: (109, "GM2"),        # Bagpipe -> GM2 Bagpipe (no good SN equivalent)
    110: (110, "GM2"),        # Fiddle -> GM2 Fiddle (no good SN equivalent)
    111: (111, "GM2"),        # Shanai -> GM2 Shanai (no good SN equivalent)

    # Percussive (112-119)
    112: (112, "GM2"),        # Tinkle Bell -> GM2 Tinkle Bell (no good SN equivalent)
    113: (113, "GM2"),        # Agogo -> GM2 Agogo (no good SN equivalent)
    114: (114, "GM2"),        # Steel Drums -> GM2 Steel Drums (no good SN equivalent)
    115: (115, "GM2"),        # Woodblock -> GM2 Woodblock (no good SN equivalent)
    116: (116, "GM2"),        # Taiko Drum -> GM2 Taiko Drum (no good SN equivalent)
    117: (117, "GM2"),        # Melodic Tom -> GM2 Melodic Tom (no good SN equivalent)
    118: (118, "GM2"),        # Synth Drum -> GM2 Synth Drum (no good SN equivalent)
    119: (119, "GM2"),        # Reverse Cymbal -> GM2 Reverse Cymbal (no good SN equivalent)

    # Sound Effects (120-127)
    120: (120, "GM2"),        # Guitar Fret Noise -> GM2 Guitar Fret Noise (no good SN equivalent)
    121: (121, "GM2"),        # Breath Noise -> GM2 Breath Noise (no good SN equivalent)
    122: (122, "GM2"),        # Seashore -> GM2 Seashore (no good SN equivalent)
    123: (123, "GM2"),        # Bird Tweet -> GM2 Bird Tweet (no good SN equivalent)
    124: (124, "GM2"),        # Telephone Ring -> GM2 Telephone Ring (no good SN equivalent)
    125: (125, "GM2"),        # Helicopter -> GM2 Helicopter (no good SN equivalent)
    126: (126, "GM2"),        # Applause -> GM2 Applause (no good SN equivalent)
    127: (127, "GM2")         # Gunshot -> GM2 Gunshot (no good SN equivalent)
}

# Supernatural tone number mapping
SUPERNATURAL_TONE_MAP = {
    # Piano (1-32)
    "SN-A.Piano": 1,      # Concert Piano
    "SN-A.Piano2": 2,     # Grand Piano 1
    "SN-E.Grand": 3,      # Grand Piano 2
    "SN-Honky-tonk": 4,   # Grand Piano 3
    
    # E.Piano (1-32)
    "SN-E.Piano": 1,      # '74 Stage Piano
    "SN-E.Piano2": 2,     # '76 Stage Piano
    
    # Keyboards (1-32)
    "SN-Harpsichord": 1,  # Harpsichord 1
    "SN-Celesta": 2,      # Celesta
    "SN-Music Box": 3,    # Music Box
    "SN-Vibraphone": 4,   # Vibraphone
    "SN-Marimba": 5,      # Marimba
    "SN-Xylophone": 6,    # Xylophone
    "SN-TubularBells": 7, # Tubular Bells
    "SN-Dulcimer": 8,     # Dulcimer
    
    # Organ (1-32)
    "SN-DrawbarOrg": 1,   # Jazz Organ 1
    "SN-DrawbarOrg2": 2,  # Jazz Organ 2
    "SN-DrawbarOrg3": 3,  # Jazz Organ 3
    "SN-ChurchOrg1": 4,   # Church Organ 1
    "SN-ChurchOrg2": 5,   # Church Organ 2
    
    # Accordion (1-32)
    "SN-Accordion": 1,    # French Accordion
    "SN-Harmonica": 2,    # Harmonica
    "SN-Bandoneon": 3,    # Bandoneon
    
    # Guitar (1-32)
    "SN-NylonGtr": 1,     # Classical Guitar
    "SN-SteelGtr": 2,     # Steel Guitar
    "SN-Jazz Gtr": 3,     # Jazz Guitar
    "SN-Clean Gtr": 4,    # Clean Guitar
    "SN-MutedGtr": 5,     # Muted Guitar
    "SN-OverdriveGtr": 6, # Overdrive Guitar
    "SN-DistGtr": 7,      # Distortion Guitar
    "SN-Gt.Harmonics": 8, # Guitar Harmonics
    
    # Bass (1-32)
    "SN-A.Bass": 1,       # Acoustic Bass
    "SN-FingeredBs": 2,   # Fingered Bass
    "SN-PickedBs": 3,     # Picked Bass
    "SN-FretlessBs": 4,   # Fretless Bass
    "SN-SlapBass": 5,     # Slap Bass
    "SN-SlapBass2": 6,    # Slap Bass 2
    "SN-SynthBass": 7,    # Synth Bass
    "SN-SynthBass2": 8,   # Synth Bass 2
    
    # Strings (1-32)
    "SN-Violin": 1,       # Violin
    "SN-Viola": 2,        # Viola
    "SN-Cello": 3,        # Cello
    "SN-Contrabass": 4,   # Contrabass
    "SN-Strings": 5,      # String Ensemble
    "SN-Pizzicato": 6,    # Pizzicato
    "SN-Harp": 7,         # Concert Harp
    "SN-Timpani": 8,      # Timpani
    
    # Orchestra (1-32)
    "SN-Strings1": 1,     # Orchestra Strings 1
    "SN-Strings2": 2,     # Orchestra Strings 2
    "SN-SynthStrings": 3, # Warm Strings
    "SN-SynthStrings2": 4, # String Ensemble
    
    # Choir (1-32)
    "SN-ChoirAahs": 1,    # Mixed Choir
    "SN-VoiceOohs": 2,    # Gospel Choir
    "SN-SynthVox": 3,     # Jazz Scat
    "SN-OrchestraHit": 4, # Orchestra Hit
    
    # Brass (1-32)
    "SN-Trumpet": 1,      # Trumpet
    "SN-Trombone": 2,     # Trombone
    "SN-Tuba": 3,         # Tuba
    "SN-MutedTrumpet": 4, # Muted Trumpet
    "SN-FrenchHorn": 5,   # French Horn
    "SN-BrassSection": 6, # Brass Section
    "SN-SynthBrass": 7,   # Synth Brass 1
    "SN-SynthBrass2": 8,  # Synth Brass 2
    
    # Reed/Wind (1-32)
    "SN-SopranoSax": 1,   # Soprano Sax
    "SN-AltoSax": 2,      # Alto Sax
    "SN-TenorSax": 3,     # Tenor Sax
    "SN-BaritoneSax": 4,  # Baritone Sax
    "SN-Oboe": 5,         # Oboe
    "SN-EnglishHorn": 6,  # English Horn
    "SN-Bassoon": 7,      # Bassoon
    "SN-Clarinet": 8,     # Clarinet
    
    # Pipe (1-32)
    "SN-Piccolo": 1,      # Piccolo
    "SN-Flute": 2,        # Flute
    "SN-Recorder": 3,     # Recorder
    "SN-PanFlute": 4,     # Pan Flute
    "SN-Shakuhachi": 5,   # Shakuhachi
    "SN-Whistle": 6,      # Whistle
    "SN-Ocarina": 7,      # Ocarina
    
    # Ethnic (1-32)
    "SN-Sitar": 1,        # Sitar
    "SN-Banjo": 2,        # Banjo
    "SN-Shamisen": 3,     # Shamisen
    "SN-Koto": 4,         # Koto
    "SN-Kalimba": 5,      # Kalimba
    "SN-Bagpipe": 6,      # Bagpipe
    
    # Percussion (1-32)
    "SN-Agogo": 1,        # Agogo
    "SN-SteelDrums": 2,   # Steel Drums
    "SN-Woodblock": 3,    # Woodblock
    "SN-TaikoDrum": 4,    # Taiko
    "SN-MelodicTom": 5,   # Melodic Tom
    "SN-SynthDrum": 6,    # Synth Drum
    "SN-ReverseCymbal": 7, # Reverse Cymbal
    
    # Sound Effects (1-32)
    "SN-FretNoise": 1,    # Guitar Fret Noise
    "SN-BreathNoise": 2,  # Breath Noise
    "SN-Seashore": 3,     # Seashore
    "SN-BirdTweet": 4,    # Bird Tweet
    "SN-Telephone": 5,    # Telephone
    "SN-Helicopter": 6,   # Helicopter
    "SN-Applause": 7,     # Applause
    "SN-Gunshot": 8       # Gunshot
}

# --- Tone Categories ---
TONE_CATEGORY = {
    # Piano and Keys
    "SN-A.Piano": "PIANO",
    "SN-A.Piano2": "PIANO",
    "SN-E.Grand": "PIANO",
    "SN-Honky-tonk": "PIANO",
    "SN-E.Piano": "E.PIANO",
    "SN-E.Piano2": "E.PIANO",
    "SN-Harpsichord": "KEYBOARD",
    "SN-Clav": "KEYBOARD",
    "SN-Celesta": "KEYBOARD",
    "SN-Music Box": "KEYBOARD",
    "SN-Vibraphone": "KEYBOARD",
    "SN-Marimba": "KEYBOARD",
    "SN-Xylophone": "KEYBOARD",
    "SN-TubularBells": "KEYBOARD",
    "SN-Dulcimer": "KEYBOARD",
    
    # Organ
    "SN-DrawbarOrg": "ORGAN",
    "SN-DrawbarOrg2": "ORGAN",
    "SN-DrawbarOrg3": "ORGAN",
    "SN-ChurchOrg1": "ORGAN",
    "SN-ChurchOrg2": "ORGAN",
    "SN-Accordion": "ACCORDION",
    "SN-Harmonica": "ACCORDION",
    "SN-Bandoneon": "ACCORDION",
    
    # Guitar and Bass
    "SN-NylonGtr": "GUITAR",
    "SN-SteelGtr": "GUITAR",
    "SN-Jazz Gtr": "GUITAR",
    "SN-Clean Gtr": "GUITAR",
    "SN-MutedGtr": "GUITAR",
    "SN-OverdriveGtr": "GUITAR",
    "SN-DistGtr": "GUITAR",
    "SN-Gt.Harmonics": "GUITAR",
    "SN-A.Bass": "BASS",
    "SN-FingeredBs": "BASS",
    "SN-PickedBs": "BASS",
    "SN-FretlessBs": "BASS",
    "SN-SlapBass": "BASS",
    "SN-SlapBass2": "BASS",
    "SN-SynthBass": "BASS",
    "SN-SynthBass2": "BASS",
    
    # Strings and Orchestra
    "SN-Violin": "STRINGS",
    "SN-Viola": "STRINGS",
    "SN-Cello": "STRINGS",
    "SN-Contrabass": "STRINGS",
    "SN-Strings": "STRINGS",
    "SN-Pizzicato": "STRINGS",
    "SN-Harp": "STRINGS",
    "SN-Timpani": "STRINGS",
    "SN-Strings1": "ORCHESTRA",
    "SN-Strings2": "ORCHESTRA",
    "SN-SynthStrings": "ORCHESTRA",
    "SN-SynthStrings2": "ORCHESTRA",
    
    # Choir and Brass
    "SN-ChoirAahs": "CHOIR",
    "SN-VoiceOohs": "CHOIR",
    "SN-SynthVox": "CHOIR",
    "SN-OrchestraHit": "CHOIR",
    "SN-Trumpet": "BRASS",
    "SN-Trombone": "BRASS",
    "SN-Tuba": "BRASS",
    "SN-MutedTrumpet": "BRASS",
    "SN-FrenchHorn": "BRASS",
    "SN-BrassSection": "BRASS",
    "SN-SynthBrass": "BRASS",
    "SN-SynthBrass2": "BRASS",
    
    # Wind and Reed
    "SN-SopranoSax": "WIND",
    "SN-AltoSax": "WIND",
    "SN-TenorSax": "WIND",
    "SN-BaritoneSax": "WIND",
    "SN-Oboe": "WIND",
    "SN-EnglishHorn": "WIND",
    "SN-Bassoon": "WIND",
    "SN-Clarinet": "WIND",
    "SN-Piccolo": "WIND",
    "SN-Flute": "WIND",
    "SN-Recorder": "WIND",
    "SN-PanFlute": "WIND",
    "SN-Shakuhachi": "WIND",
    "SN-Whistle": "WIND",
    "SN-Ocarina": "WIND",
    
    # Ethnic and Percussion
    "SN-Sitar": "ETHNIC",
    "SN-Banjo": "ETHNIC",
    "SN-Shamisen": "ETHNIC",
    "SN-Koto": "ETHNIC",
    "SN-Kalimba": "ETHNIC",
    "SN-Bagpipe": "ETHNIC",
    "SN-Agogo": "PERCUSSION",
    "SN-SteelDrums": "PERCUSSION",
    "SN-Woodblock": "PERCUSSION",
    "SN-TaikoDrum": "PERCUSSION",
    "SN-MelodicTom": "PERCUSSION",
    "SN-SynthDrum": "PERCUSSION",
    "SN-ReverseCymbal": "PERCUSSION",
    
    # Sound Effects
    "SN-FretNoise": "SFX",
    "SN-BreathNoise": "SFX",
    "SN-Seashore": "SFX",
    "SN-BirdTweet": "SFX",
    "SN-Telephone": "SFX",
    "SN-Helicopter": "SFX",
    "SN-Applause": "SFX",
    "SN-Gunshot": "SFX",
    
    # Synth Lead and Pad
    "SN-SynthLead": "SYNTH_LEAD",
    "SN-SynthPad": "SYNTH_PAD",
    "SN-SynthFX": "SYNTH_FX"
}

# Bank select values for each category
BANK_MSB = {
    # SN-A (Acoustic) Banks - MSB 89
    "PIANO": 89,      # 0x59 SN-A Piano
    "E.PIANO": 89,    # 0x59 SN-A E.Piano
    "KEYBOARD": 89,   # 0x59 SN-A Keyboard
    "ORGAN": 89,      # 0x59 SN-A Organ
    "ACCORDION": 89,  # 0x59 SN-A Accordion
    "GUITAR": 89,     # 0x59 SN-A Guitar
    "BASS": 89,       # 0x59 SN-A Bass
    "STRINGS": 89,    # 0x59 SN-A Strings
    "ORCHESTRA": 89,  # 0x59 SN-A Orchestra
    "CHOIR": 89,      # 0x59 SN-A Choir
    "BRASS": 89,      # 0x59 SN-A Brass
    "WIND": 89,       # 0x59 SN-A Wind
    "ETHNIC": 89,     # 0x59 SN-A Ethnic
    
    # SN-S (Synth) Banks - MSB 95
    "SYNTH_LEAD": 95,  # 0x5F SN-S Lead
    "SYNTH_PAD": 95,   # 0x5F SN-S Pad
    "SYNTH_BRASS": 95, # 0x5F SN-S Brass
    "SYNTH_STRINGS": 95, # 0x5F SN-S Strings
    "SYNTH_BELL": 95,  # 0x5F SN-S Bell/Hit
    "SYNTH_FX": 95,    # 0x5F SN-S FX
    
    # SN-D (Drums) Banks - MSB 88
    "DRUMS": 88,       # 0x58 SN-D Drums
    "PERCUSSION": 88,  # 0x58 SN-D Percussion
    "SFX": 88         # 0x58 SN-D SFX
}

BANK_LSB = {
    # SN-A Banks (Preset SuperNATURAL Acoustic Tones)
    "PIANO": 64,      # Preset SN-A Piano Set
    "E.PIANO": 64,    # Preset SN-A E.Piano Set
    "KEYBOARD": 64,   # Preset SN-A Keyboard Set
    "ORGAN": 64,      # Preset SN-A Organ Set
    "ACCORDION": 64,  # Preset SN-A Accordion Set
    "GUITAR": 64,     # Preset SN-A Guitar Set
    "BASS": 64,       # Preset SN-A Bass Set
    "STRINGS": 64,    # Preset SN-A Strings Set
    "ORCHESTRA": 64,  # Preset SN-A Orchestra Set
    "CHOIR": 64,      # Preset SN-A Choir Set
    "BRASS": 64,      # Preset SN-A Brass Set
    "WIND": 64,       # Preset SN-A Wind Set
    "ETHNIC": 64,     # Preset SN-A Ethnic Set
    
    # SN-S Banks (Preset SuperNATURAL Synth Tones)
    "SYNTH_LEAD": 64,    # Preset SN-S Lead sounds
    "SYNTH_PAD": 64,     # Preset SN-S Pad sounds
    "SYNTH_BRASS": 64,   # Preset SN-S Brass sounds
    "SYNTH_STRINGS": 64, # Preset SN-S Strings
    "SYNTH_BELL": 64,    # Preset SN-S Bell/Hit sounds
    "SYNTH_FX": 64,      # Preset SN-S FX sounds
    
    # SN-D Banks (Preset SuperNATURAL Drum Kits)
    "DRUMS": 64,         # Preset SN-D Drum Kits
    "PERCUSSION": 64,    # Preset SN-D Percussion
    "SFX": 64           # Preset SN-D SFX
}

# --- Integra-7 Constants ---
MANUFACTURER_ID = 0x41  # Roland
DEVICE_ID = 0x10       # Default device ID
MODEL_ID = 0x6C        # Integra-7
COMMAND_DT1 = 0x12     # Data Set 1

# --- Studio Set Addresses ---
STUDIO_SET_MODE = 0x0F000402
STUDIO_SET_PART_BASE = 0x18000000
PART_OFFSET = 0x200

# --- Part Parameters Offsets ---
PART_SWITCH = 0x0000        # Part Switch
RECEIVE_CHANNEL = 0x0001    # MIDI Receive Channel
TONE_BANK_MSB = 0x0002     # Bank Select MSB
TONE_BANK_LSB = 0x0003     # Bank Select LSB
TONE_PC = 0x0004           # Program Number
TONE_BANK_TYPE = 0x0007    # Tone Bank Type (0: PCM Synth, 1: SN-A, 2: SN-S, 3: SN-D)

# --- Drum Kit Constants ---
SN_DRUM_MSB = 88  # MSB for SuperNATURAL Drum Kits
SN_DRUM_LSB = 64  # LSB for SuperNATURAL Drum Kits
DRUM_CHANNEL = 9  # MIDI channel 10 (0-based)

# Define which drum kits have good SuperNATURAL mappings
SN_DRUM_KITS = {
    0: "Standard Kit",      # Standard Kit
    8: "Room Kit",         # Room Kit
    16: "Power Kit",       # Power Kit
    24: "Electronic Kit",  # Electronic Kit
    25: "TR-808 Kit",     # TR-808 Kit
    32: "Jazz Kit",       # Jazz Kit
    40: "Brush Kit",      # Brush Kit
}

# GM2 Drum Kit Program Number Mapping
GM2_DRUM_MAP = {
    0: 0,    # Standard Kit
    1: 1,    # Standard Kit 2
    8: 8,    # Room Kit
    16: 16,  # Power Kit
    24: 24,  # Electronic Kit
    25: 25,  # TR-808 Kit
    32: 32,  # Jazz Kit
    40: 40,  # Brush Kit
    # Additional GM2 mappings
    2: 0,    # Standard Kit 2 -> Standard Kit
    3: 0,    # Standard Kit 3 -> Standard Kit
    4: 0,    # Standard Kit 4 -> Standard Kit
    5: 0,    # Standard Kit 5 -> Standard Kit
    6: 0,    # Standard Kit 6 -> Standard Kit
    7: 0,    # Standard Kit 7 -> Standard Kit
    9: 8,    # Room Kit 2 -> Room Kit
    10: 8,   # Room Kit 3 -> Room Kit
    11: 16,  # Room Kit 4 -> Power Kit
    17: 16,  # Power Kit 2 -> Power Kit
    18: 16,  # Power Kit 3 -> Power Kit
    19: 16,  # Power Kit 4 -> Power Kit
    26: 25,  # TR-808 Kit 2 -> TR-808 Kit
    27: 25,  # TR-808 Kit 3 -> TR-808 Kit
    28: 25,  # TR-808 Kit 4 -> TR-808 Kit
    33: 32,  # Jazz Kit 2 -> Jazz Kit
    34: 32,  # Jazz Kit 3 -> Jazz Kit
    35: 32,  # Jazz Kit 4 -> Jazz Kit
    41: 40,  # Brush Kit 2 -> Brush Kit
    42: 40,  # Brush Kit 3 -> Brush Kit
    43: 40,  # Brush Kit 4 -> Brush Kit
}

def create_sysex(address, data):
    """Creates a Roland SysEx message."""
    addr_msb = (address >> 16) & 0xFF
    addr_mid = (address >> 8) & 0xFF
    addr_lsb = address & 0xFF
    
    msg_data = [
        MANUFACTURER_ID,    # Roland
        DEVICE_ID,         # Device ID
        MODEL_ID,          # Integra-7
        COMMAND_DT1,       # Command
        addr_msb,          # Address MSB
        addr_mid,          # Address Middle
        addr_lsb,         # Address LSB
        *data             # Data
    ]
    
    # Calculate checksum (Roland method)
    checksum = 0
    for i in range(4, len(msg_data)):  # Start from address bytes
        checksum += msg_data[i]
    checksum = (128 - (checksum % 128)) % 128
    msg_data.append(checksum)
    
    return mido.Message('sysex', data=msg_data)

def initialize_part(track, part_num):
    """Initialize a part with basic settings."""
    # Reset All Controllers
    track.append(mido.Message('control_change', channel=part_num, control=121, value=0, time=0))
    
    # All Notes Off
    track.append(mido.Message('control_change', channel=part_num, control=123, value=0, time=0))
    
    # Small delay after initialization (only for non-drum channels)
    if part_num != DRUM_CHANNEL:
        track.append(mido.Message('note_on', note=0, velocity=0, time=10))

def set_bank_and_program(track, channel, msb, lsb, program):
    """Set bank and program numbers using MIDI CC messages."""
    if channel == DRUM_CHANNEL:
        print(f"\nWriting drum channel messages:")
    
    # Reset All Controllers
    track.append(mido.Message('control_change', channel=channel, control=121, value=0, time=0))
    if channel == DRUM_CHANNEL:
        print("  Reset All Controllers")
    
    # All Notes Off
    track.append(mido.Message('control_change', channel=channel, control=123, value=0, time=0))
    if channel == DRUM_CHANNEL:
        print("  All Notes Off")
    
    # Set the appropriate tone bank type via SysEx
    part_address = STUDIO_SET_PART_BASE + (channel * PART_OFFSET) + TONE_BANK_TYPE
    bank_type = None
    if msb == 89:  # SN-A
        track.append(create_sysex(part_address, [1]))  # Type 1 = SN-A
        bank_type = "SN-A"
        if channel == DRUM_CHANNEL:
            print("  SysEx Bank Type: SN-A (1)")
    elif msb == 88:  # SN-D
        track.append(create_sysex(part_address, [3]))  # Type 3 = SN-D
        bank_type = "SN-D"
        if channel == DRUM_CHANNEL:
            print("  SysEx Bank Type: SN-D (3)")
    elif msb == 95:  # SN-S
        track.append(create_sysex(part_address, [2]))  # Type 2 = SN-S
        bank_type = "SN-S"
        if channel == DRUM_CHANNEL:
            print("  SysEx Bank Type: SN-S (2)")
    elif msb == GM2_MSB:  # GM2
        track.append(create_sysex(part_address, [0]))  # Type 0 = PCM Synth
        bank_type = "GM2"
        if channel == DRUM_CHANNEL:
            print("  SysEx Bank Type: PCM Synth (0)")
    
    # Minimal delay after tone bank type change
    track.append(mido.Message('note_on', note=0, velocity=0, time=10))
    
    # Send Bank Select MSB (CC#0)
    track.append(mido.Message('control_change', channel=channel, control=0, value=msb, time=0))
    if channel == DRUM_CHANNEL:
        print(f"  Bank Select MSB: {msb}")
    
    # Send Bank Select LSB (CC#32)
    track.append(mido.Message('control_change', channel=channel, control=32, value=lsb, time=0))
    if channel == DRUM_CHANNEL:
        print(f"  Bank Select LSB: {lsb}")
    
    # Send Program Change
    track.append(mido.Message('program_change', channel=channel, program=program, time=0))
    if channel == DRUM_CHANNEL:
        print(f"  Program Change: {program}")
    
    # Minimal delay after program change
    track.append(mido.Message('note_on', note=0, velocity=0, time=10))
    
    print(f"Set Channel {channel}: Bank={bank_type}, MSB={msb}, LSB={lsb}, Program={program}")

def map_gm1_to_supernatural(input_midi_path, output_midi_path):
    """Maps a GM1 MIDI file to use Supernatural sounds."""
    print(f"Opening input MIDI file: {input_midi_path}")
    try:
        mid = mido.MidiFile(input_midi_path)
        print(f"Successfully opened MIDI file with {len(mid.tracks)} tracks")
        
        # Debug: Print all messages affecting channel 9 in input file
        print("\nAnalyzing input file for channel 9 messages:")
        for i, track in enumerate(mid.tracks):
            track_has_ch9 = False
            for msg in track:
                if hasattr(msg, 'channel') and msg.channel == DRUM_CHANNEL:
                    if not track_has_ch9:
                        print(f"\nTrack {i+1}:")
                        track_has_ch9 = True
                    if msg.type == 'program_change':
                        print(f"  Program Change to {msg.program}")
                    elif msg.type == 'control_change':
                        if msg.control == 0:
                            print(f"  Bank Select MSB: {msg.value}")
                        elif msg.control == 32:
                            print(f"  Bank Select LSB: {msg.value}")
                        elif msg.control == 121:
                            print(f"  Reset All Controllers")
                        elif msg.control == 123:
                            print(f"  All Notes Off")
                    elif msg.type == 'note_on' and msg.velocity > 0:
                        print(f"  First note: {msg.note}")
                        break
                elif msg.type == 'sysex':
                    # Check if it's a bank type change for channel 9
                    if len(msg.data) >= 7:
                        addr = (msg.data[4] << 16) | (msg.data[5] << 8) | msg.data[6]
                        part_addr = STUDIO_SET_PART_BASE + (DRUM_CHANNEL * PART_OFFSET) + TONE_BANK_TYPE
                        if addr == part_addr:
                            print(f"  SysEx Bank Type Change: {msg.data[7]}")
    except Exception as e:
        print(f"Error opening MIDI file: {e}")
        return

    output_mid = mido.MidiFile(ticks_per_beat=mid.ticks_per_beat)
    
    # Create initialization track
    init_track = mido.MidiTrack()
    output_mid.tracks.append(init_track)
    
    # Keep track of which channels have been assigned to which programs
    channel_program_map = {}
    
    # First initialize the drum channel to ensure it's set up correctly from the start
    print(f"Initializing drum channel {DRUM_CHANNEL}")
    initialize_part(init_track, DRUM_CHANNEL)
    
    # Set up drum channel with GM2 Standard Kit
    print(f"Setting up drum channel {DRUM_CHANNEL} with GM2 Standard Kit")
    # Set bank type to PCM Synth via SysEx
    part_address = STUDIO_SET_PART_BASE + (DRUM_CHANNEL * PART_OFFSET) + TONE_BANK_TYPE
    init_track.append(create_sysex(part_address, [0]))  # Type 0 = PCM Synth
    init_track.append(mido.Message('note_on', note=0, velocity=0, time=10))
    
    # Set to GM2 Standard Kit with correct MSB/LSB
    set_bank_and_program(init_track, DRUM_CHANNEL, GM2_DRUM_MSB, GM2_LSB, 0)  # Using GM2_DRUM_MSB (120) and GM2_LSB (0)
    channel_program_map[DRUM_CHANNEL] = (GM2_DRUM_MSB, GM2_LSB, 0)
    
    # Initialize all other parts
    for part in range(16):
        if part != DRUM_CHANNEL:  # Skip drum channel as it's already initialized
            print(f"Initializing part {part}")
            initialize_part(init_track, part)
    
    # Process each track
    for i, track in enumerate(mid.tracks):
        print(f"\nProcessing track {i+1}/{len(mid.tracks)}")
        output_track = mido.MidiTrack()
        output_mid.tracks.append(output_track)
        
        # Find the channel and program for this track
        track_channel = None
        track_program = None
        cumulative_time = 0
        
        for msg in track:
            if hasattr(msg, 'channel'):
                track_channel = msg.channel  # Get channel from first channel message
                if msg.type == 'program_change':
                    track_program = msg.program
                    break
            cumulative_time += msg.time
        
        # Reset position for actual processing
        if track_channel is not None and cumulative_time > 0:
            # Add the cumulative time to the first message to preserve timing
            output_track.append(mido.Message('note_on', note=0, velocity=0, time=cumulative_time))
        
        if track_channel is not None:
            # For drum channel, only set it up if it hasn't been initialized yet
            if track_channel == DRUM_CHANNEL:
                if track_program is not None and track_channel not in channel_program_map:
                    if track_program in SN_DRUM_KITS:
                        print(f"Setting drum channel {track_channel} to SN-D {SN_DRUM_KITS[track_program]} (Kit {track_program})")
                        set_bank_and_program(output_track, track_channel, SN_DRUM_MSB, SN_DRUM_LSB, track_program)
                        channel_program_map[track_channel] = (SN_DRUM_MSB, SN_DRUM_LSB, track_program)
                    else:
                        gm2_program = GM2_DRUM_MAP.get(track_program, 0)  # Default to Standard Kit if no mapping
                        print(f"Using GM2 Kit {gm2_program} for drum program {track_program}")
                        set_bank_and_program(output_track, track_channel, GM2_DRUM_MSB, GM2_LSB, gm2_program)
                        channel_program_map[track_channel] = (GM2_DRUM_MSB, GM2_LSB, gm2_program)
            # For non-drum channels, only process if we found a program change
            elif track_program is not None:
                if track_program in SUPERNATURAL_MAP:
                    program_num, tone_name = SUPERNATURAL_MAP[track_program]
                    
                    if tone_name == "GM2":
                        msb = GM2_MSB
                        lsb = GM2_LSB
                        program_num = track_program  # Use original program number for GM2
                    else:
                        category = TONE_CATEGORY[tone_name]
                        msb = BANK_MSB[category]
                        lsb = BANK_LSB[category]
                    
                    # Only update if different from current program
                    if (track_channel not in channel_program_map or 
                        channel_program_map[track_channel] != (msb, lsb, program_num)):
                        print(f"Setting channel {track_channel}: {tone_name} (Program {program_num})")
                        set_bank_and_program(output_track, track_channel, msb, lsb, program_num)
                        channel_program_map[track_channel] = (msb, lsb, program_num)
        
        # Process all messages in the track
        last_time = 0
        for msg in track:
            if hasattr(msg, 'channel'):
                # Skip bank select messages as we handle them with program changes
                if msg.type == 'control_change' and msg.control in [0, 32]:
                    last_time += msg.time
                    continue
                if msg.type == 'program_change':
                    # For drum channel, only handle program changes if they map to a different kit
                    if msg.channel == DRUM_CHANNEL:
                        # Get the target GM2 program number
                        target_program = msg.program if msg.program in SN_DRUM_KITS else GM2_DRUM_MAP.get(msg.program, 0)
                        current_program = channel_program_map.get(msg.channel, (None, None, None))[2]
                        
                        print(f"Drum program change request: Input={msg.program}, Maps to={target_program}, Current={current_program}")
                        
                        # Only update if the target program is different from current
                        if target_program != current_program:
                            # Add accumulated time before program change
                            if last_time > 0:
                                output_track.append(mido.Message('note_on', note=0, velocity=0, time=last_time))
                                last_time = 0
                                
                            if msg.program in SN_DRUM_KITS:
                                print(f"Mid-track drum change to SN-D {SN_DRUM_KITS[msg.program]} (Kit {msg.program})")
                                set_bank_and_program(output_track, msg.channel, SN_DRUM_MSB, SN_DRUM_LSB, msg.program)
                                channel_program_map[msg.channel] = (SN_DRUM_MSB, SN_DRUM_LSB, msg.program)
                            else:
                                print(f"Mid-track drum change to GM2 Kit {target_program}")
                                set_bank_and_program(output_track, msg.channel, GM2_DRUM_MSB, GM2_LSB, target_program)
                                channel_program_map[msg.channel] = (GM2_DRUM_MSB, GM2_LSB, target_program)
                        else:
                            print(f"Skipping drum program change - already using program {current_program}")
                            last_time += msg.time
                    elif msg.program in SUPERNATURAL_MAP:
                        program_num, tone_name = SUPERNATURAL_MAP[msg.program]
                        
                        if tone_name == "GM2":
                            msb = GM2_MSB
                            lsb = GM2_LSB
                            program_num = msg.program
                        else:
                            category = TONE_CATEGORY[tone_name]
                            msb = BANK_MSB[category]
                            lsb = BANK_LSB[category]
                        
                        # Only update if different from current program
                        if (msg.channel not in channel_program_map or 
                            channel_program_map[msg.channel] != (msb, lsb, program_num)):
                            # Add accumulated time before program change
                            if last_time > 0:
                                output_track.append(mido.Message('note_on', note=0, velocity=0, time=last_time))
                                last_time = 0
                                
                            print(f"Mid-track change to {tone_name} (Program {program_num})")
                            set_bank_and_program(output_track, msg.channel, msb, lsb, program_num)
                            channel_program_map[msg.channel] = (msb, lsb, program_num)
                        else:
                            last_time += msg.time
                    continue
                else:
                    # Copy all other channel messages (notes, controllers, etc.)
                    new_msg = msg.copy()
                    new_msg.time = last_time + msg.time
                    output_track.append(new_msg)
                    last_time = 0
            else:
                # Pass through non-channel messages (like meta messages)
                new_msg = msg.copy()
                new_msg.time = last_time + msg.time
                output_track.append(new_msg)
                last_time = 0
    
    print(f"\nSaving output MIDI file to: {output_midi_path}")
    try:
        output_mid.save(output_midi_path)
        print("Successfully saved mapped MIDI file")
    except Exception as e:
        print(f"Error saving MIDI file: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Convert GM1 MIDI file to use Integra-7 Supernatural sounds')
    parser.add_argument('input_files', nargs='+', help='Input MIDI file(s) or pattern(s)')
    
    args = parser.parse_args()
    
    # Process each argument which could be a pattern or a file
    input_files = []
    for pattern in args.input_files:
        # Try to expand as a pattern first
        matched_files = glob(pattern)
        if matched_files:
            input_files.extend(matched_files)
        else:
            # If not a pattern, treat as a direct file path
            input_files.append(pattern)
    
    if not input_files:
        print("No input files specified")
        exit(1)
    
    print(f"\nFound {len(input_files)} file(s) to process")
    
    # Process each file
    for input_file in input_files:
        # Generate output filename by prepending "SN" to the input filename
        input_dir = os.path.dirname(input_file)
        input_basename = os.path.basename(input_file)
        output_basename = "SN" + input_basename
        output_file = os.path.join(input_dir, output_basename)
        
        print(f"\nProcessing file {input_files.index(input_file) + 1}/{len(input_files)}...")
        print(f"Input file: {input_file}")
        print(f"Output file: {output_file}")
        map_gm1_to_supernatural(input_file, output_file)
