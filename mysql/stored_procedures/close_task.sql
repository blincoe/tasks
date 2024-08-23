delimiter //

create procedure close_task (
    status varchar(20)
    , updated_at datetime
    , task_id integer
    )
    begin
    

    update tasks 
        set 
            `status` = status
            , `updated_at` = updated_at
    where
        `task_id` = task_id
        ;

    select
        created_at, 
        user_name, 
        task_title, 
        task_description, 
        trigger_date
    from tasks
    where
        `task_id` = task_id
        ;
    
    end //

delimiter ;
