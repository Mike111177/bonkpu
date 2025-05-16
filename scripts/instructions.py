from collections import defaultdict


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
# overflowSet = lambda f: bool(f & FLAG_SIGN) != bool(f & FLAG_CARRY) #nvm i need a hardware flag for this to work


select_count = [MLI | CLO, MHI | CHO]

# Gets prepended to all instructions
microcode_prefix = [*select_count, RO | II | CE]

jumpi = [*select_count, RO | BI | CE, *select_count, CHI | RO | CE, CLI | BO]

skip_jumpi = [CE, CE]

select_address_arg = [
    *select_count,
    RO | BI | CE,
    *select_count,
    MHI | RO | CE,
    MLI | BO,
]

instruction_microcode = [
    ("NOP", []),
    ("LDAi", [*select_count, RO | AI | CE]),
    ("LDAa", [*select_address_arg, AI | RO]),
    ("STAa", [*select_address_arg, RI | AO]),
    ("ADDa", [*select_address_arg, BI | RO, EO | AI | FI]),
    ("ADDi", [*select_count, RO | BI | CE, EO | AI | FI]),
    ("SUBi", [*select_count, RO | BI | CE, SU | EO | AI | FI]),
    ("JMPa", jumpi),
    ("JEZa", lambda f: (jumpi if zeroSet(f) else skip_jumpi)),
    ("JNZa", lambda f: (jumpi if not zeroSet(f) else skip_jumpi)),
    ("JSa", lambda f: (jumpi if signSet(f) else skip_jumpi)),
    ("JNSa", lambda f: (jumpi if not signSet(f) else skip_jumpi)),
    ("JCa", lambda f: (jumpi if carrySet(f) else skip_jumpi)),
    ("JNCa", lambda f: (jumpi if not carrySet(f) else skip_jumpi)),
    # ("JOi", lambda f: (jumpi if overflowSet(f) else skip_jumpi)),
    # ("JNOi", lambda f: (jumpi if overflowSet(f) else skip_jumpi)),
    ("HLT", [HLT]),
]


def microcode_post_fn(instruction: list[int]):
    for i in range(len(instruction) - 1, -1, -1):
        if instruction[i]:
            instruction[i] |= IE
            break


instruction_table = {ins: idx for idx, (ins, _) in enumerate(instruction_microcode)}
instruction_variants = defaultdict(dict)
for variant, opcode in instruction_table.items():
    if variant[-1] in {"i", "a"}:
        base = variant[:-1]
        mode = variant[-1]
    else:
        base = variant
        mode = None
    instruction_variants[base][mode] = variant