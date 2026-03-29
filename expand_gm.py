import os
import glob
import json

# Format: FFXIV Preset -> [(Target GM, Target Name), ...]
logical_mappings = {
    # Pianos -> Expand across all 6 main acoustic/electric piano types
    0: [
        (1, "Bright Acoustic Piano"),
        (2, "Electric Grand Piano"),
        (3, "Honky-tonk Piano"),
        (4, "Electric Piano 1"),
        (5, "Electric Piano 2")
    ],
    # Harpsichord/Clavinet/Bells are plucked/struck, Harp makes a beautiful acoustic substitute
    46: [
        (6, "Harpsichord"),
        (7, "Clavinet"),
        (8, "Celesta"),
        (9, "Glockenspiel"),
        (10, "Music Box"),
        (15, "Dulcimer")
    ],
    # Guitars
    25: [ # Lute (Nylon) to Steel Acoustic
        (24, "Acoustic Guitar Nylon")
    ],
    27: [ # Clean Guitar to Jazz Guitar
        (26, "Electric Guitar Jazz")
    ],
    # Basses -> Doublebass is acoustic, but can reasonably cover electric basses musically
    43: [
        (32, "Acoustic Bass"),
        (33, "Electric Bass Finger"),
        (34, "Electric Bass Pick"),
        (35, "Fretless Bass")
    ],
    # Strings -> Violin natively covers string sections seamlessly
    40: [ 
        (44, "Tremolo Strings"),
        (48, "String Ensemble 1"),
        (49, "String Ensemble 2")
    ],
    # FFXIV Fiddle is pizzicato, so we leave it isolated exclusively at 45 (pizzicato).
    # We don't map GM 110 (Fiddle) to it because GM Fiddle is bowed. If Fiddle was needed, we'd map 110 to Violin (40).
    
    # Brass -> Trumpet covers Muted and Sections well
    56: [ 
        (59, "Muted Trumpet"),
        (61, "Brass Section")
    ],
    # Reeds -> Saxophone (Alto) covers the whole Sax family
    65: [ 
        (64, "Soprano Sax"),
        (66, "Tenor Sax"),
        (67, "Baritone Sax")
    ],
    68: [ # Oboe covers the double reeds
        (69, "English Horn"),
        (70, "Bassoon")
    ],
    # Pipes -> Fife (Piccolo) covers the small high whistles
    72: [ 
        (74, "Recorder"),
        (78, "Whistle")
    ],
    75: [ # Panpipes smoothly covers the breathy ethnic flutes
        (76, "Blown Bottle"),
        (77, "Shakuhachi"),
        (79, "Ocarina")
    ]
}

def expand():
    preset_files = glob.glob(os.path.join("presets", "*.json"))
    
    # Map of actual base preset numbers to their file path
    source_files = {}
    for p in preset_files:
        basename = os.path.basename(p)
        try:
            num = int(basename.split("-")[1].split("_")[0])
            source_files[num] = p
        except Exception:
            pass

    # Ensure output directory exists
    output_dir = os.path.join("custom", "presets")
    os.makedirs(output_dir, exist_ok=True)

    created_count = 0
    for src_num, expansions in logical_mappings.items():
        if src_num in source_files:
            src_path = source_files[src_num]
            with open(src_path, "r", encoding="utf-8") as f:
                src_data = json.load(f)
                
            for targ_num, targ_name in expansions:
                safe_name = targ_name
                
                targ_filename = f"000-{targ_num:03d}_{safe_name}.json"
                targ_path = os.path.join("custom", "presets", targ_filename)
                
                targ_data = json.loads(json.dumps(src_data)) # deepcopy
                targ_data["preset_number"] = targ_num
                targ_data["name"] = targ_name
                
                with open(targ_path, "w", encoding="utf-8") as f:
                    json.dump(targ_data, f, indent=2)
                    
                created_count += 1
                
    print(f"Successfully generated {created_count} truly logical GM expansions.")

if __name__ == '__main__':
    expand()
