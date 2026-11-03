banner_t=max(0,banner_t-wp_dt());
if(!wp_active()||!active)exit;
var _dt=wp_dt();spawn_timer-=_dt;
if(spawn_index<array_length(queue)&&spawn_timer<=0) {
    var _kind=queue[spawn_index],_route=obj_game.route;
    wp_spawn(global.enemy_objects[_kind],_route[0][0],_route[0][1],{enemy_kind:_kind});
    wp_fx(_route[0][0],_route[0][1]-14,1,global.col.purple,54);wp_fx(_route[0][0],_route[0][1]-20,3,global.col.purple,40);
    if(_kind==3){wp_sound(snd_boss,1);wp_shake(.4);}
    spawn_index++;spawn_timer=max(.35,.9-obj_game.wave*.04);
}
if(spawn_index>=array_length(queue)&&instance_number(obj_enemy)==0) {
    active=false;
    if(obj_game.wave>=global.rules.total)wp_end_run(1);
    else {
        var _bonus=45+obj_game.wave*10;obj_game.gold+=_bonus;
        wp_notice(wp_tr("Wave cleared. Aether +","Хвилю відбито. Ефір +")+string(_bonus));wp_sound(snd_clear,.85);wp_save(true);
    }
}
