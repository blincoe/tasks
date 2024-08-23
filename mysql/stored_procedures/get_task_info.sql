delimiter //

create procedure get_task_info ()
    begin

    select
        task_id
        , created_at
        , updated_at
        , user_name
        , task_title
        , task_description
        , trigger_date
        , status
    from tasks
    ;
    
    end //

delimiter ;
