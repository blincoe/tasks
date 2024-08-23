delimiter //

create procedure update_user (
    _updated_at datetime
    , _email_address varchar(100)
    , _summary_notification_preference varchar(20)
    , _trigger_notification_preference varchar(20)
    , _closed_task_display_count_preference int
    , _user_name varchar(100)
    )
    begin
    
    update users 
        set 
            updated_at = _updated_at
            , email_address = _email_address
            , summary_notification_preference = _summary_notification_preference
            , trigger_notification_preference = _trigger_notification_preference
            , closed_task_display_count_preference = _closed_task_display_count_preference
    where
        user_name = _user_name
        ;

    select
        created_at
    from users
    where
        user_name = _user_name
        ;
    
    end //

delimiter ;
