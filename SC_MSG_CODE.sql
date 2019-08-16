CREATE TABLE SC_MSG_CODE(
   centre_id vachar2(6) not null,
   bank_no   vachar2(6) not null,
   code      vachar2(11) not null,
   lang      vachar2(2)  not null,
   name      vachar2(400) not null,
   primary key(centre_id,code,lang)
);

grant all on SC_MSG_CODE to public;

CREATE TABLE SC_CODE_COUNT(
   code      vachar2(11) not null,
   cnt       int  not null,
   primary key(code)
);

grant all on SC_CODE_COUNT to public;

