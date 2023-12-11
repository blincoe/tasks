create table users (
    user_name text primary key unique
    , created_at datetime default (datetime())
    , updated_at datetime null
    , email_address text not null
);

create table tasks (
    task_id integer primary key autoincrement
    , created_at datetime default (datetime())
    , updated_at datetime null
    , user_name text not null
    , title text not null
    , notes text null
    , trigger_date date null
    , status text not null
);

