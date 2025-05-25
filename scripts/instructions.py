from collections import defaultdict

# Instruction end
IE = 1 << 15
# Counter control
CE = 1 << 14
# Ram Control
MU = 1 << 13
MB = 1 << 12
# ALU Control
SU = 1 << 11
FI = 1 << 10
# Stack Pointer Control (bit 8-9)
SE = 1 << 8
SI = 2 << 8
SD = 3 << 8
# Bus in control (bit 4-7)
RI = 1 << 4
AI = 2 << 4
BI = 3 << 4
II = 4 << 4
CHI = 5 << 4
CLI = 6 << 4
MHI = 7 << 4
MLI = 8 << 4
OHI = 9 << 4
OLI = 10 << 4
OC = 11 << 4
# Bus out control (bit 0-3)
RO = 1
AO = 2
BO = 3
EO = 4
CHO = 5
CLO = 6
SHO = 7
SLO = 8
HLT = 15  # We can't halt and output at the same time anyway :D


# Flag logic
FLAG_ZERO = 0b1
FLAG_SIGN = 0b10
FLAG_CARRY = 0b100
zeroSet = lambda f: f & FLAG_ZERO
signSet = lambda f: f & FLAG_SIGN
carrySet = lambda f: f & FLAG_CARRY
# overflowSet = lambda f: bool(f & FLAG_SIGN) != bool(f & FLAG_CARRY) #nvm i need a hardware flag for this to work


select_count = [MLI | CLO, MHI | CHO | MU]

# Gets prepended to all instructions
ld_op = [*select_count, RO | II | CE]

jumpa = [
    *select_count,
    RO | BI | CE,
    CHI | RO | MB | CE,
    CLI | BO,
]

skip_a = [CE, CE]

select_address = [
    MLI | RO,
    MHI | RO | MB | MU,
]

select_address_arg = [
    *select_count,
    MLI | RO | CE,
    MHI | RO | MB | MU | CE,
]

select_offset_arg = [
    *select_count,
    OLI | RO | CE,
    OHI | RO | MB | CE,
]

select_stack = [
    MLI | SLO,
    MHI | SHO | MU,
]

instruction_microcode = [
    ("NOP", []),
    ("LDi", [*select_count, RO | AI | CE]),
    ("LDa", [*select_address_arg, AI | RO]),
    ("LDp", [*select_address_arg, *select_address, AI | RO]),
    ("LDs", [*select_offset_arg, *select_stack, AI | RO, OC]),
    ("STa", [*select_address_arg, RI | AO]),
    ("STp", [*select_address_arg, *select_address, RI | AO]),
    ("STs", [*select_offset_arg, *select_stack, RI | AO, OC]),
    ("ADDi", [*select_count, RO | BI | CE, EO | AI | FI]),
    ("ADDa", [*select_address_arg, BI | RO, EO | AI | FI]),
    ("ADDs", [*select_offset_arg, *select_stack, RO | BI, EO | AI | FI, OC]),
    ("SUBi", [*select_count, RO | BI | CE, SU | EO | AI | FI]),
    ("SUBa", [*select_address_arg, BI | RO, SU | EO | AI | FI]),
    ("SUBs", [*select_offset_arg, *select_stack, RO | BI, SU | EO | AI | FI, OC]),
    ("JMPa", jumpa),
    ("JEZa", lambda f: (jumpa if zeroSet(f) else skip_a)),
    ("JNZa", lambda f: (jumpa if not zeroSet(f) else skip_a)),
    ("JSa", lambda f: (jumpa if signSet(f) else skip_a)),
    ("JNSa", lambda f: (jumpa if not signSet(f) else skip_a)),
    ("JCa", lambda f: (jumpa if carrySet(f) else skip_a)),
    ("JNCa", lambda f: (jumpa if not carrySet(f) else skip_a)),
    # ("JVi", lambda f: (jumpi if overflowSet(f) else skip_jumpi)),
    # ("JNVi", lambda f: (jumpi if overflowSet(f) else skip_jumpi)),
    ("SEI", [SE]),
    ("SD", [SD]),
    ("SI", [SI]),
    ("PSH", [*select_stack, RI | AO | SD]),
    ("PSHi", [*select_count, RO | BI | CE, *select_stack, RI | BO | SD]),
    ("POP", [SI, *select_stack, AI | RO]),
    ("CALLa", [*select_stack, RI | CHO | SD, *select_stack, RI | CLO | SD, *jumpa]),
    ("RET", [SI, *select_stack, CLI | RO | SI, *select_stack, CHI | RO, *skip_a]),
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
    if variant[-1] in {"i", "a", "p", "s"}:
        base = variant[:-1]
        mode = variant[-1]
    else:
        base = variant
        mode = None
    instruction_variants[base][mode] = variant
