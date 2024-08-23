delimiter //

create procedure update_user (
    updated_at datetime
    , email_address varchar(100)
    , summary_notification_preference varchar(20)
    , trigger_notification_preference varchar(20)
    , user_name varchar(100)
    )
    begin
    
    update users 
        set 
            `updated_at` = updated_at
            , `email_address` = email_address
            , `summary_notification_preference`= summary_notification_preference
            , `trigger_notification_preference` = trigger_notification_preference
    where
        `user_name` = user_name
        ;

    select
        created_at
    from users
    where
        `user_name` = user_name
        ;
    
    end //

delimiter ;
