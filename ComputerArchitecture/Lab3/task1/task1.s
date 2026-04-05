.data
org_value:    .word 0         ; 原始输入值
result: .word 0         ; 字节翻转后的结果
mask:   .word 0xFF      ; 字节提取掩码
s8:     .word 8         ; 移位量
s16:    .word 16
s24:    .word 24

.text
_start:
    ; 从IO读取一个32位大端整数
    load_addr 0x80
    store_addr org_value          ; 保存原值

    ; 第1步：取 bits 0-7 (LSB)，移到 bits 24-31 成为新 MSB
    load_addr org_value
    and mask                ; acc = org_value & 0xFF          (例: 0x12)
    shiftl s24              ; acc = byte0 << 24         (例: 0x12000000)
    store_addr result       ; result = 0x12000000

    ; 第2步：取 bits 8-15，移到 bits 16-23
    load_addr org_value
    shiftr s8               ; acc = org_value >> 8
    and mask                ; acc = byte1               (例: 0x34)
    shiftl s16              ; acc = byte1 << 16         (例: 0x00340000)
    or result               ; result |= 0x00340000      (例: 0x12340000)
    store_addr result

    ; 第3步：取 bits 16-23，移到 bits 8-15
    load_addr org_value
    shiftr s16              ; acc = org_value >> 16
    and mask                ; acc = byte2               (例: 0x56)
    shiftl s8               ; acc = byte2 << 8          (例: 0x00005600)
    or result               ; result |= 0x00005600      (例: 0x12345600)
    store_addr result

    ; 第4步：取 bits 24-31 (MSB)，放到 bits 0-7 成为新 LSB
    load_addr org_value
    shiftr s24              ; acc = org_value >> 24
    and mask                ; acc = byte3               (例: 0x78)
    or result               ; result |= 0x78            (例: 0x12345678)
    store_addr result

    ; 写出字节翻转后的结果
    load_addr result
    store_addr 0x84

done:
    halt