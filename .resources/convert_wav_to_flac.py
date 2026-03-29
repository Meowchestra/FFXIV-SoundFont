import os
import subprocess
import shutil

# --- CONFIGURATION ---
SOURCE_DIR = r".resources\[7.3] Instrument wav\sound\instruments"
TARGET_DIR = r".resources\[7.3] Instrument flac\sound\instruments"

def convert_wav_to_flac():
    if not os.path.exists(SOURCE_DIR):
        print(f"Error: Source directory not found: {SOURCE_DIR}")
        return

    if not os.path.exists(TARGET_DIR):
        os.makedirs(TARGET_DIR)

    wav_files = [f for f in os.listdir(SOURCE_DIR) if f.lower().endswith(".wav")]
    print(f"Found {len(wav_files)} files. Starting conversion...")

    success_count = 0
    fail_count = 0

    for filename in wav_files:
        input_path = os.path.join(SOURCE_DIR, filename)
        output_path = os.path.join(TARGET_DIR, filename.replace(".wav", ".flac"))

        # -vn ensures ffmpeg doesn't get confused by "junk" in the FFXIV header
        # -c:a flac ensures a clean lossless output
        cmd = [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-i", input_path,
            "-vn", 
            "-c:a", "flac",
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            success_count += 1
        else:
            print(f"   [FAIL] {filename}: {result.stderr.strip()}")
            fail_count += 1

    print(f"\n--- Done: {success_count} success, {fail_count} failed ---")

if __name__ == "__main__":
    convert_wav_to_flac()
