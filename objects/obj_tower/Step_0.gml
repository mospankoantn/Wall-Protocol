if(!wp_active())exit;
var _dt=wp_dt();cooldown=max(-.5,cooldown-_dt);recoil=max(0,recoil-_dt*4);depth=-y;
var _range=global.towers[tower_kind].range+(level-1)*10;
target=noone;var _best=-1;
for(var _i=0;_i<instance_number(obj_enemy);++_i) {
    var _e=instance_find(obj_enemy,_i);
    if(_e.hp>0&&_e.progress>_best&&point_distance(x,y,_e.x,_e.y)<=_range){target=_e;_best=_e.progress;}
}
if(cooldown<=0&&instance_exists(target)) {
    var _power=1+(level-1)*.58;
    wp_spawn(obj_projectile,x,y-27,{shot_kind:tower_kind,target:target,shot_power:_power,tower_level:level});
    cooldown=global.towers[tower_kind].rate/(1+(level-1)*[.12,.08,.10][tower_kind]);recoil=1;
    wp_sound(global.towers[tower_kind].sound,.45);
}
