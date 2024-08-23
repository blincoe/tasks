delimiter //

create procedure delete_task (
    task_id integer
    )
    begin
    

    delete from tasks 
    where
        `task_id` = task_id
        ;

    
    end //

delimiter ;
