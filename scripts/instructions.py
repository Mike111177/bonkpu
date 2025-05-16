HLT = 1 << 23
MHI = 1 << 22
MLI = 1 << 21
RI = 1 << 20
RO = 1 << 19
II = 1 << 18
AI = 1 << 16
AO = 1 << 15
BI = 1 << 14
BO = 1 << 13
EO = 1 << 12
SU = 1 << 11
FI = 1 << 10
CE = 1 << 9
CHO = 1 << 8
CLO = 1 << 7
CHI = 1 << 6
CLI = 1 << 5
X = 1 << 4
X = 1 << 3
X = 1 << 2
X = 1 << 1
IE = 1 << 0

FLAG_ZERO = 0b1
FLAG_SIGN = 0b10
FLAG_CARRY = 0b100
zeroSet = lambda f: f & FLAG_ZERO
signSet = lambda f: f & FLAG_SIGN
carrySet = lambda f: f & FLAG_CARRY
#overflowSet = lambda f: bool(f & FLAG_SIGN) != bool(f & FLAG_CARRY) #nvm i need a hardware flag for this to work

# Gets prepended to all instructions
instructions_prefix = [MHI | CHO, MLI | CLO, RO | II | CE, CE]

jumpi = [
    MHI | CHO,
    MLI | CLO,
    RO | BI | CE,
    MHI | CHO,
    MLI | CLO,
    CHI | RO | CE,
    CLI | BO,
]

skip_jumpi = [CE, CE]

instructions_table = [
    ("NOP", []),
    ("LDAi", [MHI | CHO, MLI | CLO, RO | AI | CE]),
    ("ADDi", [MHI | CHO, MLI | CLO, RO | BI | CE, EO | AI | FI]),
    ("SUBi", [MHI | CHO, MLI | CLO, RO | BI | CE, SU | EO | AI | FI]),
    ("JMPi", jumpi),
    ("JEZi", lambda f: (jumpi if zeroSet(f) else skip_jumpi)),
    ("JNZi", lambda f: (jumpi if not zeroSet(f) else skip_jumpi)),
    ("JSi", lambda f: (jumpi if signSet(f) else skip_jumpi)),
    ("JNSi", lambda f: (jumpi if not signSet(f) else skip_jumpi)),
    ("JCi", lambda f: (jumpi if carrySet(f) else skip_jumpi)),
    ("JNCi", lambda f: (jumpi if not carrySet(f) else skip_jumpi)),
    #("JOi", lambda f: (jumpi if overflowSet(f) else skip_jumpi)),
    #("JNOi", lambda f: (jumpi if overflowSet(f) else skip_jumpi)),
    ("HLT", [HLT]),
]

def instruction_post_fn(instruction: list[int]):
    for i in range(len(instruction) - 1, -1, -1):
        if instruction[i]:
            instruction[i] |= IE
            break