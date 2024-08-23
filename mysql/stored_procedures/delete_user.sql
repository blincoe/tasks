delimiter //

create procedure delete_user (
    _user_name varchar(100)
    )
    begin
    

    delete from users 
    where
        user_name = _user_name
        ;

    
    end //

delimiter ;
