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
