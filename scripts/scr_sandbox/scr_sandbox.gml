/// Manual test range. All controls and starting entities are authored in rm_test.
function wp_sandbox_setup() {
    var _lab=wp_ensure(obj_sandbox);
    global.pending_load=undefined;global.resume_text=false;
    obj_game.gold=_lab.starting_aether;obj_game.wave=_lab.test_wave;
    // If all example towers were removed, restore a small editable starter set.
    if(instance_number(obj_tower)==0) {
        for(var _i=0;_i<min(3,instance_number(obj_build_pad));++_i) {
            var _pad=instance_find(obj_build_pad,_i);
            var _tower=wp_spawn(global.towers[_i].object,_pad.x,_pad.y,{level:_i+1});
            _tower.pad_key=_pad.pad_key;_pad.tower=_tower;
        }
    }
    if(instance_number(obj_enemy)==0)for(var _k=0;_k<4;++_k)wp_sandbox_spawn(_k);
    // Project editor-placed enemies onto the nearest route segment so their
    // progress and tower targeting agree with their authored starting positions.
    var _route=obj_game.route;
    with(obj_enemy) {
        var _best=1000000000,_length=0;
        for(var _n=0;_n<array_length(_route)-1;++_n) {
            var _a=_route[_n],_b=_route[_n+1],_dx=_b[0]-_a[0],_dy=_b[1]-_a[1];
            var _sq=_dx*_dx+_dy*_dy;
            var _t=_sq>0?clamp(((x-_a[0])*_dx+(y-_a[1])*_dy)/_sq,0,1):0;
            var _px=_a[0]+_t*_dx,_py=_a[1]+_t*_dy,_dist=point_distance(x,y,_px,_py);
            if(_dist<_best){_best=_dist;path_i=_n;progress=_length+sqrt(_sq)*_t;}
            _length+=sqrt(_sq);
        }
        var _a=_route[path_i],_b=_route[path_i+1],_len=point_distance(_a[0],_a[1],_b[0],_b[1]);
        var _dx=_b[0]-_a[0],_dy=_b[1]-_a[1];
        var _t=_len>0?clamp(((x-_a[0])*_dx+(y-_a[1])*_dy)/(_len*_len),0,1):0;
        x=_a[0]+_t*_dx;y=_a[1]+_t*_dy;depth=-y;
    }
    wp_page("pause");
}
function wp_sandbox_spawn(_kind) {
    if(room!=rm_test||!instance_exists(obj_game))return noone;
    var _r=obj_game.route;
    return wp_spawn(global.enemy_objects[clamp(_kind,0,3)],_r[0][0],_r[0][1]);
}
function wp_sandbox_clear() {
    with(obj_enemy)instance_destroy();with(obj_projectile)instance_destroy();with(obj_effect)instance_destroy();
    obj_wave.active=false;obj_wave.queue=[];obj_wave.spawn_index=0;obj_wave.spawn_timer=0;
}
function wp_sandbox_label(_action) {
    switch(_action) {
        case "lab_spawn0":return wp_tr("+ Risen","+ Мрець");
        case "lab_spawn1":return wp_tr("+ Brute","+ Громила");
        case "lab_spawn2":return wp_tr("+ Runner","+ Бігун");
        case "lab_spawn3":return wp_tr("+ Colossus","+ Колос");
        case "lab_swarm":return wp_tr("+ 12 enemies","+ 12 ворогів");
        case "lab_clear":return wp_tr("Clear enemies","Прибрати ворогів");
        case "lab_gold":return wp_tr("+ 1000 aether","+ 1000 ефіру");
        case "lab_heal":return wp_tr("Repair core","Відновити ядро");
        case "lab_god":return wp_tr("God mode: ","Безсмертя: ")+(obj_sandbox.invulnerable?wp_tr("ON","ТАК"):wp_tr("OFF","НІ"));
        case "lab_cycle":return wp_tr("Test wave: ","Тест хвилі: ")+string(obj_sandbox.test_wave)+" / 8";
        case "lab_victory":return wp_tr("Test victory","Тест перемоги");
        case "lab_defeat":return wp_tr("Test defeat","Тест поразки");
        case "lab_reset":return wp_tr("Reset test room","Скинути кімнату");
        case "lab_menu":return wp_tr("Main menu","Головне меню");
    }
    return _action;
}
function wp_sandbox_action(_action) {
    if(room!=rm_test||!instance_exists(obj_sandbox))return;
    if(_action=="lab_reset"){global.pending_load=undefined;wp_room_goto(room);return;}
    if(_action=="lab_menu"){global.pending_load=undefined;wp_room_goto(rm_menu);return;}
    if(!wp_active())return;
    if(string_copy(_action,1,9)=="lab_spawn"){wp_sandbox_spawn(real(string_char_at(_action,10)));return;}
    switch(_action) {
        case "lab_swarm":for(var _i=0;_i<12;++_i)wp_sandbox_spawn(_i mod 3);break;
        case "lab_clear":wp_sandbox_clear();break;
        case "lab_gold":obj_game.gold=min(1000000,obj_game.gold+1000);break;
        case "lab_heal":obj_game.base_hp=20;wp_fx(obj_core.x,obj_core.y,1,global.col.teal,70);break;
        case "lab_god":obj_sandbox.invulnerable=!obj_sandbox.invulnerable;break;
        case "lab_cycle":if(!obj_wave.active){obj_sandbox.test_wave=obj_sandbox.test_wave mod 8+1;obj_game.wave=obj_sandbox.test_wave;}break;
        case "lab_victory":wp_end_run(1);break;
        case "lab_defeat":obj_game.base_hp=0;wp_end_run(2);break;
    }
}

// Fallback only: existing room-authored buttons always win.
function wp_sandbox_buttons() {
    return [
        {"x":1084,"y":168,"action":"wave","page":"game","button_w":258,"nav_order":0},
        {"x":1084,"y":227,"action":"speed","page":"game","button_w":124,"nav_order":1},
        {"x":1218,"y":227,"action":"pause","page":"game","button_w":124,"nav_order":2},
        {"x":1084,"y":398,"action":"build0","page":"game","button_w":258,"nav_order":3},
        {"x":1084,"y":458,"action":"build1","page":"game","button_w":258,"nav_order":4},
        {"x":1084,"y":518,"action":"build2","page":"game","button_w":258,"nav_order":5},
        {"x":1084,"y":584,"action":"upgrade","page":"game","button_w":258,"nav_order":6},
        {"x":1084,"y":641,"action":"sell","page":"game","button_w":258,"nav_order":7},
        {"x":503,"y":300,"action":"music","page":"options","button_w":360,"nav_order":0},
        {"x":503,"y":360,"action":"sfx","page":"options","button_w":360,"nav_order":1},
        {"x":503,"y":420,"action":"fullscreen","page":"options","button_w":360,"nav_order":2},
        {"x":503,"y":480,"action":"language","page":"options","button_w":360,"nav_order":3},
        {"x":503,"y":540,"action":"effects","page":"options","button_w":360,"nav_order":4},
        {"x":503,"y":622,"action":"back","page":"options","button_w":360,"nav_order":5},
        {"x":503,"y":355,"action":"english","page":"language","button_w":360,"nav_order":0},
        {"x":503,"y":417,"action":"ukrainian","page":"language","button_w":360,"nav_order":1},
        {"x":503,"y":460,"action":"retry","page":"result","button_w":360,"nav_order":0},
        {"x":503,"y":522,"action":"menu","page":"result","button_w":360,"nav_order":1},
        {"x":503,"y":320,"action":"resume","page":"pause","button_w":360,"nav_order":0},
        {"x":503,"y":390,"action":"options","page":"pause","button_w":360,"nav_order":1},
        {"x":503,"y":460,"action":"lab_reset","page":"pause","button_w":360,"nav_order":2},
        {"x":503,"y":530,"action":"menu","page":"pause","button_w":360,"nav_order":3},
        {"x":24,"y":544,"action":"lab_spawn0","page":"game","button_w":192,"button_h":40,"nav_order":8},
        {"x":228,"y":544,"action":"lab_spawn1","page":"game","button_w":192,"button_h":40,"nav_order":9},
        {"x":432,"y":544,"action":"lab_spawn2","page":"game","button_w":192,"button_h":40,"nav_order":10},
        {"x":636,"y":544,"action":"lab_spawn3","page":"game","button_w":192,"button_h":40,"nav_order":11},
        {"x":840,"y":544,"action":"lab_swarm","page":"game","button_w":192,"button_h":40,"nav_order":12},
        {"x":24,"y":590,"action":"lab_clear","page":"game","button_w":192,"button_h":40,"nav_order":13},
        {"x":228,"y":590,"action":"lab_gold","page":"game","button_w":192,"button_h":40,"nav_order":14},
        {"x":432,"y":590,"action":"lab_heal","page":"game","button_w":192,"button_h":40,"nav_order":15},
        {"x":636,"y":590,"action":"lab_god","page":"game","button_w":192,"button_h":40,"nav_order":16},
        {"x":840,"y":590,"action":"lab_cycle","page":"game","button_w":192,"button_h":40,"nav_order":17},
        {"x":24,"y":636,"action":"lab_victory","page":"game","button_w":192,"button_h":40,"nav_order":18},
        {"x":228,"y":636,"action":"lab_defeat","page":"game","button_w":192,"button_h":40,"nav_order":19},
        {"x":432,"y":636,"action":"lab_reset","page":"game","button_w":192,"button_h":40,"nav_order":20},
        {"x":636,"y":636,"action":"lab_menu","page":"game","button_w":192,"button_h":40,"nav_order":21}
    ];
}
