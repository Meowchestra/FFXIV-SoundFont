import subprocess
import os

# Path to check (using your hidden .resources folder)
test_file = r".resources\[7.3] Instrument wav\sound\instruments\001grandpiano.scd_0.wav"

def diagnose():
    if not os.path.exists(test_file):
        print(f"Error: Could not find file at {test_file}")
        # Try without the dot just in case
        alternate = test_file.replace(r".resources", "resources")
        if os.path.exists(alternate):
             print(f"Wait, found it at {alternate} instead!")
             test_file_to_use = alternate
        else:
            return
    else:
        test_file_to_use = test_file

    print(f"--- Diagnosing: {test_file_to_use} ---\n")
    
    # Try running ffprobe to see what it detects
    try:
        cmd = ["ffprobe", "-v", "error", "-show_format", "-show_streams", test_file_to_use]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.stdout:
            print("FFPROBE RESULTS:")
            print(result.stdout)
        else:
            print("FFPROBE failed to find any streams.")
            if result.stderr:
                print(f"FFPROBE ERRORS: {result.stderr.strip()}")
                
    except FileNotFoundError:
        print("ffprobe not found. Please ensure ffmpeg/ffprobe is in your PATH.")

if __name__ == "__main__":
    diagnose()
