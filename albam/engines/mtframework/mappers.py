from enum import Enum


# Maps the hash id of each file type that the format accept
# and its corresponding extension. If the type is used throughout
# This list was provided by users in the Xentax forums.
# To do: search the users and credit them.

FILE_ID_TO_EXTENSION = {
    0x22fa09: "hpe",
    0x26e7ff: "ccl",
    0x86b80f: "plexp",
    0xfda99b: "ntr",
    0x2358e1a: "spkg",
    0x2373ba7: "spn",
    0x2833703: "efs",
    0x58a15856: "mod",
    0x315e81f: "sds",
    0x437bcf2: "grw",
    0x4b4be62: "tmd",
    0x525aee2: "wfp",
    0x5a36d08: "qif",
    0x69a1911: "olp",
    0x737e28b: "rst",
    0x7437cce: "base",
    0x79b5f3e: "pci",
    0x7b8bcde: "fca",
    0x7f768af: "gii",
    0x89bef2c: "sap",
    0xa74682f: "rnp",
    0xc4fcae4: "PldefendParam",
    0xd06be6b: "tmn",
    0xecd7df4: "sca",
    0x11c35522: "gr2",
    0x12191ba1: "epv",
    0x12688d38: "pjp",
    0x12c3bfa7: "cpl",
    0x133917ba: "mss",
    0x14428eae: "gce",
    0x15302ef4: "lot",
    0x157388d3: "itl",
    0x15773620: "nmr",
    0x167dbbff: "stq",
    0x1823137d: "mlm",
    0x19054795: "nml",
    0x199c56c0: "ocl",
    0x1b520b68: "zon",
    0x1bcc4966: "srq",
    0x1c2b501f: "atr",
    0x1eb3767c: "spr",
    0x2052d67e: "sn2",
    0x215896c2: "statusparam",
    0x2282360d: "jex",
    0x22948394: "gui",
    0x22b2a2a2: "PlNeckPos",
    0x232e228c: "rev",
    0x241f5deb: "tex",
    0x242bb29a: "gmd",
    0x257d2f7c: "swm",
    0x2749c8a8: "mrl",
    0x271d08fe: "ssq",
    0x272b80ea: "prp",
    0x276de8b7: "e2d",
    0x2a37242d: "gpl",
    0x2a4f96a8: "rbd",
    0x2b0670a5: "map",
    0x2b303957: "gop",
    0x2b40ae8f: "equ",
    0x2ce309ab: "joblvl",
    0x2d12e086: "srd",
    0x2d462600: "gfd",
    0x30fc745f: "smx",
    0x312607a4: "bll",
    0x31b81aa5: "qr",
    0x325aaca5: "shl",
    0x32e2b13b: "edp",
    0x33b21191: "esp",
    0x354284e7: "lvl",
    0x358012e8: "vib",
    0x36019854: "bed",
    0x39a0d1d6: "sms",
    0x39c52040: "lcm",
    0x3a947ac1: "cql",
    0x3bba4e33: "qct",
    0x3d97ad80: "amr",
    0x3e356f93: "stc",
    0x3e363245: "chn",
    0x3fb52996: "imx",
    0x4046f1e1: "ajp",
    0x437662fc: "oml",
    0x4509fa80: "itemlv",
    0x456b6180: "cnsshake",
    0x472022df: "aIPlactParam",
    0x48538ffd: "ist",
    0x48c0af2d: "msl",
    0x49b5a885: "ssc",
    0x4b704cc0: "mia",
    0x4c0db839: "sdl",
    0x4ca26828: "bmse",
    0x4e397417: "ean",
    0x4e44fb6d: "fpe",
    0x4ef19843: "nav",
    0x4fb35a95: "aor",
    0x50f3d713: "skl",
    0x5175c242: "geo2",
    0x51fc779f: "sbc",
    0x522f7a3d: "fcp",
    0x52dbdcd6: "rdd",
    0x535d969f: "ctc",
    0x5802b3ff: "ahc",
    0x59d80140: "ablparam",
    0x5a61a7c8: "fed",
    0x5a7fea62: "ik",
    0x5b334013: "bap",
    0x5ea7a3e9: "sky",
    0x5f36b659: "way",
    0x5f88b715: "epd",
    0x60bb6a09: "hed",
    0x6186627d: "wep",
    0x619d23df: "shp",
    0x628dfb41: "gr2s",
    0x63747aa7: "rpi",
    0x63b524a7: "ltg",
    0x64387ff1: "qlv",
    0x65b275e5: "sce",
    0x66b45610: "fsm",
    0x671f21da: "stp",
    0x69a5c538: "dwm",
    0x6d0115ed: "prt",
    0x6d5ae854: "efl",
    0x6db9fa5f: "cmc",
    0x6ee70eff: "pcf",
    0x6f302481: "plw",
    0x6fe1ea15: "spl",
    0x72821c38: "stm",
    0x73850d05: "arc",
    0x754b82b4: "ahs",
    0x76820d81: "lmt",
    0x76de35f6: "rpn",
    0x7808ea10: "rtex",
    0x7817ffa5: "fbik_human",
    0x7aa81cab: "eap",
    0x7bec319a: "sps",
    0x7da64808: "qmk",
    0x7e1c8d43: "pcs",
    0x7e33a16c: "spc",
    0x7e4152ff: "stg",
    0x17a550d: "lom",
    0x253f147: "hit",
    0x39d71f2: "rvt",
    0xdadab62: "oba",
    0x10c460e6: "msg",
    0x176c3f95: "los",
    0x19a59a91: "lnk",
    0x1ba81d3c: "nck",
    0x1ed12f1b: "glp",
    0x1efb1b67: "adh",
    0x2447d742: "idm",
    0x266e8a91: "lku",
    0x2c4666d1: "smh",
    0x2dc54131: "cdf",
    0x30ed4060: "pth",
    0x36e29465: "hkx",
    0x38f66fc3: "seg",
    0x430b4ff4: "ptl",
    0x46810940: "egv",
    0x4d894d5d: "cmi",
    0x4e2fef36: "mtg",
    0x4f16b7ab: "hri",
    0x50f9db3e: "bfx",
    0x5204d557: "shp",
    0x538120de: "eng",
    0x557ecc08: "aef",
    0x585831aa: "pos",
    0x5898749c: "bgm",
    0x60524fbb: "shw",
    0x60dd1b16: "lsp",
    0x758b2eb7: "cef",
    0x7d1530c2: "sngw",
    0x46fb08ba: "bmt",
    0x285a13d9: "vzo",
    0x4323d83a: "stex",
    0x6a5cdd23: "occ",
    }

EXTENSION_TO_FILE_ID = {ext_desc: h for h, ext_desc in FILE_ID_TO_EXTENSION.items()}


class Mod156BoneAnimationMapping(Enum):
    """
    Mod156.bones_animation_mapping is an array of 256 bytes. Each index
    correspond to a certain predefined bone type, and it's used to be able to
    transfer animations between models.
    """
    ROOT = 0
    LOWER_SPINE = 1
    UPPER_SPINE = 2
    NECK = 3
    HEAD = 4
    RIGHT_SHOULDER = 5
    RIGHT_UPPER_ARM = 6
    RIGHT_ARM = 7
    RIGHT_WRIST = 8
    RIGHT_HAND = 9
    LEFT_SHOULDER = 10
    LEFT_UPPER_ARM = 11
    LEFT_ARM = 12
    LEFT_WRIST = 13
    LEFT_HAND = 14
    HIPS = 15
    RIGHT_UPPER_LEG = 16
    RIGHT_LEG = 17
    RIGHT_FOOT = 18
    RIGHT_TOE = 19
    LEFT_UPPER_LEG = 20
    LEFT_LEG = 21
    LEFT_FOOT = 22
    LEFT_TOE = 23
    RIGHT_UPPER_THUMB = 24
    RIGHT_MIDDLE_THUMB = 25
    RIGHT_LOWER_THUMB = 26
    RIGHT_UPPER_INDEX_FINGER = 27
    RIGHT_MIDDLE_INDEX_FINGER = 28
    RIGHT_LOWER_INDEX_FINGER = 29
    RIGHT_UPPER_MIDDLE_FINGER = 30
    RIGHT_MIDDLE_MIDDLE_FINGER = 31
    RIGHT_LOWER_MIDDLE_FINGER = 32
    RIGHT_PALM = 33
    RIGHT_UPPER_RING_FINGER = 34
    RIGHT_MIDDLE_RING_FINGER = 35
    RIGHT_LOWER_RING_FINGER = 36
    UNK_37 = 37  # Chris 56
    UNK_38 = 38  # Chris 57
    UNK_39 = 39  # Chris 58
    UNK_40 = 40  # Chris 96
    UNK_41 = 41  # Chris 97
    UNK_42 = 42  # Chris 98
    UNK_43 = 43  # Chris 85
    UNK_44 = 44  # Chris 86
    UNK_45 = 45  # Chris 87
    UNK_46 = 46  # Chris 82
    UNK_47 = 47  # Chris 83
    UNK_48 = 48  # Chris 84
    UNK_49 = 49  # Chris 88
    UNK_50 = 50  # Chris 92
    UNK_51 = 51  # Chris 93
    UNK_52 = 52  # Chris 94
    UNK_53 = 53  # Chris 89
    UNK_54 = 54  # Chris 90
    UNK_55 = 55  # Chris 91
    UNK_56 = 56  # Chris 5
    UNK_57 = 57  # Chris 6
    UNK_58 = 58  # Chris 7
    UNK_59 = 59  # Chris 8
    UNK_60 = 60  # Chris 9
    UNK_61 = 61  # Chris 255
    UNK_62 = 62  # Chris 74
    UNK_63 = 63  # Chris 49
    UNK_64 = 64  # Chris 76
    UNK_65 = 65  # Chris 78
    UNK_66 = 66  # Chris 123
    UNK_67 = 67  # Chris 122
    UNK_68 = 68  # Chris 116
    UNK_69 = 69  # Chris 118
    UNK_70 = 70  # Chris 72
    UNK_71 = 71  # Chris 73
    UNK_72 = 72  # Chris 47
    UNK_73 = 73  # Chris 48
    UNK_74 = 74  # Chris 52
    UNK_75 = 75  # Chris 51
    UNK_76 = 76  # Chris 103
    UNK_77 = 77  # Chris 104
    UNK_78 = 78  # Chris 101
    UNK_79 = 79  # Chris 102
    UNK_80 = 80  # Chris 100
    UNK_81 = 81  # Chris 99
    UNK_82 = 82  # Chris 255
    UNK_83 = 83  # Chris 255
    UNK_84 = 84  # Chris 255
    UNK_85 = 85  # Chris 255
    UNK_86 = 86  # Chris 255
    UNK_87 = 87  # Chris 255
    UNK_88 = 88  # Chris 255
    UNK_89 = 89  # Chris 255
    UNK_90 = 90  # Chris 255
    UNK_91 = 91  # Chris 255
    UNK_92 = 92  # Chris 255
    UNK_93 = 93  # Chris 255
    UNK_94 = 94  # Chris 255
    UNK_95 = 95  # Chris 255
    UNK_96 = 96  # Chris 255
    UNK_97 = 97  # Chris 255
    UNK_98 = 98  # Chris 255
    UNK_99 = 99  # Chris 255
    UNK_100 = 100  # Chris 68
    UNK_101 = 101  # Chris 95
    UNK_102 = 102  # Chris 105
    UNK_103 = 103  # Chris 106
    UNK_104 = 104  # Chris 255
    UNK_105 = 105  # Chris 255
    UNK_106 = 106  # Chris 255
    UNK_107 = 107  # Chris 255
    UNK_108 = 108  # Chris 124
    UNK_109 = 109  # Chris 125
    UNK_110 = 110  # Chris 126
    UNK_111 = 111  # Chris 127
    UNK_112 = 112  # Chris 128
    UNK_113 = 113  # Chris 129
    UNK_114 = 114  # Chris 107
    UNK_115 = 115  # Chris 108
    UNK_116 = 116  # Chris 109
    UNK_117 = 117  # Chris 110
    UNK_118 = 118  # Chris 19
    UNK_119 = 119  # Chris 20
    UNK_120 = 120  # Chris 21
    UNK_121 = 121  # Chris 22
    UNK_122 = 122  # Chris 15
    UNK_123 = 123  # Chris 16
    UNK_124 = 124  # Chris 17
    UNK_125 = 125  # Chris 18
    UNK_126 = 126  # Chris 26
    UNK_127 = 127  # Chris 27
    UNK_128 = 128  # Chris 24
    UNK_129 = 129  # Chris 25
    UNK_130 = 130  # Chris 23
    UNK_131 = 131  # Chris 255
    UNK_132 = 132  # Chris 255
    UNK_133 = 133  # Chris 255
    UNK_134 = 134  # Chris 255
    UNK_135 = 135  # Chris 255
    UNK_136 = 136  # Chris 255
    UNK_137 = 137  # Chris 255
    UNK_138 = 138  # Chris 255
    UNK_139 = 139  # Chris 255
    UNK_140 = 140  # Chris 255
    UNK_141 = 141  # Chris 255
    UNK_142 = 142  # Chris 255
    UNK_143 = 143  # Chris 255
    UNK_144 = 144  # Chris 255
    UNK_145 = 145  # Chris 255
    UNK_146 = 146  # Chris 255
    UNK_147 = 147  # Chris 255
    UNK_148 = 148  # Chris 255
    UNK_149 = 149  # Chris 255
    UNK_150 = 150  # Chris 255
    UNK_151 = 151  # Chris 255
    UNK_152 = 152  # Chris 255
    UNK_153 = 153  # Chris 255
    UNK_154 = 154  # Chris 255
    UNK_155 = 155  # Chris 255
    UNK_156 = 156  # Chris 255
    UNK_157 = 157  # Chris 255
    UNK_158 = 158  # Chris 255
    UNK_159 = 159  # Chris 255
    UNK_160 = 160  # Chris 255
    UNK_161 = 161  # Chris 255
    UNK_162 = 162  # Chris 255
    UNK_163 = 163  # Chris 255
    UNK_164 = 164  # Chris 255
    UNK_165 = 165  # Chris 255
    UNK_166 = 166  # Chris 255
    UNK_167 = 167  # Chris 255
    UNK_168 = 168  # Chris 255
    UNK_169 = 169  # Chris 255
    UNK_170 = 170  # Chris 255
    UNK_171 = 171  # Chris 255
    UNK_172 = 172  # Chris 255
    UNK_173 = 173  # Chris 255
    UNK_174 = 174  # Chris 255
    UNK_175 = 175  # Chris 255
    UNK_176 = 176  # Chris 255
    UNK_177 = 177  # Chris 255
    UNK_178 = 178  # Chris 255
    UNK_179 = 179  # Chris 255
    UNK_180 = 180  # Chris 44
    UNK_181 = 181  # Chris 43
    UNK_182 = 182  # Chris 42
    UNK_183 = 183  # Chris 41
    UNK_184 = 184  # Chris 40
    UNK_185 = 185  # Chris 39
    UNK_186 = 186  # Chris 38
    UNK_187 = 187  # Chris 37
    UNK_188 = 188  # Chris 36
    UNK_189 = 189  # Chris 35
    UNK_190 = 190  # Chris 34
    UNK_191 = 191  # Chris 33
    UNK_192 = 192  # Chris 32
    UNK_193 = 193  # Chris 31
    UNK_194 = 194  # Chris 30
    UNK_195 = 195  # Chris 29
    UNK_196 = 196  # Chris 28
    UNK_197 = 197  # Chris 14
    UNK_198 = 198  # Chris 13
    UNK_199 = 199  # Chris 12
    UNK_200 = 200  # Chris 11
    UNK_201 = 201  # Chris 10
    UNK_202 = 202  # Chris 255
    UNK_203 = 203  # Chris 255
    UNK_204 = 204  # Chris 255
    UNK_205 = 205  # Chris 255
    UNK_206 = 206  # Chris 255
    UNK_207 = 207  # Chris 255
    UNK_208 = 208  # Chris 255
    UNK_209 = 209  # Chris 255
    UNK_210 = 210  # Chris 255
    UNK_211 = 211  # Chris 255
    UNK_212 = 212  # Chris 255
    UNK_213 = 213  # Chris 255
    UNK_214 = 214  # Chris 255
    UNK_215 = 215  # Chris 255
    UNK_216 = 216  # Chris 255
    UNK_217 = 217  # Chris 255
    UNK_218 = 218  # Chris 255
    UNK_219 = 219  # Chris 255
    UNK_220 = 220  # Chris 255
    UNK_221 = 221  # Chris 255
    UNK_222 = 222  # Chris 255
    UNK_223 = 223  # Chris 255
    UNK_224 = 224  # Chris 255
    UNK_225 = 225  # Chris 255
    UNK_226 = 226  # Chris 255
    UNK_227 = 227  # Chris 255
    UNK_228 = 228  # Chris 255
    UNK_229 = 229  # Chris 255
    UNK_230 = 230  # Chris 255
    UNK_231 = 231  # Chris 255
    UNK_232 = 232  # Chris 255
    UNK_233 = 233  # Chris 255
    UNK_234 = 234  # Chris 255
    UNK_235 = 235  # Chris 255
    UNK_236 = 236  # Chris 255
    UNK_237 = 237  # Chris 255
    UNK_238 = 238  # Chris 255
    UNK_239 = 239  # Chris 255
    UNK_240 = 240  # Chris 255
    UNK_241 = 241  # Chris 255
    UNK_242 = 242  # Chris 255
    UNK_243 = 243  # Chris 255
    UNK_244 = 244  # Chris 255
    UNK_245 = 245  # Chris 255
    UNK_246 = 246  # Chris 255
    UNK_247 = 247  # Chris 255
    UNK_248 = 248  # Chris 255
    UNK_249 = 249  # Chris 255
    UNK_250 = 250  # Chris 255
    UNK_251 = 251  # Chris 255
    UNK_252 = 252  # Chris 255
    UNK_253 = 253  # Chris 255
    UNK_254 = 254  # Chris 255
    UNK_255 = 255  # Chris 255
