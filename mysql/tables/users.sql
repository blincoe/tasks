create table users (
    user_name varchar(100) primary key unique
    , created_at datetime default now()
    , updated_at datetime null
    , email_address varchar(100) not null
    , summary_notification_preference varchar(20) not null
    , trigger_notification_preference varchar(20) not null
    , closed_task_display_count_preference int not null
    , password_hash varchar(255) null
);
