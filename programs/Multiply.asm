; init 9x16
LD 9
ST $0x8000
LD 16
ST $0x8001

; load first arg in to loop counter
LD $0x8000
ST $0x8002

; init acc
LD 0
ST $0x8003

loop:
LD $0x8003
ADD $0x8001
ST $0x8003
LD $0x8002
SUB 1
ST $0x8002
JNZ loop
LD $0x8003
HLT