Patch 7.3 scd wav -> sfz -> sf2
sfz config based on older sf2 lo/hi keys and key center discoveries

Example use;
python convertSoundBank.py vst_bassdrum\vst_bassdrum.sfz vst_bassdrum.sf2

Since XIV natively has the audio format as ADPCM, uses ffmpeg to convert and read the file to prevent upscaling / pcm conversion artifacts.

---

Grab latest scd + wav files with https://github.com/goaaats/ffxiv-explorer-fork
[070000.win32.index]
sound/instruments

Then just replace wav files in the sfz folders before generating sf2 for any "new" updates.

Included in zip is also the old custom cymbal sf2 because I think the native game cymbal wav / loop values are completely broken.

---

Powershell convert all script;
# Loop through each folder in the current directory
Get-ChildItem -Directory | ForEach-Object {
    $folder = $_.FullName
    $folderName = $_.Name

    # Find the single .sfz file in this folder
    $sfz = Get-ChildItem -Path $folder -Filter *.sfz -File | Select-Object -First 1
    if ($sfz) {
        # Output should be in the current directory, named after the folder
        $sf2 = Join-Path (Get-Location) ($folderName + ".sf2")

        Write-Host "Converting $($sfz.FullName) -> $sf2"
        # Run your converter
        python convertSoundBank.py $sfz.FullName $sf2
    }
}

---

In polyphone, the preset # at the bottom when selecting Presets needs to be assigned specific numbers manually for the sf2 to function and not sound like a trumpet (overriding numbers defaults to first sf2 found?). Also 1000.031 needs to be set in Vol env release (x). Normally these should be done in the sfz when converting to sf2 but missing data for converter.

[Instrument] [Preset #]
bassdrum 117
bongo 116
cello 42
clarinet 71
cymbal 127
doublebass 43
electricguitarclean 27
electricguitarmuted 28
electricguitaroverdriven 29
electricguitarpowerchords 30
electricguitarspecial 31
fiddle 45
fife 72
flute 73
harp 46
horn 60
lute 24
oboe 68
panpipes 75
piano 0
saxophone 65
snaredrum 115
timpani 47
trombone 57
trumpet 56
tuba 58
viola 41
violin 40

The loop start/end times are also very important to be manually matched with the scd header for sustained notes. But sustain instruments must be -1 the scd value to fix audio popping issues (because of weird file hz?). 
These values need to be manually typed for each sample currently.

---

These files currently break with automated script and need manually fixing (renaming and reordering) in polyphone. They lose their sample # appended at the end. Special guitar breaks one of the samples into L/R hands (needs to be deleted) and lute is completely wrong order (might be sfz configuration order for low/hi keys?)

vst_electricguitarclean
vst_electricguitaroverdriven
vst_electricguitarpowerchords
vst_electricguitarspecial
vst_lute