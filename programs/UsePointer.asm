; Store
    LD 0x80
    ST $0x8000
    ST $0x8001
    LD 77
    ST #0x8000
; blank
    LD 0
; Retrieve
    LD 0x80
    ST $0x8000
    ST $0x8001
    LD #0x8000
; End
    HLT