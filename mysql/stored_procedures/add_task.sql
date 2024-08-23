delimiter //

create procedure add_task (
    user_name varchar(100)
    , task_title varchar(280)
    , task_description varchar(10000)
    , trigger_date date
    , status varchar(20)
    )
    begin
    
    insert into tasks (
        user_name
        , task_title 
        , task_description
        , trigger_date 
        , status
        ) values (
            user_name 
            , task_title
            , task_description
            , trigger_date
            , status
            )
        ;
    
    with
        cte as (
            select
                LAST_INSERT_ID() as latest_task_id
                )
            select
                task_id
                , created_at
                , updated_at
            from tasks
            join cte
                on task_id = latest_task_id
                ;
    
    end //

delimiter ;
