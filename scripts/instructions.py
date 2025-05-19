from collections import defaultdict

# Halt
HLT = 1 << 23
# Ram Control
MHI = 1 << 22
MLI = 1 << 21
RI = 1 << 20
RO = 1 << 19
# Instruction Control
II = 1 << 18
# A Control
AI = 1 << 17
AO = 1 << 16
# B Control
BI = 1 << 15
BO = 1 << 14
# ALU Control
EO = 1 << 13
SU = 1 << 12
FI = 1 << 11
# Counter control
CE = 1 << 10
CHO = 1 << 9
CLO = 1 << 8
CHI = 1 << 7
CLI = 1 << 6
# Stack Control
STACK_MODE1 = 1 << 5
STACK_MODE0 = 1 << 4
SE = STACK_MODE0
SI = STACK_MODE1
SD = STACK_MODE1 | STACK_MODE0
SHO = 1 << 3
SLO = 1 << 2
# Reserved
X = 1 << 1
# Instruction end
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
ld_op = [*select_count, RO | II | CE]

jumpa = [*select_count, RO | BI | CE, *select_count, CHI | RO | CE, CLI | BO]

skip_a = [CE, CE]

select_address_arg = [
    *select_count,
    RO | BI | CE,
    *select_count,
    MHI | RO | CE,
    MLI | BO,
]

select_stack = [
    MLI | SLO,
    MHI | SHO,
]

instruction_microcode = [
    ("NOP", []),
    ("LDi", [*select_count, RO | AI | CE]),
    ("LDa", [*select_address_arg, AI | RO]),
    ("STa", [*select_address_arg, RI | AO]),
    ("ADDi", [*select_count, RO | BI | CE, EO | AI | FI]),
    ("ADDa", [*select_address_arg, BI | RO, EO | AI | FI]),
    ("SUBi", [*select_count, RO | BI | CE, SU | EO | AI | FI]),
    ("SUBa", [*select_address_arg, BI | RO, SU | EO | AI | FI]),
    ("JMPa", jumpa),
    ("JEZa", lambda f: (jumpa if zeroSet(f) else skip_a)),
    ("JNZa", lambda f: (jumpa if not zeroSet(f) else skip_a)),
    ("JSa", lambda f: (jumpa if signSet(f) else skip_a)),
    ("JNSa", lambda f: (jumpa if not signSet(f) else skip_a)),
    ("JCa", lambda f: (jumpa if carrySet(f) else skip_a)),
    ("JNCa", lambda f: (jumpa if not carrySet(f) else skip_a)),
    ("SEI", [SE]),
    ("SD", [SD]),
    ("SI", [SI]),
    ("PSH", [*select_stack, RI | AO | SD]),
    ("POP", [SI, *select_stack, AI | RO]),
    ("CALLa", [*select_stack, RI | CHO | SD, *select_stack, RI | CLO | SD, *jumpa]),
    # FIXME: RET corrupts the stack pointer for some reason
    ("RET", [SI, *select_stack, CLI | RO | SI, *select_stack, CHI | RO, *skip_a]),
    # ("JVi", lambda f: (jumpi if overflowSet(f) else skip_jumpi)),
    # ("JNVi", lambda f: (jumpi if overflowSet(f) else skip_jumpi)),
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
