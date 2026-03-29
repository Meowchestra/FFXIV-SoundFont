import re

class SampleStruct:
    Samplename = ""
    ScdNum = ""
    Samples = 0
    Version = 0
    Unk1 = 0
    BankNumber = 0
    Index = 0
    HighKey = 0
    LowKey = 0
    KeyIndex = 0
    InstrumentNumber = 0
    SampleDelay = -1
    def __init__(self):
        return

MidiToIngameDict = {
    "047harp" :1 ,
    "001grandpiano" :2,
    "026steelguitar":3,
    "046pizzicato":4,
    "074flute":5,
    "069oboe":6,
    "072clarinet":7,
    "073piccolo":8,
    "076panflute":9,
    "048timpani":10,
    "097bongo":11,
    "098bd":12,
    "099snare":13,
    "100cymbal":14,
    "057trumpet":15,
    "058trombone":16,
    "059tuba":17,
    "061frenchhorn":18,
    "066altosax":19,
    "041violin":20,
    "042viola":21,
    "043cello":22,
    "044contrabass":23,
    "030driveguitar":24,
    "028cleanguitar":25,
    "029muteguitar":26,
    "031powerguitar":27,
    "032fxguitar":28
}

Comments = {
    1 : "// 1 / Harp / 047harp.scd",
    2 :"// 2 / Piano / 001grandpiano.scd",
    3 :"// 3 / Lute / 026steelguitar.scd",
    4 :"// 4 / Fiddle / 046pizzicato.scd",
    5 :"// 5 / Flute / 074flute.scd",
    6 :"// 6 / Oboe / 069oboe.scd",
    7 :"// 7 / Clarinet / 072clarinet.scd",
    8 : "// 8 / Fife / 073piccolo.scd",
    9:"// 9 / Panpipes / 076panflute.scd",
    10:"// 10 / Timpani / 048timpani.scd",
    11:"// 11 / Bongo / 097bongo.scd",
    12:"// 12 / Bass Drum / 098bd.scd",
    13:"// 13 / Snare Drum / 099snare.scd",
    14:"// 14 / Cymbal / 100cymbal.scd",
    15:"// 15 / Trumpet / 057trumpet.scd",
    16:"// 16 / Trombone / 058trombone.scd",
    17:"// 17 / Tuba / 059tuba.scd",
    18:"// 18 / Horn / 061frenchhorn.scd",
    19:"// 19 / Saxophone / 066altosax.scd",
    20:"// 20 / Violin / 041violin.scd",
    21:"// 21 / Viola / 042viola.scd",
    22:"// 22 / Cello / 043cello.scd",
    23:"// 23 / Double Bass / 044contrabass.scd",
    24:"// 24 / Electric Guitar: Overdriven / 030driveguitar.scd",
    25:"// 25 / Electric Guitar: Clean / 028cleanguitar.scd",
    26:"// 26 / Electric Guitar: Muted / 029muteguitar.scd",
    27:"// 27 / Electric Guitar: Power Chords / 031powerguitar.scd",
    28:"// 28 / Electric Guitar: Special / 032fxguitar.scd"
}


def has_numbers(inputString):
    return bool(re.search(r'\d', inputString))