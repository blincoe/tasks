delimiter //

create procedure add_user (
    _user_name varchar(100)
    , _email_address varchar(100)
    , _summary_notification_preference varchar(20)
    , _trigger_notification_preference varchar(20)
    , _closed_task_display_count_preference int
    )
    begin
    
    insert into users (
        user_name
        , email_address
        , summary_notification_preference
        , trigger_notification_preference
        , closed_task_display_count_preference
        ) values (
            _user_name
            , _email_address
            , _summary_notification_preference
            , _trigger_notification_preference
            , _closed_task_display_count_preference
            )
        ;
    
        select
            created_at
            , updated_at
        from users
        where
            user_name = _user_name
            ;
    
    end //

delimiter ;
