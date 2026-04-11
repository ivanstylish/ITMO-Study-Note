.data
org_value:    .word 0         ; 原始输入值 исходное входное значение
result: .word 0         ; 字节翻转后的结果 Результат переворачивания байта
mask:   .word 0xFF      ; 字节提取掩码 Маска извлечения байтов
s8:     .word 8         ; 移位量 количество смен
s16:    .word 16
s24:    .word 24

.text
_start:
    ; 从IO读取一个32位大端整数
    load_addr 0x80
    store_addr org_value          ; 存入内存变量，防止多次读取端口导致数据耗尽  
                                  ; Сохраним данные в переменной памяти, чтобы предотвратить исчерпание данных из-за многократного чтения с портов.

    ; 第1步：取 bits 0-7 (LSB)，移到 bits 24-31 成为新 MSB
    load_addr org_value     ; 从端口0x80读取数据
    and mask                ; acc = org_value & 0xFF          (例: 0x12)
    shiftl s24              ; acc = byte0 << 24         (例: 0x12000000)
    store_addr result       ; result = 0x12000000

    ; 第2步：取 bits 8-15，移到 bits 16-23
    load_addr org_value     ; 加载原始值
    shiftr s8               ; acc = org_value >> 8 右移8位 (s8=8)，把次低字节挪到最右边
    and mask                ; acc = byte1  和0xFF做与运算，切断高位的所有干扰        
    shiftl s16              ; acc = byte1 << 16  左移16位 (s16=16)，把它送到目标位置  
    or result               ; result |= 0x00340000  与之前保存的中间结果合并  (例: 0x12340000)
    store_addr result       ; 更新结果

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
    and mask                ; acc = byte3              
    or result               ; result |= 0x78            
    store_addr result

    ; 写出字节翻转后的结果
    load_addr result
    store_addr 0x84

done:
    halt