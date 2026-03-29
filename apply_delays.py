import json
import os
import glob
import soundfile as sf
import numpy as np

# 1. Calculate delays directly from FLAC files using ffmpeg's silencedetect logic
THRESHOLD_DB = -45
SILENCE_DURATION = 0.001
threshold_amp = 10 ** (THRESHOLD_DB / 20.0)

sample_delays = {}
flac_files = glob.glob(os.path.join("samples", "*.flac"))

print(f"Scanning {len(flac_files)} audio files for initial silence (Threshold: {THRESHOLD_DB}dB, Min Duration: {SILENCE_DURATION}s)...")

for flac_path in flac_files:
    sample_name = os.path.basename(flac_path).replace(".flac", "")
    
    try:
        data, sr = sf.read(flac_path)
    except Exception as e:
        print(f"Error reading {flac_path}: {e}")
        continue
    
    # Handle stereo/multichannel by taking the max absolute amplitude across channels
    if len(data.shape) > 1:
        data = np.max(np.abs(data), axis=1)
    else:
        data = np.abs(data)
        
    exceed_indices = np.where(data > threshold_amp)[0]
    
    if len(exceed_indices) == 0:
        delay_sec = 0.0
    else:
        delay_sec = exceed_indices[0] / float(sr)
        
    # ffmpeg's silencedetect with d=0.001 ignores silence chunks shorter than 0.001s
    if delay_sec >= SILENCE_DURATION:
        samples = int(round(delay_sec * sr))
        sample_delays[sample_name] = samples

print(f"Computed >1ms delays for {len(sample_delays)} files out of {len(flac_files)}.")

# 2. Patch the instrument JSONs
instrument_files = glob.glob(os.path.join("instruments", "*.json"))
mod_count = 0
patched_zones = 0
cleared_zones = 0

for file_path in instrument_files:
    with open(file_path, "r", encoding='utf-8') as f:
        data = json.load(f)
    
    modified = False
    for zone in data.get("zones", []):
        generators = zone.get("generators", {})
        sample_ref = generators.get("sample")
        
        if sample_ref:
            # Check if this sample has a detected delay >= 1ms
            if sample_ref in sample_delays:
                offset = sample_delays[sample_ref]
                
                old_coarse = generators.get("startAddrsCoarseOffset", 0)
                old_fine = generators.get("startAddrsOffset", 0)
                
                coarse = offset // 32768
                fine = offset % 32768
                
                # Update if different
                if old_coarse != coarse or old_fine != fine:
                    generators.pop("startAddrsCoarseOffset", None)
                    generators.pop("startAddrsOffset", None)
                    
                    if coarse > 0:
                        generators["startAddrsCoarseOffset"] = coarse
                    if fine > 0:
                        generators["startAddrsOffset"] = fine
                        
                    modified = True
                    patched_zones += 1
            else:
                # If delay is < 1ms, ENSURE we clear any existing offset
                if "startAddrsCoarseOffset" in generators or "startAddrsOffset" in generators:
                    generators.pop("startAddrsCoarseOffset", None)
                    generators.pop("startAddrsOffset", None)
                    modified = True
                    cleared_zones += 1
            
    if modified:
        with open(file_path, "w", encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        mod_count += 1

print(f"Updated {mod_count} instrument files:")
print(f" - {patched_zones} zones had delays applied or updated.")
print(f" - {cleared_zones} zones were cleared because their delay was <1ms or zero.")
