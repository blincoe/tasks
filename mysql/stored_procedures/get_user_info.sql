delimiter //

create procedure get_user_info ()
    begin

    select
        user_name
        , created_at
        , updated_at
        , email_address
        , summary_notification_preference
        , trigger_notification_preference
    from users
    ;
    
    end //

delimiter ;
