delimiter //

create procedure close_task (
    _status varchar(20)
    , _updated_at datetime
    , _task_id integer
    )
    begin
    

    update tasks 
        set 
            status = _status
            , updated_at = _updated_at
    where
        task_id = _task_id
        ;

    select
        created_at, 
        user_name, 
        task_title, 
        task_description, 
        trigger_date
    from tasks
    where
        task_id = _task_id
        ;
    
    end //

delimiter ;
