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