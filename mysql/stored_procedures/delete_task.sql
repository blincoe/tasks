delimiter //

create procedure delete_task (
    _task_id integer
    )
    begin
    

    delete from tasks 
    where
        task_id = _task_id
        ;

    
    end //

delimiter ;
