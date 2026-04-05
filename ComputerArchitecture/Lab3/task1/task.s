; big_to_little_endian.acc32 - 只读一次输入 + 正确存储到 0x84
; 使用 load_imm 把地址作为立即加载到 acc，然后 load_acc 读 mem[acc]

.data
; 将变量放在数据段，并确保它们有明确的初始值
temp_input:     .word  0
temp_res:       .word  0
mask_ff:        .word  0x000000FF
shamt8:         .word  8
shamt16:        .word  16
shamt24:        .word  24

    .text
_start:
    ; 1. 读取输入：直接加载地址 0x80
    load_imm 0x80          ; acc = 0x80
    load_acc               ; acc = mem[0x80] (即 0x12345678)
    store_addr temp_input  ; 安全备份

    ; 2. 提取 Byte 0 (最低位) 并左移 24 位
    and mask_ff            ; acc = 0x00000078
    shiftl shamt24         ; acc = 0x78000000
    store_addr temp_res

    ; 3. 提取 Byte 1 并左移 16 位
    load_addr temp_input
    shiftr shamt8          ; 算术右移，可能带符号
    and mask_ff            ; 强制清空符号扩展的高位
    shiftl shamt16
    or temp_res
    store_addr temp_res

    ; 4. 提取 Byte 2 并左移 8 位
    load_addr temp_input
    shiftr shamt16
    and mask_ff
    shiftl shamt8
    or temp_res
    store_addr temp_res

    ; 5. 提取 Byte 3 (最高位) 并移至最低位
    load_addr temp_input
    shiftr shamt24
    and mask_ff            ; 清理
    or temp_res            ; 此时 acc = 0x78563412

    ; 6. 输出到 0x84
    store_addr 0x84
    halt