delimiter //

create procedure update_task (
    task_title varchar(280)
    , task_description varchar(10000)
    , trigger_date date
    , status varchar(20)
    , updated_at datetime
    , task_id integer
    )
    begin
    
    update tasks 
        set 
            `task_title` = task_title
            , `task_description` = task_description
            , `trigger_date`= trigger_date
            , `status` = status
            , `updated_at` = updated_at
    where
        `task_id` = task_id
        ;

    select
        created_at, 
        user_name
    from tasks
    where
        `task_id` = task_id
        ;
    
    end //

delimiter ;
