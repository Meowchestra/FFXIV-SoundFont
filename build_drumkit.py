import json
import os

# Map GM key to (source_instrument, ffxiv_target_key)
drum_map = {
    # Community Matched Preset Mappings:
    35: ("Bass Drum", 55),  # Kick Drum 2
    36: ("Bass Drum", 57),  # Kick Drum 1
    41: ("Bass Drum", 63),  # Low Tom 2
    43: ("Bass Drum", 66),  # Low Tom 1
    45: ("Bass Drum", 70),  # Mid Tom 2
    47: ("Bass Drum", 73),  # Mid Tom 1
    48: ("Bass Drum", 77),  # High Tom 2
    50: ("Bass Drum", 80),  # High Tom 1
    38: ("Snare Drum", 67), # Snare Drum 1
    40: ("Snare Drum", 69), # Snare Drum 2
    49: ("Cymbal", 71),     # Crash Cymbal
    52: ("Cymbal", 69),     # Chinese Cymbal
    55: ("Cymbal", 77),     # Splash Cymbal
    57: ("Cymbal", 71),     # Crash Cymbal
    60: ("Bongo", 70),      # High Bongo
    61: ("Bongo", 67),      # Low Bongo

    # Remaining General MIDI Holes:
    37: ("Snare Drum", 72), # Side Stick 
    39: ("Snare Drum", 75), # Hand Clap 
    42: ("Cymbal", 84),     # Closed Hi Hat 
    44: ("Cymbal", 84),     # Pedal Hi-Hat
    46: ("Cymbal", 78),     # Open Hi-Hat
    51: ("Cymbal", 54),     # Ride Cymbal 1
    53: ("Cymbal", 84),     # Ride Bell
    54: ("Cymbal", 84),     # Tambourine
    56: ("Bongo", 75),      # Cowbell
    58: ("Snare Drum", 76), # Vibraslap (snare rims/buzz)
    59: ("Cymbal", 60),     # Ride Cymbal 2
    62: ("Bongo", 72),      # Mute Hi Conga
    63: ("Bongo", 70),      # Open Hi Conga
    64: ("Bongo", 67),      # Low Conga
    65: ("Timpani", 72),    # High Timbale
    66: ("Timpani", 67),    # Low Timbale
    67: ("Bongo", 74),      # High Agogo
    68: ("Bongo", 69),      # Low Agogo
    69: ("Snare Drum", 80), # Cabasa 
    70: ("Snare Drum", 80), # Maracas
    73: ("Bongo", 76),      # Short Guiro
    74: ("Bongo", 60),      # Long Guiro
    75: ("Bongo", 75),      # Claves
    76: ("Bongo", 77),      # Hi Wood Block
    77: ("Bongo", 72),      # Low Wood Block
    80: ("Cymbal", 84),     # Mute Triangle
    81: ("Cymbal", 81),     # Open Triangle
}

def parse_keyrange(kr_str):
    if "-" in kr_str:
        low, high = kr_str.split("-")
        return int(low), int(high)
    return int(kr_str), int(kr_str)

def build_kit():
    # Ensure output directory exists
    output_dir = os.path.join("custom", "instruments")
    os.makedirs(output_dir, exist_ok=True)

    # 1. Read existing instrument files globally
    source_instruments = {}
    instrument_files = ['Bass Drum', 'Snare Drum', 'Bongo', 'Timpani', 'Cymbal']
    
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
        "name": "Standard Kit",
        "zones": standard_kit_zones
    }
    
    instr_path = os.path.join("custom", "instruments", "Standard Kit.json")
    with open(instr_path, "w", encoding="utf-8") as f:
        json.dump(kit_instr, f, indent=2)
        
    print(f"Standard Drum Kit generated using community transposition with {len(standard_kit_zones)-1} mapped keys!")

if __name__ == "__main__":
    build_kit()
