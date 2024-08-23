delimiter //

create procedure update_task (
    _task_title varchar(280)
    , _task_description varchar(10000)
    , _trigger_date date
    , _status varchar(20)
    , _updated_at datetime
    , _task_id integer
    )
    begin
    
    update tasks 
        set 
            task_title = _task_title
            , task_description = _task_description
            , trigger_date= _trigger_date
            , status = _status
            , updated_at = _updated_at
    where
        task_id = _task_id
        ;

    select
        created_at, 
        user_name
    from tasks
    where
        task_id = _task_id
        ;
    
    end //

delimiter ;
