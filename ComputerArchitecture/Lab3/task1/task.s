; big_to_little_endian for acc32
; 输入:  mem[0x80] = 32-bit big-endian 值
; 输出:  mem[0x84] = 32-bit little-endian 值
;
; 要求：
;   - 所有立即数/常量必须定义在 .data 中，用 .word
;   - load_imm 只接受地址/标签（加载 mem[标签] 到 acc）
;   - 移位、and、or 等操作数都是内存地址（不是立即数）

    .data

input_addr:     .word  0x80             ; 输入地址标签（实际值是 0x80）
output_addr:    .word  0x84             ; 输出地址标签

shift_8:        .word  8                ; 移位量 8
shift_16:       .word  16               ; 移位量 16
shift_24:       .word  24               ; 移位量 24

mask_ff:        .word  0xFF             ; 字节掩码 255

result:         .word  0x00000000       ; 累积结果（初始 0，可选）

    .text

_start:                                 ; 程序入口（可省略，但建议加标签清晰）

    ; 加载输入到 acc
    load_imm input_addr                 ; acc <- mem[input_addr] = 0x80
    load_acc                            ; acc <- mem[acc] = mem[0x80] （输入值）

    ; === byte3 (低8位) -> 高8位 (<<24) ===
    and mask_ff                         ; acc = input & 0xFF
    shiftl shift_24                     ; acc <<= mem[shift_24] = <<24
    store_addr result                   ; 保存到 result（临时累积）

    ; === byte2 (<<16) ===
    load_imm input_addr
    load_acc                            ; 重新取输入
    shiftr shift_8                      ; acc >>= 8
    and mask_ff                         ; & 0xFF
    shiftl shift_16                     ; <<= 16
    or result                           ; acc |= result
    store_addr result                   ; 更新 result

    ; === byte1 (<<8) ===
    load_imm input_addr
    load_acc
    shiftr shift_16                     ; >>= 16
    and mask_ff
    shiftl shift_8                      ; <<= 8
    or result
    store_addr result

    ; === byte0 (最低8位) ===
    load_imm input_addr
    load_acc
    shiftr shift_24                     ; >>= 24 （高8位变成低8位）
    or result                           ; 最后或上
    store_addr output_addr              ; 存到 mem[0x84]

    halt