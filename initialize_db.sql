create table users (
    user_name text primary key unique
    , created_at datetime default (datetime())
    , updated_at datetime null
    , email_address text not null
    , summary_notification_preference text not null
    , trigger_notification_preference text not null
);

create table tasks (
    task_id integer primary key autoincrement
    , created_at datetime default (datetime())
    , updated_at datetime null
    , user_name text not null
    , task_title text not null
    , task_description text null
    , trigger_date date null
    , status text not null
    , constraint fk_users
        foreign key (user_name)
        references users(user_name)
        on delete cascade
);
