create database mybase;  
\c mybase  
\l  
\c postgres  
drop mybase;  
create database mybase;  
\c mybase  
mybase=# create table STUDENTS(  
mybase(# STUD_ID integer,  
mybase(# STUD_NAME text,  
mybase(# BIRTH_DATE date  
mybase(# );  
CREATE TABLE  
alter table STUDENTS add column STUD_GROUP text;  
ALTER TABLE  
select * from students;  
insert into students values (407959, 'JIAJUN ZHONG', '02/01/2005', 'P3110');  
INSERT 0 1  
select * from students;  
 stud_id |  stud_name   | birth_date | stud_group  
---------+--------------+------------+------------  
  407959 | JIAJUN ZHONG | 2005-01-02 | P3110  
(1 行记录)  
