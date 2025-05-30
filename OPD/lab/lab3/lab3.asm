ORG 0x5B6
arr_last_ele: WORD 0x5B7
arr_length: WORD 0x5B8
result: WORD 0x5B9

Start:
    CLA
    ST result
    LD #3 ; 直接上传(прямая загрузка)
    ST arr_length
    ADD ORG
    ST arr_last_ele
    repeat:LD -(arr_last_ele)
        BEQ (z==1)
        OR (result)+
        LOOP arr_length
        JUMP repeat
    HLT ; завершение программы

arr: WORD 0D00 0000 0000