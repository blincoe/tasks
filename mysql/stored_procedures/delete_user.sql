delimiter //

create procedure delete_user (
    user_name varchar(100)
    )
    begin
    

    delete from users 
    where
        `user_name` = user_name
        ;

    
    end //

delimiter ;
