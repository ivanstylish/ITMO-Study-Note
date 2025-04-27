### [实验三](../lab4/readme.md)/QUESTION 4

`EXPLAIN ANALYZE` 语句：
- 返回详细的执行计划和实际时间（`actual time`）和实际行数（`actual rows`）
`EXPLAIN` 语句：
- 仅显示查询的 预估执行计划（基于统计信息，不实际执行查询）。
- 显示每个步骤的预估 `cost`（成本）和 `rows`（预估行数）。

例如：
```sql
EXPLAIN ANALYZE
SELECT Н_ЛЮДИ.ОТЧЕСТВО, Н_ВЕДОМОСТИ.ИД
FROM Н_ЛЮДИ
INNER JOIN Н_ВЕДОМОСТИ ON Н_ЛЮДИ.ИД = Н_ВЕДОМОСТИ.ЧЛВК_ИД
WHERE
    Н_ЛЮДИ.ОТЧЕСТВО > 'Георгиевич'
    AND (Н_ВЕДОМОСТИ.ЧЛВК_ИД < 117219 OR Н_ВЕДОМОСТИ.ЧЛВК_ИД = 117219);
```
结果：
```
 QUERY PLAN                                           
------------------------------------------------------------------------------------------------------------------------------------------------
 Hash Join  (cost=676.10..5510.22 rows=18229 width=24) (actual time=5.713..22.841 rows=18601 loops=1)
   Hash Cond: ("Н_ВЕДОМОСТИ"."ЧЛВК_ИД" = "Н_ЛЮДИ"."ИД")
   ->  Bitmap Heap Scan on "Н_ВЕДОМОСТИ"  (cost=483.96..5209.29 rows=41410 width=8) (actual time=1.859..10.985 rows=42332 loops=1)
         Recheck Cond: (("ЧЛВК_ИД" < 117219) OR ("ЧЛВК_ИД" = 117219))
         Heap Blocks: exact=1553
         ->  BitmapOr  (cost=483.96..483.96 rows=41422 width=0) (actual time=1.659..1.660 rows=0 loops=1)
               ->  Bitmap Index Scan on "ВЕД_ЧЛВК_FK_IFK"  (cost=0.00..458.47 rows=41357 width=0) (actual time=1.644..1.644 rows=42301 loops=1)
                     Index Cond: ("ЧЛВК_ИД" < 117219)
               ->  Bitmap Index Scan on "ВЕД_ЧЛВК_FK_IFK"  (cost=0.00..4.78 rows=65 width=0) (actual time=0.012..0.013 rows=31 loops=1)
                     Index Cond: ("ЧЛВК_ИД" = 117219)
   ->  Hash  (cost=163.97..163.97 rows=2253 width=24) (actual time=3.797..3.799 rows=2251 loops=1)
         Buckets: 4096  Batches: 1  Memory Usage: 158kB
         ->  Seq Scan on "Н_ЛЮДИ"  (cost=0.00..163.97 rows=2253 width=24) (actual time=0.016..3.291 rows=2251 loops=1)
               Filter: (("ОТЧЕСТВО")::text > 'Георгиевич'::text)
               Rows Removed by Filter: 2867
 Planning Time: 1.423 ms
 Execution Time: 24.067 ms
 ```


- результат
```
QUERY PLAN                                              
------------------------------------------------------------------------------------------------------------------------------------------
 Hash Join  (cost=661.45..5392.05 rows=18234 width=24) (actual time=5.503..21.373 rows=18601 loops=1)
   Hash Cond: ("Н_ВЕДОМОСТИ"."ЧЛВК_ИД" = "Н_ЛЮДИ"."ИД")
   ->  Bitmap Heap Scan on "Н_ВЕДОМОСТИ"  (cost=469.32..5091.09 rows=41422 width=8) (actual time=1.770..10.061 rows=42332 loops=1)
         Recheck Cond: ("ЧЛВК_ИД" <= 117219)
         Heap Blocks: exact=1553
         ->  Bitmap Index Scan on "ВЕД_ЧЛВК_FK_IFK"  (cost=0.00..458.96 rows=41422 width=0) (actual time=1.578..1.579 rows=42332 loops=1)
               Index Cond: ("ЧЛВК_ИД" <= 117219)
   ->  Hash  (cost=163.97..163.97 rows=2253 width=24) (actual time=3.685..3.687 rows=2251 loops=1)
         Buckets: 4096  Batches: 1  Memory Usage: 158kB
         ->  Seq Scan on "Н_ЛЮДИ"  (cost=0.00..163.97 rows=2253 width=24) (actual time=0.012..3.220 rows=2251 loops=1)
               Filter: (("ОТЧЕСТВО")::text > 'Георгиевич'::text)
               Rows Removed by Filter: 2867
 Planning Time: 1.390 ms
 Execution Time: 22.575 ms
```

当没有索引时，数据库可能更倾向于使用`Hash Join`或`Merge Join`，尤其是当表的数据量较大时。`Nested Loops Join`适用于小表驱动大表的情况

1. Индексы 索引
**Индексы SQL** 索引 - список всех значений в группе из одного или нескольких столбцов, упорядоченный в некотором приемлемом для данного типа данных смысле (например, в порядке возрастания для чисел или в алфавитном порядке для символьных строк).  
**SQL 索引** 索引是一组一列或多列中所有值的列表，以给定数据类型可接受的方式排序（例如，数字按升序排列，字符串按字母顺序排列。   
```sql
CREATE INDEX idx_name ON table_name (column_name);
```
```sql
-- 为已存在的表创建索引
ALTER TABLE employees
ADD INDEX idx_age (age);
-- idx_age 索引名, age 列名
```
- `CREATE INDEX` - команда для создания индекса.
- `idx_name` - имя создаваемого индекса.
- `table_name` - имя таблицы, для которой создается индекс.
- `column_name` - имя столбца, по которому производится индексирование.

2. Оптимизация запросов 查询优化
Способы повышения производительности запросов:  
提高查询性能的方法:  
- Использование индексов.
- 使用索引。
- Настройка физических параметров СУБД (способ разделения пространства хранения данных, стратегии работы с транзакциями и т. д.).
- 配置 DBMS 物理参数（数据存储空间分区方法、事务处理策略等）。


3. Выбор плана выполнения запросов 选择查询执行计划
- Чтобы выполнить SQL-запрос необходимо построить программу — план выполнения запроса.
- 要执行 SQL 查询，需要建立一个程序 - 查询执行计划。
- Таких программ может быть несколько.
- 这样的计划可以有好几个。
- Выбор окончательного, наиболее эффективного процедурного плана
- 选最后效率最高的程序计划。