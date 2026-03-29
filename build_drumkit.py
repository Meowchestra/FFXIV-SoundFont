import json
import os

# Map GM key to (source_instrument, ffxiv_target_key)
drum_map = {
    # Community Matched Preset Mappings:
    35: ("bassdrum", 55),  # Kick Drum 2
    36: ("bassdrum", 57),  # Kick Drum 1
    41: ("bassdrum", 63),  # Low Tom 2
    43: ("bassdrum", 66),  # Low Tom 1
    45: ("bassdrum", 70),  # Mid Tom 2
    47: ("bassdrum", 73),  # Mid Tom 1
    48: ("bassdrum", 77),  # High Tom 2
    50: ("bassdrum", 80),  # High Tom 1
    38: ("snaredrum", 67), # Snare Drum 1
    40: ("snaredrum", 69), # Snare Drum 2
    49: ("cymbal", 71),    # Crash Cymbal
    52: ("cymbal", 69),    # Chinese Cymbal
    55: ("cymbal", 77),    # Splash Cymbal
    57: ("cymbal", 71),    # Crash Cymbal
    60: ("bongo", 70),     # High Bongo
    61: ("bongo", 67),     # Low Bongo

    # Remaining General MIDI Holes:
    37: ("snaredrum", 72), # Side Stick 
    39: ("snaredrum", 75), # Hand Clap 
    42: ("cymbal", 84),    # Closed Hi Hat 
    44: ("cymbal", 84),    # Pedal Hi-Hat
    46: ("cymbal", 78),    # Open Hi-Hat
    51: ("cymbal", 54),    # Ride Cymbal 1
    53: ("cymbal", 84),    # Ride Bell
    54: ("cymbal", 84),    # Tambourine
    56: ("bongo", 75),     # Cowbell
    58: ("snaredrum", 76), # Vibraslap (snare rims/buzz)
    59: ("cymbal", 60),    # Ride Cymbal 2
    62: ("bongo", 72),     # Mute Hi Conga
    63: ("bongo", 70),     # Open Hi Conga
    64: ("bongo", 67),     # Low Conga
    65: ("timpani", 72),   # High Timbale
    66: ("timpani", 67),   # Low Timbale
    67: ("bongo", 74),     # High Agogo
    68: ("bongo", 69),     # Low Agogo
    69: ("snaredrum", 80), # Cabasa 
    70: ("snaredrum", 80), # Maracas
    73: ("bongo", 76),     # Short Guiro
    74: ("bongo", 60),     # Long Guiro
    75: ("bongo", 75),     # Claves
    76: ("bongo", 77),     # Hi Wood Block
    77: ("bongo", 72),     # Low Wood Block
    80: ("cymbal", 84),    # Mute Triangle
    81: ("cymbal", 81),    # Open Triangle
}

def parse_keyrange(kr_str):
    if "-" in kr_str:
        low, high = kr_str.split("-")
        return int(low), int(high)
    return int(kr_str), int(kr_str)

def build_kit():
    # 1. Read existing instrument files globally
    source_instruments = {}
    instrument_files = ['bassdrum', 'snaredrum', 'bongo', 'timpani', 'cymbal']
    
    for instr in instrument_files:
        path = os.path.join("instruments", f"{instr}.json")
        if os.path.exists(path):
            with open(path, "r", encoding='utf-8') as f:
                source_instruments[instr] = json.load(f)

    # 2. Build the new standard kit instrument
    standard_kit_zones = [
        {
            "generators": {
                "keyRange": "35-81"
            }
        }
    ]
    
    for gm_key in range(35, 82):
        if gm_key in drum_map:
            instr_name, ffxiv_key = drum_map[gm_key]
            instr_data = source_instruments.get(instr_name)
            if not instr_data:
                continue
                
            # Scan zones to find which one naturally services ffxiv_key
            best_gens = None
            for z in instr_data.get("zones", []):
                gens = z.get("generators", {})
                if "sample" not in gens:
                    continue  # skip global zone
                    
                kr_str = gens.get("keyRange", "0-127")
                low, high = parse_keyrange(kr_str)
                if low <= ffxiv_key <= high:
                    best_gens = dict(gens)
                    break
            
            if best_gens:
                # We found the perfect sample zone. 
                # The mathematical shift:
                # We want Hitting GM_KEY to sound exactly like hitting FFXIV_KEY in the native instrument.
                # Shift = GM_KEY - new_Root
                # Desired Shift = FFXIV_KEY - original_Root
                # Therefore: new_Root = GM_KEY - FFXIV_KEY + original_Root
                
                original_root = best_gens.get("overridingRootKey", best_gens.get("pitch_keycenter", 60))
                new_root = gm_key - ffxiv_key + original_root
                
                best_gens["keyRange"] = f"{gm_key}-{gm_key}"
                best_gens["overridingRootKey"] = new_root
                best_gens["pitch_keycenter"] = new_root # Set both to ensure safety across SF2 engine parsers
                
                standard_kit_zones.append({
                    "generators": best_gens
                })

    # Save combinations back to standard_kit.json
    kit_instr = {
        "name": "standard_kit",
        "zones": standard_kit_zones
    }
    
    instr_path = os.path.join("instruments", "standard_kit.json")
    with open(instr_path, "w", encoding="utf-8") as f:
        json.dump(kit_instr, f, indent=2)
        
    print(f"Standard Drum Kit generated using community transposition with {len(standard_kit_zones)-1} mapped keys!")

if __name__ == "__main__":
    build_kit()
