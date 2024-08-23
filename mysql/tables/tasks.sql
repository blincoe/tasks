create table tasks (
    task_id integer primary key auto_increment
    , created_at datetime default now()
    , updated_at datetime null
    , user_name varchar(100) not null
    , task_title varchar(280) not null
    , task_description varchar(10000) null
    , trigger_date date null
    , status varchar(20) not null
    , constraint fk_users
        foreign key (user_name)
        references users(user_name)
        on delete cascade
);
