-- 检查数据库是否已存在，如果存在则删除
DROP DATABASE IF EXISTS mybase;

-- 创建数据库
CREATE DATABASE mybase;

-- 切换到新创建的数据库
\c mybase

-- 创建学生表
CREATE TABLE IF NOT EXISTS STUDENTS (
    STUD_ID integer,
    STUD_NAME text,
    BIRTH_DATE date
);

-- 添加学生组字段到学生表
ALTER TABLE IF EXISTS STUDENTS ADD COLUMN IF NOT EXISTS STUD_GROUP text;

-- 插入学生数据
INSERT INTO STUDENTS (STUD_ID, STUD_NAME, BIRTH_DATE, STUD_GROUP)
VALUES (407959, 'JIAJUN ZHONG', '02/01/2005', 'P3110')
ON CONFLICT (STUD_ID) DO NOTHING;

-- 查询所有学生数据
SELECT * FROM STUDENTS;  

-- 最终展现效果
 stud_id |  stud_name   | birth_date | stud_group  
---------+--------------+------------+------------  
  407959 | JIAJUN ZHONG | 2005-01-02 | P3110  
(1 行记录)  

