if(!wp_active())exit;
var _dt=wp_dt();walk_time+=_dt*5;hit_flash=max(0,hit_flash-_dt);
slow_t=max(0,slow_t-_dt);if(slow_t==0)slow_factor=1;
var _move=move_speed*slow_factor*_dt,_route=obj_game.route;
while(_move>0&&path_i<array_length(_route)-1) {
    var _tx=_route[path_i+1][0],_ty=_route[path_i+1][1],_distance=point_distance(x,y,_tx,_ty);
    if(_distance<=_move) {x=_tx;y=_ty;progress+=_distance;_move-=_distance;path_i++;}
    else {var _dir=point_direction(x,y,_tx,_ty);x+=lengthdir_x(_move,_dir);y+=lengthdir_y(_move,_dir);progress+=_move;_move=0;}
}
depth=-y;
if(path_i>=array_length(_route)-1) {
    obj_game.base_hp-=breach_damage;wp_fx(x,y,1,global.col.red,70);wp_sound(snd_breach,.65);
    if(instance_exists(obj_core))obj_core.flash=.6;
    if(obj_game.base_hp<=0)wp_end_run(2);
    instance_destroy();
}
