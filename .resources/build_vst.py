import os
import json
import shutil
import subprocess
import tempfile
import sys
import re

# --- Configuration ---
# Folders to scan for presets (.json files)
PRESETS_SEARCH_PATHS = [
    "presets"
]

# Folders to scan for instruments (.json files)
INSTRUMENTS_SEARCH_PATHS = [
    "instruments"
]

# Folder containing all audio samples (.json or .wav)
SAMPLES_DIR = "samples"

# Where to save the individual VST SoundFonts
OUTPUT_DIR = os.path.join("build", "vst")

def sanitize_filename(filename):
    """Clean the filename to remove illegal characters like colons, brackets, etc."""
    # Convert to lowercase
    s = filename.lower()
    # Replace common problems
    s = s.replace(":", "").replace("-", "_").replace(" ", "_")
    # Remove anything else that isn't alphanumeric or underscore
    s = re.sub(r'[^a-z0-9_]', '', s)
    # Remove double underscores
    s = re.sub(r'_+', '_', s)
    return s.strip('_')

def find_file(filename, search_paths):
    """Search for a file in multiple directories."""
    for folder in search_paths:
        full_path = os.path.join(folder, filename)
        if os.path.exists(full_path):
            return full_path
    return None

def build_vst_individual():
    # Ensure output directory exists
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Created output directory: {OUTPUT_DIR}")

    # 1. Discover all presets
    preset_files = []
    for folder in PRESETS_SEARCH_PATHS:
        if not os.path.exists(folder):
            continue
        for f in os.listdir(folder):
            if f.endswith(".json"):
                preset_files.append(os.path.join(folder, f))

    if not preset_files:
        print("No presets found in common search paths.")
        return

    print(f"Found {len(preset_files)} presets. Starting standalone VST builds...")

    # 2. Process each preset
    for preset_path in preset_files:
        try:
            with open(preset_path, "r", encoding="utf-8") as f:
                preset_data = json.load(f)
            
            # Extract names
            # If name is "Electric Guitar: Clean", filename will be "vst_electric_guitar_clean.sf2"
            raw_name = preset_data.get("name", os.path.splitext(os.path.basename(preset_path))[0])
            safe_name = sanitize_filename(raw_name)

            # 3. Identify required instruments
            required_instruments = set()
            for zone in preset_data.get("zones", []):
                instr_name = zone.get("generators", {}).get("instrument")
                if instr_name:
                    required_instruments.add(instr_name)
            for BUILD_TYPE in ["corrected", "uncorrected"]:
                suffix = "" if BUILD_TYPE == "corrected" else "_uncorrected"
                vst_filename = f"vst_{safe_name}{suffix}.sf2"
                output_sf2_path = os.path.join(OUTPUT_DIR, vst_filename)

                print(f">>> Building: {vst_filename}")

                # 4. Create isolated temporary build environment
                with tempfile.TemporaryDirectory() as tmp_dir:
                    tmp_presets_dir = os.path.join(tmp_dir, "presets")
                    tmp_instruments_dir = os.path.join(tmp_dir, "instruments")
                    tmp_samples_dir = os.path.join(tmp_dir, "samples")

                    os.makedirs(tmp_presets_dir)
                    os.makedirs(tmp_instruments_dir)
                    os.makedirs(tmp_samples_dir)
                    
                    # Copy info.json (essential for sfutils metadata)
                    if os.path.exists("info.json"):
                        shutil.copy("info.json", os.path.join(tmp_dir, "info.json"))

                    # Copy the specific preset
                    shutil.copy(preset_path, os.path.join(tmp_presets_dir, os.path.basename(preset_path)))

                    # Track which samples we actually need
                    used_sample_names = set()

                    # Copy all required instruments (modifying if uncorrected)
                    for instr_name in required_instruments:
                        instr_file = f"{instr_name}.json"
                        instr_source_path = find_file(instr_file, INSTRUMENTS_SEARCH_PATHS)
                        
                        if instr_source_path:
                            dest_path = os.path.join(tmp_instruments_dir, instr_file)
                            with open(instr_source_path, "r", encoding="utf-8") as inf:
                                instr_json = json.load(inf)
                            
                            # Identify used samples from zones
                            if "zones" in instr_json:
                                for zone in instr_json["zones"]:
                                    if "generators" in zone:
                                        s_name = zone["generators"].get("sample")
                                        if s_name:
                                            used_sample_names.add(s_name)
                                        
                                        # Strip delay compensation if uncorrected
                                        if BUILD_TYPE == "uncorrected" and "startAddrsOffset" in zone["generators"]:
                                            del zone["generators"]["startAddrsOffset"]
                            
                            # Save the instrument (either original or stripped)
                            with open(dest_path, "w", encoding="utf-8") as outf:
                                json.dump(instr_json, outf, indent=2)
                        else:
                            print(f"Warning: Instrument '{instr_name}' not found for preset '{raw_name}'")

                    # Copy ONLY the required samples
                    for s_base in used_sample_names:
                        # Copy the .json metadata for the sample
                        s_json = os.path.join(SAMPLES_DIR, f"{s_base}.json")
                        if os.path.exists(s_json):
                            shutil.copy(s_json, os.path.join(tmp_samples_dir, f"{s_base}.json"))
                        
                        # Copy the audio file (strictly .flac as requested)
                        found_audio = False
                        s_audio = os.path.join(SAMPLES_DIR, f"{s_base}.flac")
                        if os.path.exists(s_audio):
                            shutil.copy(s_audio, os.path.join(tmp_samples_dir, f"{s_base}.flac"))
                            found_audio = True
                        
                        if not found_audio:
                            print(f"   [WARNING] Missing FLAC audio for sample: {s_base}")

                    # 5. Execute sfutils compile
                    try:
                        cmd = ["sfutils", "compile", tmp_dir, output_sf2_path]
                        result = subprocess.run(cmd, capture_output=True, text=True)
                        
                        if result.returncode == 0:
                            print(f"   [SUCCESS] Saved to {output_sf2_path}")
                        else:
                            print(f"   [FAILED] {result.stderr.strip()}")
                    
                    except FileNotFoundError:
                        print("   [ERROR] 'sfutils' command not found. Please ensure it is installed.")
                        return 

        except Exception as e:
            print(f"   [ERROR] Unexpected error processing {preset_path}: {str(e)}")

    print("\n--- ALL INDIVIDUAL BUILDS COMPLETE ---")
    print(f"Files are located in: {OUTPUT_DIR}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("Usage: python build_vst.py")
        print("Builds each preset in the project as a standalone .sf2 file.")
    else:
        build_vst_individual()
