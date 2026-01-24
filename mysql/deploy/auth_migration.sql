-- Authentication Migration
-- Adds password-based authentication support

-- 1. Add password_hash column to users table
ALTER TABLE users ADD COLUMN password_hash varchar(255) null;

-- 2. Drop and recreate modified stored procedures
DROP PROCEDURE IF EXISTS add_user;
DROP PROCEDURE IF EXISTS get_user_info;
DROP PROCEDURE IF EXISTS set_password;

-- 3. Recreate add_user with password_hash support
delimiter //

create procedure add_user (
    _user_name varchar(100)
    , _email_address varchar(100)
    , _summary_notification_preference varchar(20)
    , _trigger_notification_preference varchar(20)
    , _closed_task_display_count_preference int
    , _password_hash varchar(255)
    )
    begin

    insert into users (
        user_name
        , email_address
        , summary_notification_preference
        , trigger_notification_preference
        , closed_task_display_count_preference
        , password_hash
        ) values (
            _user_name
            , _email_address
            , _summary_notification_preference
            , _trigger_notification_preference
            , _closed_task_display_count_preference
            , _password_hash
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

-- 4. Recreate get_user_info with password_hash support
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
        , closed_task_display_count_preference
        , password_hash
    from users
    ;

    end //

delimiter ;

-- 5. Create new set_password procedure
delimiter //

create procedure set_password (
    _user_name varchar(100)
    , _password_hash varchar(255)
    , _updated_at datetime
    )
    begin

    update users
        set
            password_hash = _password_hash
            , updated_at = _updated_at
    where
        user_name = _user_name
        ;

    end //

delimiter ;
