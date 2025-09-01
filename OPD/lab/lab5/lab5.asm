
; Программа асинхронного вывода данных на ВУ-1
; Вариант 10747
; Выводит строку "плохо" с последующим символом CR (0D)
; Программа начинается с адреса 232, строка хранится по адресу 5B0

ORG 232        ; Начало программы по адресу 232₁₆

START:  
        CLA             ; Очистка аккумулятора
        LD STRADDR      ; Загрузка адреса начала строки
        ST ADDR         ; Сохранение адреса начала строки
        
NEXTCH: LD IOFLAGS      ; Проверка флага готовности ВУ
        AND READY
        BEQ NEXTCH      ; Ждем, пока ВУ будет готово
        
        LD (ADDR)       ; Загрузка двух символов из памяти
        SWAB            ; Первый символ в младший байт
        AND MASK        ; Маскируем только младший байт
        OUT VU1         ; Выводим символ на ВУ-1
        CMP CRLF        ; Проверяем, не CR ли это
        BEQ EXIT        ; Если CR, выходим
        
        LD (ADDR)       ; Загрузка двух символов из памяти снова
        AND MASK        ; Маскируем только младший байт
        OUT VU1         ; Выводим символ на ВУ-1
        CMP CRLF        ; Проверяем, не CR ли это
        BEQ EXIT        ; Если CR, выходим
        
        INC ADDR        ; Увеличиваем адрес для следующей пары символов
        JUMP NEXTCH     ; Переходим к следующим символам
        
EXIT:   HLT             ; Остановка программы

; Данные программы
STRADDR:    WORD 5B0    ; Адрес начала строки
ADDR:       WORD 0      ; Текущий адрес в строке
IOFLAGS:    WORD 0FFE   ; Адрес флагов ввода-вывода
READY:      WORD 1      ; Маска для проверки готовности ВУ
MASK:       WORD 00FF   ; Маска для выделения младшего байта
CRLF:       WORD 000D   ; Символ CR (возврат каретки)
VU1:        WORD 0FFF   ; Адрес ВУ-1 для вывода

; Размещение строки "плохо" в памяти по адресу 5B0
ORG 5B0                 ; Переход к адресу строки 5B0

; ISO-8859-5 коды для символов "плохо" + CR
        WORD F0EB       ; "пл"
        WORD EEF5       ; "ох"
        WORD EE0D       ; "о" + CR
        
END START





variant 1074
ORG 5A3       ; 程序从地址5A3h开始

START:  CLA             ; 清空累加器
        LD #624         ; 加载第一个字符的地址
        ST ADDR         ; 存储当前地址

LOOP:   CLA             ; 清空累加器
        LD ADDR         ; 加载当前内存地址
        ST PTR          ; 存储到指针

        CALL READ_CHAR  ; 从内存读取字符
        ST CHAR         ; 存储字符

        CMP #0D         ; 与CR（字符串结束符）比较
        BEQ END         ; 如果是CR，结束程序

; 检查设备VU-3是否准备好
CHECK:  IN 3            ; 读取设备3的状态
        AND #40         ; 检查第6位（准备位）是否置位
        BEQ CHECK       ; 如果未准备好，继续等待

; 将字符输出到设备VU-3
        CLA             ; 清空累加器
        LD CHAR         ; 加载字符
        OUT 3           ; 输出到设备3

; 移动到下一个地址
        CLA             ; 清空累加器
        LD ADDR         ; 加载当前地址
        INC             ; 自增以获取下一个地址
        ST ADDR         ; 存储更新后的地址
        JUMP LOOP       ; 继续处理下一个字符

; 读取字符子程序
; 从PTR指向的内存位置读取字符
READ_CHAR:
        CLA             ; 清空累加器
        LD (PTR)        ; 从PTR指向的内存位置加载数据
        RET             ; 返回

END:    HLT             ; 结束程序

; 变量
ADDR:   WORD ?          ; 当前内存地址
PTR:    WORD ?          ; 间接寻址的指针
CHAR:   WORD ?          ; 当前字符

END START


变体10745
1. 程序从 VU-3 执行异步数据输入
2. 程序从地址 565 开始。 要放置的字符串位于地址 5D4。
3. 字符串必须以 KOI-8 编码显示。
4. 字符串在内存中的表示格式： ADR1: SIMV2 SIMV1 ADR2: SIMV4 SIMV3 .... STOP_SIMV。
5. 字符串输入或输出必须以字符代码 0D (CR) 结束。 停止字符是普通字符串字符，与其他字符串字符一样受内存位置规则的约束。

```asm
ORG 0x565 ;程序从地址565开始。
RES: WORD 0x5D4 ;要放置的字符串位于地址5D4。
FINISH: WORD 0x0D
TEMP: WORD ?

START:
    CLA
S1:
    IN 7
    AND #0x40
    BEQ S1
    IN 6
    ST (RES)
    ST TEMP
    CMP FINISH
    BEQ EXIT
    CLA
S2:
    IN 7
    AND #0x40
    BEQ S2
    IN 6
    SWAB
    OR TEMP
    ST (RES)
    SUB TEMP
    SWAB
    CMP FINISH
    BEQ EXIT
    LD (RES)+
    CLA
    JUMP S1
EXIT:
    LD (RES)+
    HLT
```