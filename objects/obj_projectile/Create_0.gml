if(!variable_instance_exists(id,"shot_kind"))shot_kind=0;
if(!variable_instance_exists(id,"target"))target=noone;
if(!variable_instance_exists(id,"shot_power"))shot_power=1;
if(!variable_instance_exists(id,"tower_level"))tower_level=1;
sprite_index=[spr_arrow,spr_orb,spr_shard][shot_kind];image_speed=0;depth=-900;
flight_speed=[620,390,500][shot_kind];
