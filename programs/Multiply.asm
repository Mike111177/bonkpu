    SEI ; init stack pointer    
    PSH 4
    PSH 6
    CALL multiply
    SI
    SI
    PSH
    PSH 9
    CALL multiply
    HLT

multiply: ;  (A = ^1, B = ^2, RET = A)
A = ^4 
B = ^5
COUNTER = ^1
    PSH
ACC = ^2
    PSH
    LD A
    CMP B
    JNC skip_swap ; If A>B swap
TMP = ^1 ; 
    ST TMP
    LD B
    ST A    
    LD TMP
    ST B
skip_swap:
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
    POP
    POP
    RET
