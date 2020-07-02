#create database lab3;

use lab3;

create table bank (
	bankname	VARCHAR(20)		not null,
	city		VARCHAR(20)		not null,
	money		DOUBLE			not null,
	constraint PK_BANK primary key (bankname)
);
INSERT INTO bank VALUES('合肥分行','合肥',10000000);
INSERT INTO bank VALUES('北京分行','北京',20000000);
INSERT INTO bank VALUES('上海分行','上海',30000000);

create table department (
	departID		CHAR(4)			not null,
    departname		VARCHAR(20)		not null,
    departtype		VARCHAR(15),
    manager			CHAR(18)		not null,
    bank			VARCHAR(20)		not null,
    constraint PK_DEPARTMENT primary key (departID),
	Constraint FK_BANK_DEPART Foreign Key(bank) References bank(bankname)
);
INSERT INTO department VALUES('0001','部门1',null,'333333333333333333','上海分行');
INSERT INTO department VALUES('0002','部门2',null,'444444444444444444','上海分行');
INSERT INTO department VALUES('0003','部门1',null,'555555555555555555','北京分行');
INSERT INTO department VALUES('0004','部门2',null,'666666666666666666','北京分行');
INSERT INTO department VALUES('0005','部门1',null,'777777777777777777','合肥分行');
INSERT INTO department VALUES('0006','部门2',null,'888888888888888888','合肥分行');


create table employee (
	empID			CHAR(18)		not null,
    empname			VARCHAR(20)		not null,
    empphone		CHAR(11),
    empaddr			VARCHAR(50),
    emptype			CHAR(1),
    empstart		DATE			not null,
    depart			CHAR(4),
    constraint PK_EMPLOYEE primary key (empID),
	Constraint FK_DEPART_EMP Foreign Key(depart) References department(departID),
	Constraint CK_EMPTYPE Check(emptype IN ('0','1'))
);
INSERT INTO employee VALUES('333333333333333333','1',null,null,null,'2020-6-1','0001');
INSERT INTO employee VALUES('444444444444444444','2',null,null,null,'2020-6-1','0001');
INSERT INTO employee VALUES('555555555555555555','3',null,null,null,'2020-6-1','0002');
INSERT INTO employee VALUES('666666666666666666','4',null,null,null,'2020-6-1','0002');
INSERT INTO employee VALUES('777777777777777777','5',null,null,null,'2020-6-1','0003');
INSERT INTO employee VALUES('888888888888888888','6',null,null,null,'2020-6-1','0003');

create table customer (
	cusID			CHAR(18)		not null,
	cusname			VARCHAR(10)		not null,
	cusphone		CHAR(11)		not null,
	address			VARCHAR(50),
	contact_phone	CHAR(11)		not null,
	contact_name	VARCHAR(10)		not null,
	contact_Email	VARCHAR(20),
	relation		VARCHAR(10)		not null,
    loanres			CHAR(18),
    accres			CHAR(18),
	constraint PK_CUSTOMER primary key (cusID),
    Constraint FK_CUS_LOANRES Foreign Key(loanres) References employee(empID),
    Constraint FK_CUS_ACCRES Foreign Key(accres) References employee(empID)
);
INSERT INTO customer VALUES('123456789123456789','ljy','12345678910','earth','10987654321','yl','123@126.com','mather',null,null);

create table accounts(
	accountID		CHAR(6)			not null,
	money			DOUBLE			not null,
    settime			DATETIME,
	accounttype		VARCHAR(10),
	constraint PK_ACC primary key (accountID),
	Constraint CK_ACCOUNTTYPE Check(accounttype IN ('储蓄账户','支票账户'))
);

create table saveacc (
	accountID		CHAR(6)			not null,
    interestrate	float,
    savetype		CHAR(1),
    constraint PK_SAVEACC primary key (accountID),
	Constraint FK_SAVE_ACC Foreign Key(accountID) References accounts(accountID) On Delete Cascade
);

create table checkacc (
	accountID		CHAR(6)			not null, 
    overdraft		DOUBLE,
    constraint PK_CHECKACC primary key (accountID),
	Constraint FK_CHECK_ACC Foreign Key(accountID) References accounts(accountID) On Delete Cascade
);

create table cusforacc (
	accountID		CHAR(6)			not null,
    bank			VARCHAR(20),
    cusID			CHAR(18)		not null,
    visit			DATETIME,
    accounttype		VARCHAR(10),
    constraint PK_CUSACC primary key (accountID, cusID),
    Constraint FK_BANK_ACCOUT Foreign Key(bank) References bank(bankname),
    Constraint FK_CUS Foreign Key(cusID) References customer(cusID),
	Constraint FK_CUS_ACC Foreign Key(accountID) References accounts(accountID) On Delete Cascade,
    Constraint UK Unique Key(bank, cusID, accounttype)
);

create table loan (
	loanID			CHAR(4)			not null,
    money			DOUBLE,
    bank			VARCHAR(20),
    state			CHAR(1)			default '0',
    constraint PK_LOAN primary key (loanID),
	Constraint FK_BANK_LOAN Foreign Key(bank) References bank(bankname)
);
select cusID from cusforloan where loanID='0001';
select * from loan;
create table cusforloan (
	loanID			CHAR(4),
    cusID			CHAR(18),
    constraint PK_CUSLOAN primary key (loanID, cusID),
    Constraint FK_LOAN Foreign Key(loanID) References loan(loanID) On Delete Cascade,
    Constraint FK_CUSL Foreign Key(cusID) References customer(cusID)
);
select * from cusforloan;
create table payinfo (
	loanID			CHAR(4),
    cusID			CHAR(18),
    money			DOUBLE,
    paytime			DATETIME,
    constraint PK_PAYINFO primary key (loanID, cusID, money, paytime),
    Constraint FK_PAY_LOAN Foreign Key(loanID) References loan(loanID) On Delete Cascade,
    Constraint FK_PAY_CUS Foreign Key(cusID) References customer(cusID)
);  

create view checkaccounts
as select accounts.accountID,bank,accounttype,money,settime,overdraft 
from accounts,checkacc,(select distinct accounts.accountID,bank from accounts,cusforacc where accounts.accountID=cusforacc.accountID) tmp 
where accounts.accountID=checkacc.accountID and accounts.accountID=tmp.accountID;

create view saveaccounts (accountID,bank,accounttype,money,settime,interestrate,savetype)
as select accounts.accountID,bank,accounttype,money,settime,interestrate,savetype
from accounts,saveacc,(select distinct accounts.accountID,bank from accounts,cusforacc where accounts.accountID=cusforacc.accountID) tmp 
where accounts.accountID=saveacc.accountID and accounts.accountID=tmp.accountID;
select * from checkstat;
create view checkstat (bank, totalmoney,totalcustomer)
as select t1.bank,totalmoney,totalcustomer 
from (select bank,sum(money) as totalmoney from checkaccounts group by bank) t1, 
(select bank,count(distinct cusID) as totalcustomer from cusforacc where accounttype='支票账户' group by bank) t2
where t1.bank=t2.bank;

create view savestat (bank, totalmoney,totalcustomer)
as select t1.bank,totalmoney,totalcustomer 
from (select bank,sum(money) as totalmoney from saveaccounts group by bank) t1, 
(select bank,count(distinct cusID) as totalcustomer from cusforacc where accounttype='储蓄账户' group by bank) t2
where t1.bank=t2.bank;

create view loanstat (bank, totalmoney,totalcustomer)
as select t1.bank,totalmoney,totalcustomer 
from (select bank,sum(money) as totalmoney from loan group by bank) t1, 
(select bank, count(distinct cusID) as totalcustomer 
from loan,cusforloan where loan.loanID=cusforloan.loanID group by bank) t2
where t1.bank=t2.bank;


DELIMITER $
create trigger loanDelete
Before delete on loan
for each row
begin
	declare a int;
	select state into a from loan where old.loanID=loan.loanID;
    if a = 1 then
		signal sqlstate 'HY000' set message_text = '贷款发放中';
	end if;
end $
DELIMITER ;


DELIMITER $
create trigger loanState
After insert on payinfo
for each row
begin
	declare pay int;
    declare total int;
	select sum(money) into pay from payinfo where payinfo.loanID=new.loanID;
    select money into total from loan where loan.loanID=new.loanID;
    if pay > 0 and pay < total then
		update loan set state='1' where loan.loanID=new.loanID;
	elseif pay=total then
		update loan set state='2' where loan.loanID=new.loanID;
	elseif pay>total then
		delete from payinfo where payinfo.loanID=new.loanID and payinfo.cusID=new.cusID and payinfo.paytime=new.paytime and payinfo.money=new.money;
		signal sqlstate 'HY001' set message_text = '超出贷款金额';
	end if;
end $
DELIMITER ;

 SHOW TRIGGERS;
 
