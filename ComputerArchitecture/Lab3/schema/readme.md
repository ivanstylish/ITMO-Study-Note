### 关于 RISC-IV 架构的电路原理图学习指南
 
![](./risc_iv_schema_v2.drawio.png)
 
在单周期架构中，所有指令都会经历标准的五个阶段（在同一个时钟周期内并行完成）：IF（取指） $\rightarrow$ ID（译码） $\rightarrow$ EX（执行） $\rightarrow$ MEM（访存） $\rightarrow$ WB（写回）。
 
В однотактной архитектуре все инструкции проходят пять стандартных стадий параллельно в течение одного тактового цикла: IF (выборка) → ID (декодирование) → EX (исполнение) → MEM (обращение к памяти) → WB (запись результата).
 
---
 
#### 总线 / Шины
 
- **数据总线**（Reg File ↔ ALU ↔ MEM）32 bit — **Шина данных**: фактическая передача данных между процессором, памятью и периферией.
- **地址总线**（PC → ALU → Addr Decoder）32 bit — **Шина адреса**: указывает источник или место назначения данных. В новой схеме отображается штрихпунктирной линией.
- **立即数**（Sign Extend 12b → 32 bit 输出）— **Непосредственное значение**: 12-битное поле инструкции, знакорасширенное до 32 бит.
- **ALUOp 控制信号** ≈ 4 bit（11 种操作）— **Управляющий сигнал ALUOp**: определяет, какую операцию выполнить АЛУ.
- **MemToReg / RegWrite / ALUSrc / Branch / Jump / JR / MemW·R / halt** — по 1–2 bit каждый, все показаны красной пунктирной линией.
**总线协同工作 / Взаимодействие шин**：地址总线首先工作（PC 或 ALU 给出地址），Control Unit 随即发出控制信号，最后数据总线完成数据传送。MUX（多路复用器）的作用是根据控制信号从多个输入中选择其中一路输出。Шина адреса работает первой (PC или ALU формируют адрес), затем Control Unit выдаёт управляющие сигналы, после чего шина данных переносит данные. Мультиплексор (MUX) выбирает один из нескольких входных сигналов согласно управляющей команде.
 
---
 
#### 各模块功能说明 / Описание модулей
 
- `PC (Program Counter)`：保存当前正在执行指令的 32 位内存地址。每个时钟周期结束时，从 MUX next PC（3 输入）接收下一条指令的地址并写回。PC 同时向三路并行输出：opcode、rs1/rs2/rd、imm[11:0]，分别进入 Control Unit、Register File 和 Sign Extend（指令存储器在图外，未画出）。箭头方向：进口来自 MUX next PC，出口向右并行送出三条字段线。
  32-битный регистр текущего адреса инструкции. По завершении такта принимает следующий адрес от MUX next PC (3-входной). Параллельно выдаёт три поля: opcode → Control Unit, rs1/rs2/rd → Register File, imm[11:0] → Sign Extend (память инструкций — внешняя, на схеме не показана). Вход — от MUX next PC, выходы — три параллельные линии вправо.
- `PC+4 / PC+offset (branch / jal target)`：两个并行加法器，同一周期内同时运算。**PC+4**：将 PC 值加 4，得到顺序下一条指令地址（无跳转时使用）。**PC+offset**：将 PC 与来自 Sign Extend 的 32 位 offset 相加，得到分支/JAL 跳转目标地址。两路结果均送 MUX next PC 的不同输入端。
  Два параллельных сумматора. PC+4: следующий последовательный адрес. PC+offset: PC + 32-битное смещение от Sign Extend → целевой адрес ветвления/JAL. Оба результата подаются на MUX next PC.
- `MUX next PC (3-in)`：三输入多路选择器，由 Control Unit 的 Branch/Jump/JR [2b] 信号控制：sel=00 选 PC+4（顺序执行）；sel=01 选 PC+offset（条件分支成立，需 zero flag 配合）；sel=10 选 PC+offset 或 rs1（无条件跳转 j/jal，或寄存器跳转 jr——ALU 输出 rs1 走左侧专用通道进入第三输入）。输出写回 PC，完成取指环路。
  Трёхвходной мультиплексор. sel=00: PC+4; sel=01: PC+offset (при выполнении условия ветвления + zero flag); sel=10: PC+offset или rs1 (j/jal/jr). Выход записывается в PC.
- `Control Unit`：整个处理器的译码与控制中枢。接收 opcode [7b] 进行组合逻辑译码，同步输出 8 路控制信号（图中均为红色虚线）：ALUSrc → MUX src2；ALUOp → ALU；MemW/R → Addr Decoder；MemToReg/RegWrite → MUX WB；Branch/Jump/JR → MUX next PC；halt → HALT 端口。同时接收 ALU 的 zero flag 反馈，用于判断条件分支（beqz: rs1==0？bgt: rs1>rs2？）是否成立。opcode 从左侧进入，所有控制信号从右侧/下方发出。
  Центральный декодер. Принимает opcode [7b], через комбинационную логику выдаёт 8 управляющих сигналов (красные пунктиры): ALUSrc, ALUOp, MemW/R, MemToReg/RegWrite, Branch/Jump/JR, halt. Также принимает zero flag от ALU для оценки условий ветвления.
- `Register File 32×32b`：32 个 32 位通用寄存器（x0–x31），x0 硬接线恒为 0。支持两路并行读（rs1→A 端口，rs2→B 端口）和一路写（WD 端口，由 RegWrite 使能）。读操作为纯组合逻辑（无延迟），写操作在时钟上升沿触发。**A [32b]** 送 ALU 作第一操作数；**B [32b]** 同时送 MUX src2（R 型第二操作数）和 Memory Subsystem（sw/sb 写入数据，走专用线 B(sw/sb data) [32b]）。写回数据 WD 来自 MUX WB。
  32 регистра по 32 бит; x0 аппаратно равен 0. Два порта чтения (rs1→A, rs2→B), один порт записи (WD, при RegWrite=1, по фронту такта). A → ALU; B → MUX src2 и Memory Subsystem (линия B(sw/sb data) [32b]). WD — от MUX WB.
- `Sign Extend 12b`：将指令中 12 位立即数字段符号扩展至 32 位（imm[11]=1 则高 20 位填 1，否则填 0）。输出同时送往两处：**imm [32b]** 线送 MUX src2（I 型/S 型指令的 ALU 第二操作数）；**offset [32b]** 线向上送回 IF 区域的 PC+offset 加法器（分支/跳转偏移量）。这是 ID 区域唯一向上反向传递数据的路径。
  Знакорасширяет 12-битное imm до 32 бит. Выход: линия imm [32b] → MUX src2; линия offset [32b] → сумматор PC+offset в зоне IF. Единственный поток данных, идущий из ID обратно в IF.
- `MUX WB`：写回阶段的最终选择器，位于 ID 区域内（输出直接写回 Register File）。MemToReg=0 时选 ALU result（R 型和 I 型运算指令）；MemToReg=1 时选 MemRD（来自 MEM 区域 MUX MemRD 的统一读出信号，用于 lw 加载指令）。RegWrite=1 时经 WD(write-back) [32b] 线写入 Register File；sw/sb 指令时 RegWrite=0，输出被忽略。
  Итоговый мультиплексор записи. MemToReg=0: результат ALU (R/I-инструкции); MemToReg=1: MemRD (от MUX MemRD, для lw). При RegWrite=1 → запись WD в RegFile; при RegWrite=0 (sw/sb) — игнорируется.
- `MUX src2`：选择 ALU 第二操作数，区分 R 型与 I/S 型指令。ALUSrc=0（Control Unit 输出）选寄存器 B（R 型：两个寄存器操作数，如 `add rd,rs1,rs2`）；ALUSrc=1 选立即数 imm（I 型：`addi/lw`；S 型：`sw/sb` 地址计算）。图中为菱形，B [32b] 从左上进，imm [32b] 从右上进，src2 [32b] 从下方输出进入 ALU。
  Выбор второго операнда ALU. ALUSrc=0: регистр B (R-тип); ALUSrc=1: imm (I/S-тип). Ромб: B — слева-сверху, imm — справа-сверху, src2 — снизу в ALU.
- `ALU`：计算核心，支持 11 种操作（ALUOp 4 位选择）：算术——add、sub、mul、div、rem；移位——sll、srl、sra；逻辑——and、or、xor。同时输出：**result [32b]** 送 MUX WB（R/I 运算写回）；**addr [32b]**（点划线）送 Memory Subsystem 的 Addr Decoder（lw/sw 地址）；**zero flag [1b]**（红色虚线）送回 Control Unit（条件分支判断，result==0 时为 1）。A [32b] 从左进，src2 从上进，result 从右出，addr 走点划线向右送 MEM。
  Вычислительное ядро, 11 операций (ALUOp): add, sub, mul, div, rem, sll, srl, sra, and, or, xor. Выходы: result [32b] → MUX WB; addr [32b] (штрихпунктир) → Addr Decoder; zero flag [1b] (красный пунктир) → Control Unit.
- `Addr Decoder (Memory Subsystem)`：Memory Subsystem 的流量入口，是本次电路重画的核心改动。直接接收 ALU 的 addr [32b]、Register File 的 B(sw/sb data) [32b] 以及 Control Unit 的 MemW/R [2b]，根据地址范围分流：addr 为普通地址 → 路由到 Data Memory（读写）；addr=0x80 → 路由到 MMIO（lw 读输入值）；addr=0x84 → 路由到 MMIO（sw 写输出值）。图中为菱形，三路输入从左侧进，两路输出分别向上送 Data Memory、向下送 MMIO。
  Входной узел Memory Subsystem. Принимает addr, B-данные и MemW/R; маршрутизирует: обычный адрес → Data Memory; 0x80 → MMIO (чтение); 0x84 → MMIO (запись). Ромб: входы слева, выходы вправо (Data Memory вверх, MMIO вниз).
- `Data Memory + MMIO + MUX MemRD (Memory Subsystem)`：**Data Memory**：支持字（lw/sw）和字节（sb）访问，MemRead=1 时读出 RD，MemWrite=1 时将 B 数据写入指定地址。**MMIO**：实现 wrench 框架的内存映射 I/O——lw 从地址 0x80 读取外部输入流的下一个值（yaml 配置：`memory_mapped_io: 0x80: [n1, n2, ...]`）；sw 将结果写入地址 0x84 的输出流（可由 wrench 的 assert 机制验证，例如阶乘结果）。**MUX MemRD**：Memory Subsystem 内部汇合器，将 Data Memory 的 RD 与 MMIO 的 INPUT(0x80) 二选一，输出统一的 **MemRD [32b]** 信号，从 MEM 区域右侧走专用返回通道送 MUX WB。这是整个 Memory Subsystem 的唯一数据出口。
  Data Memory: чтение (MemRead=1) → RD; запись (MemWrite=1) → данные B по адресу. MMIO: lw читает из 0x80 (входной поток yaml); sw пишет в 0x84 (проверяется через assert). MUX MemRD: объединяет RD и INPUT(0x80) → единый сигнал MemRD [32b] → MUX WB (по выделенному каналу справа). Единственный выход данных из Memory Subsystem.
---
 
#### 各阶段执行流程 / Стадии выполнения
 
- `IF（取指）`：PC 给出当前地址，同时并行计算 PC+4（顺序地址）和 PC+offset（offset 来自 Sign Extend，分支/跳转目标地址）。三路结果送 MUX next PC，由 Branch/Jump/JR 控制信号和 zero flag 共同决定下一个 PC，写回 PC 完成环路。指令字段（opcode、rs1/rs2/rd、imm[11:0]）并行向下传递进入 ID 阶段。
  PC выдаёт адрес; параллельно вычисляются PC+4 и PC+offset. MUX next PC (3-in) с учётом Branch/Jump/JR и zero flag выбирает следующий PC → запись в PC. Поля инструкции (opcode, rs1/rs2/rd, imm[11:0]) параллельно передаются в стадию ID.
- `ID（译码）`：opcode 送 Control Unit 生成全部控制信号；rs1/rs2/rd 送 Register File 读出 A 和 B；imm[11:0] 经 Sign Extend 扩展至 32 位，imm [32b] 送 MUX src2，offset [32b] 向上送 PC+offset 加法器。Control Unit 同时输出 ALUSrc、ALUOp、MemW/R、MemToReg、RegWrite、Branch/Jump/JR、halt 共 8 路信号。MUX WB 也位于此区域，负责写回选择。
  opcode → Control Unit (все управляющие сигналы); rs1/rs2/rd → Register File → A, B; imm[11:0] → Sign Extend → imm[32b] → MUX src2 и offset[32b] → PC+offset. MUX WB также расположен здесь.
- `EX（执行）`：MUX src2 根据 ALUSrc 选择 B（R 型）或 imm（I/S 型）作为 ALU 的 src2。ALU 执行运算，输出 result [32b] 和 zero flag [1b]（zero flag 反馈 Control Unit 用于条件分支判断）。同时 addr [32b]（点划线）送 Memory Subsystem 的 Addr Decoder。
  MUX src2 (ALUSrc) выбирает B или imm. ALU выполняет операцию → result [32b] и zero flag [1b] (→ CU). addr [32b] (штрихпунктир) → Addr Decoder.
- `MEM（访存）`：Addr Decoder 根据 addr 分流：普通地址 → Data Memory（lw 读 RD，sw 写 B 数据）；0x80 → MMIO 读输入值；0x84 → MMIO 写输出值。MUX MemRD 将读出数据汇合为统一 MemRD [32b] 送 MUX WB。R 型/I 型计算指令此阶段 MemR=MemW=0，透传不访存。
  Addr Decoder маршрутизирует: обычный → Data Memory; 0x80 → MMIO (чтение); 0x84 → MMIO (запись). MUX MemRD → MemRD [32b] → MUX WB. Для R/I-инструкций MemR=MemW=0.
- `WB（写回，位于 ID 区域）`：MUX WB 根据 MemToReg 在 result 和 MemRD 之间选择，RegWrite=1 时经 WD(write-back) [32b] 写入 Register File 的 rd 寄存器，完成一条指令的完整执行。sw/sb 指令 RegWrite=0，不写回。
  MUX WB выбирает result или MemRD (MemToReg). При RegWrite=1 → запись WD в rd регистрового файла. Для sw/sb RegWrite=0.
---
 
#### 各类型指令具体执行流程 / Потоки выполнения по типам инструкций
 
##### R 型（add / sub / mul / div / rem / and / or / xor / sll / srl / sra）
 
```
add rd, rs1, rs2
```
 
| 阶段 / Стадия | 激活路径 / Активные пути |
|---|---|
| IF | PC → PC+4 → MUX next PC(sel=00) → PC；opcode/rs1/rs2/rd → ID |
| ID | opcode → CU：ALUSrc=0, ALUOp=操作码, RegWrite=1, MemToReg=0；rs1/rs2 → RegFile → A, B |
| EX | MUX src2(ALUSrc=0) 选 B → ALU：A op B → result；zero flag → CU（分支不使用）|
| MEM | MemR=MemW=0，透传不访存 |
| WB | MUX WB(MemToReg=0) 选 result → RegWrite=1 → 写入 rd |
 
控制信号 / Сигналы управления：`ALUSrc=0 / ALUOp=op / RegWrite=1 / MemToReg=0 / MemR=0 / MemW=0`
 
##### I 型运算（addi / lui）
 
```
addi rd, rs1, k     ; rd = rs1 + k
lui  rd, k          ; rd = k << 12
```
 
| 阶段 / Стадия | 激活路径 / Активные пути |
|---|---|
| IF | PC → PC+4 → MUX next PC(sel=00) → PC；opcode/rs1/rd/imm → ID |
| ID | opcode → CU：ALUSrc=1, ALUOp=add/lui, RegWrite=1, MemToReg=0；rs1 → RegFile → A；imm[11:0] → Sign Extend → imm[32b] → MUX src2 |
| EX | MUX src2(ALUSrc=1) 选 imm → ALU：rs1+imm（addi）或 imm<<12（lui）→ result |
| MEM | 透传不访存 |
| WB | MUX WB 选 result → RegWrite=1 → 写入 rd |
 
控制信号：`ALUSrc=1 / ALUOp=add 或 lui / RegWrite=1 / MemToReg=0 / MemR=0 / MemW=0`
 
##### lw（加载字 / Загрузка слова）
 
```
lw rd, offset(rs1)     ; rd = M[rs1 + offset]
```
 
| 阶段 / Стадия | 激活路径 / Активные пути |
|---|---|
| IF | PC → PC+4 → MUX next PC(sel=00) → PC；opcode/rs1/rd/imm → ID |
| ID | opcode → CU：ALUSrc=1, ALUOp=add, MemRead=1, MemWrite=0, RegWrite=1, MemToReg=1；rs1 → A；imm → Sign Extend → imm[32b] |
| EX | MUX src2(1) 选 imm → ALU：rs1+imm → addr（点划线送 Addr Decoder）|
| MEM | Addr Decoder 判断 addr：普通地址 → Data Memory 读出 RD → MUX MemRD；若 addr=0x80 → MMIO 读 INPUT → MUX MemRD；输出 MemRD [32b] → MUX WB |
| WB | MUX WB(MemToReg=1) 选 MemRD → RegWrite=1 → 写入 rd |
 
控制信号：`ALUSrc=1 / ALUOp=add / MemRead=1 / MemWrite=0 / MemToReg=1 / RegWrite=1`
 
##### sw（存储字 / Сохранение слова）
 
```
sw rs2, offset(rs1)    ; M[rs1 + offset] = rs2
```
 
| 阶段 / Стадия | 激活路径 / Активные пути |
|---|---|
| IF | PC → PC+4 → MUX next PC(sel=00) → PC；opcode/rs1/rs2/imm → ID（无 rd 字段）|
| ID | opcode → CU：ALUSrc=1, ALUOp=add, MemRead=0, MemWrite=1, RegWrite=0；rs1 → A；rs2 → B（写入数据）；imm → Sign Extend → imm[32b] |
| EX | MUX src2(1) 选 imm → ALU：rs1+imm → addr（点划线送 Addr Decoder）；B(sw/sb data) [32b] 走专用线直接送 Addr Decoder |
| MEM | Addr Decoder 判断 addr：普通地址 → Data Memory 写入 B（MemWrite=1）；若 addr=0x84 → MMIO 写出 OUTPUT（wrench assert 可验证）|
| WB | RegWrite=0，MUX WB 输出被忽略，不写回任何寄存器 |
 
控制信号：`ALUSrc=1 / ALUOp=add / MemRead=0 / MemWrite=1 / MemToReg=x / RegWrite=0`
 
##### B 型条件分支（beqz / bnez / bgt / ble / beq / bne）
 
```
beqz rs1, k           ; if rs1 == 0 : PC = PC + k
bgt  rs1, rs2, k      ; if rs1 > rs2 : PC = PC + k
```
 
| 阶段 / Стадия | 激活路径 / Активные пути |
|---|---|
| IF | PC 同时计算 PC+4 和 PC+offset（offset 来自 Sign Extend）；两路均送 MUX next PC 等待判决 |
| ID | opcode → CU：Branch=1, ALUSrc=0, RegWrite=0, MemR/W=0；rs1[,rs2] → A[,B]；imm → Sign Extend → offset [32b] → PC+offset |
| EX | ALU 执行比较：beqz → A-0（检测 rs1==0）；bgt → A-B（检测 rs1>rs2）→ zero flag → CU；CU 判断：条件成立 → MUX next PC sel=01 选 PC+offset；不成立 → sel=00 选 PC+4 |
| MEM | 透传不访存 |
| WB | RegWrite=0，不写回 |
 
控制信号：`Branch=1 / ALUSrc=0 / ALUOp=sub / RegWrite=0 / MemR=0 / MemW=0 / sel 由 zero flag 决定`
 
##### J 型跳转（j / jal / jr）
 
```
j   k              ; PC = PC + k
jal rd, k          ; rd = PC+4；PC = PC + k
jr  rs             ; PC = rs
```
 
| 阶段 / Стадия | 激活路径 / Активные пути |
|---|---|
| IF | PC 计算 PC+4 和 PC+offset；jr 的目标（rs1 值）由 ALU 输出走左侧专用通道进入 MUX next PC 第三输入 |
| ID | opcode → CU：Jump=1（j/jal）或 JR=1（jr）；jal 时 rd → RegFile 写端口（保存 PC+4）；RegWrite=1（jal）或 0（j/jr）|
| EX | j/jal：MUX next PC sel=10 直接选 PC+offset，ALU 不参与主运算；jr：ALU 输出 rs1（透传），走左侧专用通道进入 MUX next PC sel=10 |
| MEM | 透传不访存 |
| WB | jal：RegWrite=1，MUX WB 选 result（即 PC+4）写入 rd；j/jr：RegWrite=0 |
 
控制信号：`Jump=1 或 JR=1 / RegWrite=1(jal)/0(j,jr) / MUX next PC sel=10`
 
---


#### 答辩问题：
##### 1. RISC-IV 中的栈操作。内存分配、过程间数据传递 / risc-iv Работа со стеком. Выделение памяти, передача данных в/из процедур.

**中文**：栈通常向下增长（SP 寄存器）。分配栈帧使用 `addi sp, sp, -N`。参数可通过寄存器（A0–A7）或压栈传递，返回值通常放在 A0 中。被调用者需手动保存 callee-saved 寄存器（S* 系列）。调用使用 `jal` 指令。

**俄文**：Стек растёт вниз. Выделение: `addi sp, sp, -N`. Параметры — в регистрах A* или на стеке, возврат значения — в A0.

##### 2. 在原理图（schema）中，Nop 指令看起来如何？如何执行？/ schema Как будет выглядеть Nop и как он будет выполняться?

**中文**：Nop 通常编码为特殊 opcode（如全零或 `addi x0, x0, 0`）。在原理图中，控制单元解码后不激活 ALU、内存或写回操作，仅将 PC 增加指令长度（4 或 11 字节），不改变任何状态。执行时间为 1 个周期。

**俄文**：Nop — специальный opcode (часто все нули). Control Unit пропускает операции, только PC += размер инструкции.

##### 3. Jmp 指令在原理图中如何？如何执行？/ schema Как будет выглядеть Jmp и как он будет выполняться?

**中文**：Jmp 指令包含目标地址或偏移。在原理图中，控制单元通过多路选择器（mux）将新地址直接送入 PC，不保存返回地址。执行流程：取指 → 解码 → 更新 PC → 从新地址取下一条指令。

**俄文**：Jmp загружает новое значение в PC через mux. Нет сохранения возврата.

##### 4. Add 指令在原理图中如何？如何执行？/ schema Как будет выглядеть Add и как он будет выполняться?

**中文**：Add 指令涉及取两个操作数送入 ALU 进行加法运算，结果写回目标寄存器（或 Acc），同时更新状态标志。在原理图中路径为：取指 → 解码 → 读寄存器/内存 → ALU → 写回 + 更新标志寄存器。

**俄文**：Операнды → ALU (сложение) → запись результата + обновление флагов C/V.

##### 5. 寄存器文件内部如何工作？/ schema Как работает внутри регистровый файл?

**中文**：寄存器文件是由多个快速 SRAM 单元组成的阵列，包含读端口（通常两个）和写端口。地址解码器根据寄存器编号选择对应单元，多路复用器将数据送到数据总线，写操作由写使能（WE）信号控制，支持并行读写多个寄存器。

**俄文**：Массив SRAM с адресными портами чтения и записи. Декодер выбирает регистр, мультиплексоры выводят данные.

##### 6. 内存映射 I/O 内部如何工作？/ schema Как работает внутри Memory Mapped I/O?

**中文**：MMIO 在地址解码阶段被识别为 I/O 地址范围。当地址落在 MMIO 区间时，地址译码器激活外设控制器而非普通 RAM，通过数据总线与设备交换数据。外部看起来与内存访问完全一致，无需额外 I/O 指令。

**俄文**：Адрес декодируется в диапазон устройств. Вместо RAM активируется периферия, данные идут через общую шину.

##### 7. 控制单元（Control Unit）中是否有寄存器？/ schema Есть ли регистры в Control Unit?

**中文**：是的，控制单元通常包含以下寄存器：指令寄存器（IR，用于保存当前指令）、程序计数器（PC）、状态标志寄存器，以及可能的临时寄存器或微码状态寄存器。控制单元根据这些寄存器和指令 opcode 生成各种控制信号。

**俄文**：Да, обычно присутствуют: Instruction Register (IR), Program Counter (PC), регистры флагов и временные регистры.
