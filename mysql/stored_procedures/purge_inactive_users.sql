delimiter //

create procedure purge_inactive_users ()
    begin
    
    set sql_safe_updates = 0;

    delete u 
    from users as u
    left join tasks t
        on u.user_name = t.user_name
    where
        t.user_name is null
        ;

    
    end //

delimiter ;
