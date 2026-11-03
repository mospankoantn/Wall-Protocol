function wp_ensure(_object,_x=0,_y=0) {if(!instance_exists(_object))return wp_spawn(_object,_x,_y);return instance_find(_object,0);}
function wp_room_setup() {
    wp_init();wp_ensure(obj_app);wp_ensure(obj_audio);
    if(room==rm_boot) {wp_ensure(obj_splash);wp_page("splash");wp_ensure_buttons();return;}
    if(room==rm_menu) {wp_ensure(obj_menu);wp_page("main");wp_ensure_buttons();return;}
    if(room==rm_text) {wp_ensure(obj_text,100,150);wp_page("text");wp_ensure_buttons();return;}
    wp_ensure(obj_game);wp_ensure(obj_wave);wp_ensure(obj_board);wp_ensure(obj_hud);
    // 1.4: the run (survival or a story chapter) decides rules, map layout and visual theme. A save to be loaded decides first.
    if(room==rm_test)wp_rules_set(0,0);
    else if(!is_undefined(global.pending_load))wp_rules_set(wp_save_mode(global.pending_load),wp_save_chapter(global.pending_load));
    wp_map_apply(room==rm_test?0:global.rules.map);
    wp_ensure(obj_core,966,475);wp_ensure(obj_portal,70,385);
    if(instance_number(obj_path_node)<2) {
        with(obj_path_node)instance_destroy();
        for(var _i=0;_i<array_length(global.default_route);++_i) wp_spawn(obj_path_node,global.default_route[_i][0],global.default_route[_i][1],{node_order:_i});
        show_debug_message("Wall Protocol: restored missing route markers.");
    }
    var _nodes=[];
    with(obj_path_node)array_push(_nodes,id);
    array_sort(_nodes,function(_a,_b){return _a.node_order-_b.node_order;});
    obj_game.route=[];
    for(var _j=0;_j<array_length(_nodes);++_j)array_push(obj_game.route,[_nodes[_j].x,_nodes[_j].y]);
    if(instance_number(obj_build_pad)==0) {
        for(var _p=0;_p<array_length(global.default_pads);++_p)wp_spawn(obj_build_pad,global.default_pads[_p][0],global.default_pads[_p][1],{pad_key:"pad_"+(_p<10?"0":"")+string(_p)});
        show_debug_message("Wall Protocol: restored missing build pads.");
    }
    // Custom editor keys are retained. Duplicate default keys become unique by position.
    var _seen={};
    with(obj_build_pad) {
        if(pad_key=="pad"||variable_struct_exists(_seen,pad_key))pad_key="pad_"+string(round(x))+"_"+string(round(y));
        _seen[$ pad_key]=true;
    }
    // Towers can also be authored directly in the room. Link to the nearest pad.
    with(obj_tower) {
        var _pad=instance_nearest(x,y,obj_build_pad);
        if(instance_exists(_pad)&&point_distance(x,y,_pad.x,_pad.y)<50&&!instance_exists(_pad.tower)) {_pad.tower=id;pad_key=_pad.pad_key;x=_pad.x;y=_pad.y;}
        else {var _new=wp_spawn(obj_build_pad,x,y,{pad_key:"authored_"+string(round(x))+"_"+string(round(y))});_new.tower=id;pad_key=_new.pad_key;}
    }
    obj_game.ready=true;
    obj_game.gold=global.rules.gold;
    wp_page("game");
    if(room==rm_test){wp_sandbox_setup();wp_ensure_buttons();return;}
    var _loaded=false;
    if(!is_undefined(global.pending_load)) {
        _loaded=wp_restore(global.pending_load);global.pending_load=undefined;
        if(!_loaded){wp_notice(wp_tr("The map changed. Your save was kept; start a new expedition.","Мапа змінилася. Збереження залишено; почніть новий похід."));obj_game.ready=false;wp_room_goto(rm_menu);return;}
    }
    wp_ensure_buttons();
    if(global.resume_text){wp_page("pause");global.resume_text=false;}
    else if(_loaded)wp_page("pause");
    if(!_loaded)wp_save(true);
    // Story chapters open with a briefing (skipped on retry and when resuming a save).
    if(global.mode==1&&!_loaded&&!global.skip_brief&&global.page=="game")wp_cutscene_start("brief",global.chapter,wp_story_lines("brief",global.chapter));
    global.skip_brief=false;
    if(global.test_mode)wp_ensure(obj_test);
}
function wp_pad_by_key(_key) {
    for(var _i=0;_i<instance_number(obj_build_pad);++_i){var _p=instance_find(obj_build_pad,_i);if(_p.pad_key==_key)return _p;}
    return noone;
}
function wp_selected_tower() {
    if(!instance_exists(obj_game)||!instance_exists(obj_game.selected_pad))return noone;
    return obj_game.selected_pad.tower;
}
function wp_upgrade_cost(_tower) {return round(global.towers[_tower.tower_kind].cost*(.65+.35*_tower.level));}
function wp_build(_pad,_kind) {
    if(!wp_active()||!instance_exists(_pad)||instance_exists(_pad.tower)||_kind<0||_kind>2)return false;
    var _cost=global.towers[_kind].cost;
    if(obj_game.gold<_cost){wp_notice(wp_tr("Not enough aether.","Недостатньо ефіру."));wp_sound(snd_error,.7);return false;}
    obj_game.gold-=_cost;
    var _tower=wp_spawn(global.towers[_kind].object,_pad.x,_pad.y,{tower_kind:_kind});
    _tower.pad_key=_pad.pad_key;_pad.tower=_tower;
    wp_fx(_pad.x,_pad.y,1,global.col.gold,44);wp_fx(_pad.x,_pad.y-22,3,global.col.gold,46);wp_sound(snd_build);
    return true;
}
function wp_upgrade(_tower) {
    if(!wp_active()||!instance_exists(_tower)||_tower.level>=3)return false;
    var _cost=wp_upgrade_cost(_tower);
    if(obj_game.gold<_cost){wp_notice(wp_tr("Not enough aether.","Недостатньо ефіру."));wp_sound(snd_error,.7);return false;}
    obj_game.gold-=_cost;_tower.level++;_tower.invested+=_cost;_tower.cooldown=0;
    wp_fx(_tower.x,_tower.y,1,global.col.gold,55);wp_fx(_tower.x,_tower.y-30,3,global.col.gold,60);wp_fx(_tower.x,_tower.y,0,global.col.gold,48);wp_sound(snd_upgrade,.9);
    return true;
}
function wp_sell(_tower) {
    if(!wp_active()||!instance_exists(_tower))return false;
    obj_game.gold+=round(_tower.invested*.7);
    var _pad=wp_pad_by_key(_tower.pad_key);if(instance_exists(_pad))_pad.tower=noone;
    wp_fx(_tower.x,_tower.y,1,global.col.gold,32);instance_destroy(_tower);wp_sound(snd_sell,.8);
    return true;
}
function wp_start_wave() {
    if(room==rm_test&&wp_active()&&!obj_wave.active)obj_game.wave=obj_sandbox.test_wave-1;
    if(!wp_active()||!instance_exists(obj_wave)||obj_wave.active||obj_game.wave>=global.rules.total)return false;
    obj_game.wave++;
    obj_wave.queue=wp_wave_list(obj_game.wave);obj_wave.spawn_index=0;obj_wave.spawn_timer=.6;obj_wave.active=true;obj_wave.banner_t=2.4;obj_wave.caption=wp_wave_caption(obj_game.wave);
    wp_notice(wp_tr("Wave ","Хвиля ")+string(obj_game.wave)+wp_tr(" approaches."," наближається."));wp_sound(snd_horn,.9);wp_sound(snd_wave,.7);
    return true;
}
function wp_fx(_x,_y,_kind,_color,_radius=30) {
    if(!global.effects)return;
    wp_spawn(obj_effect,_x,_y,{fx_kind:_kind,tint:_color,radius:_radius});
}
// Smooth room change: fade to black, switch rooms, fade back in (handled by obj_app). Instant in automated tests.
function wp_room_goto(_room) {
    if(global.test_mode){room_goto(_room);return;}
    if(global.fade_dir>0)return;
    global.fade_room=_room;global.fade_dir=1;
}
function wp_shake(_amount) { if(global.effects)global.shake=max(global.shake,_amount); }
// A translucent copy of a fallen enemy that rises and dissolves.
function wp_ghost(_enemy) {
    if(!global.effects)return;
    wp_spawn(obj_effect,_enemy.x,_enemy.y,{fx_kind:4,tint:c_white,radius:0,ghost_sprite:_enemy.sprite_index,ghost_frame:floor(_enemy.walk_time)mod 2,ghost_face:_enemy.face});
}
// Short floating text (aether gained, core damage). Purely cosmetic, so it follows the effects option.
function wp_popup(_x,_y,_text,_color) {
    if(!global.effects)return;
    wp_spawn(obj_effect,_x,_y,{fx_kind:2,tint:_color,radius:0,fx_text:_text});
}
function wp_cycle_target(_tower) {
    if(!wp_active()||!instance_exists(_tower))return false;
    _tower.target_mode=(_tower.target_mode+1)mod 4;
    wp_sound(snd_click,.5);
    return true;
}
function wp_damage(_enemy,_damage) {
    if(!instance_exists(_enemy)||_enemy.hp<=0)return;
    _enemy.hp-=_damage;_enemy.hit_flash=.12;
    if(_enemy.hp<=0) {
        obj_game.gold+=_enemy.reward;obj_game.kills++;
        wp_fx(_enemy.x,_enemy.y,0,global.col.gold,22);
        if(_enemy.enemy_kind==0)wp_sound(snd_hit,.35,.1);else wp_sound(snd_death,_enemy.enemy_kind==3?.9:.5,.08);
        wp_popup(_enemy.x,_enemy.y-34,"+"+string(_enemy.reward),global.col.gold);
        if(_enemy.enemy_kind==3){wp_fx(_enemy.x,_enemy.y,1,global.col.purple,130);wp_fx(_enemy.x,_enemy.y,0,global.col.gold,70);wp_shake(.55);}
        wp_ghost(_enemy);
        instance_destroy(_enemy);
    }
}
// Keeps the best victory: more stars first, then the faster time. Stored with the settings.
function wp_record_result() {
    var _stars=wp_rating(obj_game.base_hp),_time=obj_game.elapsed;
    var _better=_stars>global.best_stars||(_stars==global.best_stars&&(global.best_time<=0||_time<global.best_time));
    if(!_better)return;
    global.best_stars=_stars;global.best_time=_time;obj_game.new_record=true;
    wp_settings_save();
}
function wp_end_run(_result) {
    if(obj_game.result!=0)return;
    obj_game.result=_result;obj_game.base_hp=max(0,obj_game.base_hp);wp_page("result");
    wp_sound(_result==1?snd_victory:snd_defeat);
    if(room==rm_test)return;
    if(_result==1) {
        if(global.mode==1)wp_story_record(global.chapter,wp_rating(obj_game.base_hp),obj_game.elapsed);
        else wp_record_result();
    }
    // Completed runs cannot be resumed as an already-finished combat state.
    var _file=global.file_prefix+"save.json",_bak=global.file_prefix+"save.bak";
    if(file_exists(_file))file_delete(_file);if(file_exists(_bak))file_delete(_bak);
}

// Applies a generated map (scr_maps) over the room: replaces route, pads, decor, core and portal, and sets the visual theme.
// Map 0 keeps whatever the room contains (the editable forest map).
function wp_map_apply(_id) {
    global.theme=wp_map_theme(_id);
    if(_id==0)return;
    var _m=wp_map_data(_id);
    if(is_undefined(_m))return;
    with(obj_path_node)instance_destroy();
    with(obj_build_pad)instance_destroy();
    with(obj_decor)instance_destroy();
    with(obj_core)instance_destroy();
    with(obj_portal)instance_destroy();
    for(var _i=0;_i<array_length(_m.route);++_i)wp_spawn(obj_path_node,_m.route[_i][0],_m.route[_i][1],{node_order:_i});
    for(var _p=0;_p<array_length(_m.pads);++_p)wp_spawn(obj_build_pad,_m.pads[_p][0],_m.pads[_p][1],{pad_key:"pad_"+(_p<10?"0":"")+string(_p)});
    var _kinds=[obj_tree,obj_rocks,obj_brazier,obj_wall,obj_grave];
    for(var _d=0;_d<array_length(_m.decor);++_d)wp_spawn(_kinds[_m.decor[_d][0]],_m.decor[_d][1],_m.decor[_d][2]);
    wp_spawn(obj_core,_m.core[0],_m.core[1]);
    wp_spawn(obj_portal,_m.portal[0],_m.portal[1]);
}
