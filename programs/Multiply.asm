SEI ; init stack pointer
A=$0x8000
B=$0x8001
    LD 4      ; 4x6
    ST A
    LD 6
    ST B
    CALL multiply
    ST A      ; resultx9
    LD 9
    ST B
    CALL multiply
    HLT

multiply:
    LD A
    SUB B
    JNC skip_swap ; If A>B swap
TMP=$0x8002
    LD A
    ST TMP
    LD B
    ST A    
    LD TMP
    ST B
skip_swap:
COUNTER=$0x8002
ACC=$0x8003
    LD A       ; load first arg in to loop counter
    ST COUNTER
    LD 0       ; init acc
    ST ACC
loop:
    LD ACC
    ADD B
    ST ACC
    LD COUNTER
    SUB 1
    ST COUNTER
    JNZ loop
    LD ACC
    RET
