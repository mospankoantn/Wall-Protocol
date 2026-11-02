if(!wp_active())exit;
if(!instance_exists(target)){instance_destroy();exit;}
array_push(trail,[x,y]);if(array_length(trail)>8)array_delete(trail,0,1);
var _step=flight_speed*wp_dt(),_tx=target.x,_ty=target.y-14;
image_angle=point_direction(x,y,_tx,_ty)-45;
if(point_distance(x,y,_tx,_ty)<=_step+6) {
    var _damage=global.towers[shot_kind].damage*shot_power;
    wp_fx(_tx,_ty,3,[global.col.gold,global.col.purple,global.col.teal][shot_kind],[20,40,26][shot_kind]);
    if(shot_kind==1) {
        var _victims=[];var _radius=58+(tower_level-1)*7;
        with(obj_enemy)if(point_distance(x,y,other.target.x,other.target.y)<=_radius)array_push(_victims,id);
        for(var _i=0;_i<array_length(_victims);++_i)wp_damage(_victims[_i],_damage);
        wp_fx(_tx,_ty,1,global.col.purple,_radius);
    } else {
        if(shot_kind==2){target.slow_factor=max(.42,.6-(tower_level-1)*.07);target.slow_t=1.7+(tower_level-1)*.35;wp_fx(_tx,_ty,0,global.col.teal,20);}
        wp_damage(target,_damage);
    }
    instance_destroy();
} else {
    var _dir=point_direction(x,y,_tx,_ty);x+=lengthdir_x(_step,_dir);y+=lengthdir_y(_step,_dir);
}
