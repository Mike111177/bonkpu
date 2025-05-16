;init
    LD 1       
    ST $0x8000
loop:
    ST $0x8001
    LD $0x8000
    ADD $0x8001
    ST $0x8000
    LD $0x8001
    ADD $0x8000
    JNC loop
    LD $0x8000; A should be 233
    HLT