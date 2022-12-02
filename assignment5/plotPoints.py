######################
#Filename: plotPts
######################

luminosity = {
    0 : [
        0b10000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
    ],
    1 : [
        0b01000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
    ],
    2 : [
        0b00100000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
    ],
    3 : [
        0b00010000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
    ],
    4 : [
        0b00001000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
    ],
    5 : [
        0b00000100,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
    ],
    6 : [
        0b00000010,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
    ],
    7 : [
        0b00000001,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
    ],
    8 : [
        0b00000000,
        0b10000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
    ],
    9 : [
        0b00000000,
        0b01000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
    ],
    10 : [
        0b00000000,
        0b00100000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
    ],
    11 : [
        0b00000000,
        0b00010000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
    ],
    12 : [
        0b00000000,
        0b00001000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
    ],
    13 : [
        0b00000000,
        0b00000100,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
    ],
    14 : [
        0b00000000,
        0b00000010,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
    ],
    15 : [
        0b00000000,
        0b00000001,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
    ],
    16 : [
        0b00000000,
        0b00000000,
        0b10000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
    ],
    17 : [
        0b00000000,
        0b00000000,
        0b01000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
    ],
    18 : [
        0b00000000,
        0b00000000,
        0b00100000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
    ],
    19 : [
        0b00000000,
        0b00000000,
        0b00010000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
    ],
    20 : [
        0b00000000,
        0b00000000,
        0b00001000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
    ],
    21 : [
        0b00000000,
        0b00000000,
        0b00000100,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
    ],
    22 : [
        0b00000000,
        0b00000000,
        0b00000010,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
    ],
    23 : [
        0b00000000,
        0b00000000,
        0b00000001,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
    ],
    24 : [
        0b00000000,
        0b00000000,
        0b00000000,
        0b10000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
    ],
    25 : [
        0b00000000,
        0b00000000,
        0b00000000,
        0b01000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
    ],
    26 : [
        0b00000000,
        0b00000000,
        0b00000000,
        0b00100000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
    ],
    27 : [
        0b00000000,
        0b00000000,
        0b00000000,
        0b00010000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
    ],
    28 : [
        0b00000000,
        0b00000000,
        0b00000000,
        0b00001000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
    ],
    29 : [
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000100,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
    ],
    30 : [
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000010,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
    ],
    31 : [
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000001,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
    ],
    32 : [
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b10000000,
        0b00000000,
        0b00000000,
        0b00000000,
    ],
    33 : [
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b01000000,
        0b00000000,
        0b00000000,
        0b00000000,
    ],
    34 : [
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00100000,
        0b00000000,
        0b00000000,
        0b00000000,
    ],
    35 : [
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00010000,
        0b00000000,
        0b00000000,
        0b00000000,
    ],
    36 : [
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00001000,
        0b00000000,
        0b00000000,
        0b00000000,
    ],
    37 : [
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000100,
        0b00000000,
        0b00000000,
        0b00000000,
    ],
    38 : [
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000010,
        0b00000000,
        0b00000000,
        0b00000000,
    ],
    39 : [
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000001,
        0b00000000,
        0b00000000,
        0b00000000,
    ],
    40 : [
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b10000000,
        0b00000000,
        0b00000000,
    ],
    41 : [
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b01000000,
        0b00000000,
        0b00000000,
    ],
    42 : [
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00100000,
        0b00000000,
        0b00000000,
    ],
    43 : [
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00010000,
        0b00000000,
        0b00000000,
    ],
    44 : [
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00001000,
        0b00000000,
        0b00000000,
    ],
    45 : [
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000100,
        0b00000000,
        0b00000000,
    ],
    46 : [
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000010,
        0b00000000,
        0b00000000,
    ],
    47 : [
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000001,
        0b00000000,
        0b00000000,
    ],
    48 : [
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b10000000,
        0b00000000,
    ],
    49 : [
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b01000000,
        0b00000000,
    ],
    50 : [
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00100000,
        0b00000000,
    ],
    51 : [
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00010000,
        0b00000000,
    ],
    52 : [
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00001000,
        0b00000000,
    ],
    53 : [
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000100,
        0b00000000,
    ],
    54 : [
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000010,
        0b00000000,
    ],
    55 : [
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000001,
        0b00000000,
    ],
    56 : [
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b10000000,
    ],
    57 : [
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b01000000,
    ],
    58 : [
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00100000,
    ],
    59 : [
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00010000,
    ],
    60 : [
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00001000,
    ],
    61 : [
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000100,
    ],
    62 : [
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000010,
    ],
    63 : [
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000001,
    ],
}
