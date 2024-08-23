delimiter //

create procedure add_user (
    user_name varchar(100)
    , email_address varchar(100)
    , summary_notification_preference varchar(20)
    , trigger_notification_preference varchar(20)
    )
    begin
    
    insert into users (
        user_name
        , email_address
        , summary_notification_preference
        , trigger_notification_preference
        ) values (
            user_name
            , email_address
            , summary_notification_preference
            , trigger_notification_preference
            )
        ;
    
        select
            created_at
            , updated_at
        from users
        where
            `user_name` = user_name
            ;
    
    end //

delimiter ;
