import os
import glob
import json

# FFXIV preset to a list of (GM_Target_Number, GM_Target_Name)
exhaustive_mappings = {
    # Pianos -> Expand across acoustic/electric piano types, mallet percussion, organs, and metallic synth pads
    0: [
        (1, "Bright Acoustic Piano"),
        (2, "Electric Grand Piano"),
        (3, "Honky-tonk Piano"),
        (4, "Electric Piano 1"),
        (5, "Electric Piano 2"),
        (11, "Vibraphone"),
        (12, "Marimba"),
        (13, "Xylophone"),
        (14, "Tubular Bells"),
        (16, "Drawbar Organ"),
        (17, "Percussive Organ"),
        (18, "Rock Organ"),
        (19, "Church Organ"),
        (93, "Metallic Pad"),
        (97, "Soundtrack FX"),
        (114, "Steel Drums")
    ],
    # Harpsichord/Clavinet/Bells are plucked/struck, Harp makes a beautiful acoustic substitute
    46: [
        (6, "Harpsichord"),
        (7, "Clavinet"),
        (8, "Celesta"),
        (9, "Glockenspiel"),
        (10, "Music Box"),
        (15, "Dulcimer"),
        (88, "New Age Pad"),
        (94, "Halo Pad"),
        (107, "Koto"),
        (108, "Kalimba"),
        (112, "Tinkle Bell")
    ],
    # Guitars
    24: [ 
        (25, "Acoustic Guitar Steel"),
        (104, "Sitar"),
        (105, "Banjo"),
        (106, "Shamisen")
    ],
    27: [ 
        (26, "Electric Guitar Jazz")
    ],
    29: [
        (84, "Charang Lead")
    ],
    31: [
        (120, "Guitar Fret Noise")
    ],
    # Basses -> Doublebass is acoustic, but can reasonably cover electric & synth basses
    43: [
        (32, "Acoustic Bass"),
        (33, "Electric Bass Finger"),
        (34, "Electric Bass Pick"),
        (35, "Fretless Bass"),
        (36, "Slap Bass 1"),
        (37, "Slap Bass 2"),
        (38, "Synth Bass 1"),
        (39, "Synth Bass 2"),
        (87, "Bass and Lead")
    ],
    # Strings -> Violin perfectly handles the high leads and ensembles
    40: [ 
        (44, "Tremolo Strings"),
        (48, "String Ensemble 1"),
        (50, "SynthStrings 1"),
        (51, "SynthStrings 2"),
        (90, "Polysynth Pad")
    ],
    # Viola -> Low/mid string sections and warm synths
    41: [
        (49, "String Ensemble 2"),
        (89, "Warm Pad")
    ],
    # Cello -> Bowed synthetic pad substitute
    42: [
        (92, "Bowed Pad")
    ],
    # FFXIV Fiddle is natively Pizzicato, so we map GM 110 (Fiddle) to it just by nominal namesake.
    45: [
        (110, "Fiddle")
    ],
    # Timpani
    47: [
        (55, "Orchestra Hit")
    ],
    # Brass -> Trumpet covers Muted and Sections well
    56: [ 
        (59, "Muted Trumpet"),
        (61, "Brass Section"),
        (63, "SynthBrass 2")
    ],
    # Horn
    60: [
        (62, "SynthBrass 1"),
        (86, "Fifths Lead")
    ],
    # Reeds -> Saxophone (Alto) covers the whole Sax family + saw lead
    65: [ 
        (64, "Soprano Sax"),
        (66, "Tenor Sax"),
        (67, "Baritone Sax"),
        (81, "Sawtooth Lead")
    ],
    68: [ # Oboe covers the double reeds and ethnic shrills
        (69, "English Horn"),
        (70, "Bassoon"),
        (109, "Bagpipe"),
        (111, "Shanai")
    ],
    71: [
        (80, "Square Lead")
    ],
    # Pipes -> Fife (Piccolo) covers the small high whistles
    72: [ 
        (74, "Recorder"),
        (78, "Whistle")
    ],
    73: [ # Flute covers voices/choirs
        (52, "Choir Aahs"),
        (53, "Voice Oohs"),
        (85, "Voice Lead"),
        (91, "Choir Pad")
    ],
    75: [ # Panpipes handles free-blown air sounds and continuous accordions
        (20, "Reed Organ"),
        (21, "Accordion"),
        (22, "Harmonica"),
        (23, "Tango Accordion"),
        (76, "Blown Bottle"),
        (77, "Shakuhachi"),
        (79, "Ocarina"),
        (82, "Calliope Lead"),
        (83, "Chiff Lead"),
        (95, "Sweep Pad")
    ],
    # Percussion
    115: [
        (118, "Synth Drum")
    ],
    116: [
        (113, "Agogo")
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

    created_count = 0
    for src_num, expansions in exhaustive_mappings.items():
        if src_num in source_files:
            src_path = source_files[src_num]
            with open(src_path, "r", encoding="utf-8") as f:
                src_data = json.load(f)
                
            for targ_num, targ_name in expansions:
                safe_name = targ_name.lower().replace(" (", "_").replace(")", "").replace(" ", "_").replace("+", "and")
                
                targ_filename = f"000-{targ_num:03d}_{safe_name}.json"
                targ_path = os.path.join("presets", targ_filename)
                
                targ_data = json.loads(json.dumps(src_data)) # deepcopy
                targ_data["preset_number"] = targ_num
                targ_data["name"] = targ_name
                
                with open(targ_path, "w", encoding="utf-8") as f:
                    json.dump(targ_data, f, indent=2)
                    
                created_count += 1
                
    print(f"Successfully generated {created_count} exhaustive GM expansions.")

if __name__ == '__main__':
    expand()
