delimiter //

create procedure add_task (
    _user_name varchar(100)
    , _task_title varchar(280)
    , _task_description varchar(10000)
    , _trigger_date date
    , _status varchar(20)
    )
    begin
    
    insert into tasks (
        user_name
        , task_title 
        , task_description
        , trigger_date 
        , status
        ) values (
            _user_name 
            , _task_title
            , _task_description
            , _trigger_date
            , _status
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
