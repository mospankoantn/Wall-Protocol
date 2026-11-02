function wp_read_json(_file) {
    if(!file_exists(_file)) return undefined;
    var _handle=-1;
    try {
        _handle=file_text_open_read(_file);
        var _text="";
        while(!file_text_eof(_handle)) { _text+=file_text_read_string(_handle);file_text_readln(_handle);if(string_length(_text)>2000000)throw "File too large"; }
        file_text_close(_handle);_handle=-1;
        return json_parse(_text,undefined,true);
    } catch(_error) { if(_handle!=-1)file_text_close(_handle);return undefined; }
}
function wp_write_json(_file,_data) {
    var _handle=-1;
    try {
        var _tmp=_file+".tmp";
        _handle=file_text_open_write(_tmp);
        file_text_write_string(_handle,json_stringify(_data));file_text_close(_handle);_handle=-1;
        if(is_undefined(wp_read_json(_tmp))) return false;
        if(file_exists(_file)) file_delete(_file);
        file_rename(_tmp,_file);
        return file_exists(_file);
    } catch(_error) {if(_handle!=-1)file_text_close(_handle);return false;}
}
function wp_number(_value,_lo,_hi) { return is_real(_value)&&!is_nan(_value)&&!is_infinity(_value)&&_value>=_lo&&_value<=_hi; }
function wp_integer(_value,_lo,_hi) {return wp_number(_value,_lo,_hi)&&floor(_value)==_value;}
function wp_fields(_value,_names) {
    if(!is_struct(_value))return false;
    for(var _i=0;_i<array_length(_names);++_i)if(!variable_struct_exists(_value,_names[_i]))return false;
    return true;
}
function wp_settings_load() {
    var _s=wp_read_json(global.file_prefix+"settings.json");
    if(!wp_fields(_s,["version","language","music","sfx","fullscreen","effects"]))return;
    if(_s.version!=1)return;
    if(_s.language=="en"||_s.language=="uk") {global.lang=_s.language;global.language_chosen=true;}
    if(wp_number(_s.music,0,1))global.music_volume=_s.music;
    if(wp_number(_s.sfx,0,1))global.sfx_volume=_s.sfx;
    if(is_bool(_s.fullscreen))global.fullscreen=_s.fullscreen;
    if(is_bool(_s.effects))global.effects=_s.effects;
    // Records were added in 1.2; older settings files simply do not contain them.
    if(variable_struct_exists(_s,"best_stars")&&wp_integer(_s.best_stars,0,3))global.best_stars=_s.best_stars;
    if(variable_struct_exists(_s,"best_time")&&wp_number(_s.best_time,0,10000000))global.best_time=_s.best_time;
}
function wp_settings_save() {
    if(!wp_write_json(global.file_prefix+"settings.json",{version:1,language:global.lang,music:global.music_volume,sfx:global.sfx_volume,fullscreen:global.fullscreen,effects:global.effects,best_stars:global.best_stars,best_time:global.best_time}))wp_notice(wp_tr("Could not save options.","Не вдалося зберегти налаштування."));
}
function wp_snapshot() {
    var _g=obj_game,_w=obj_wave;
    var _data={version:WP_SAVE_VERSION,gold:_g.gold,hp:_g.base_hp,wave:_g.wave,kills:_g.kills,elapsed:_g.elapsed,time_scale:_g.time_scale,next_uid:_g.next_uid,route:_g.route,active:_w.active,spawn_index:_w.spawn_index,spawn_timer:_w.spawn_timer,towers:[],enemies:[],projectiles:[]};
    with(obj_tower) {
        array_push(_data.towers,{pad_key:pad_key,kind:tower_kind,level:level,invested:invested,cooldown:cooldown,x:x,y:y,mode:target_mode});
    }
    with(obj_enemy) {
        if(hp>0)array_push(_data.enemies,{uid:uid,kind:enemy_kind,x:x,y:y,hp:hp,max_hp:max_hp,path_i:path_i,progress:progress,slow_t:slow_t,slow_factor:slow_factor});
    }
    with(obj_projectile) {
        if(instance_exists(target)&&target.hp>0)array_push(_data.projectiles,{kind:shot_kind,x:x,y:y,target_uid:target.uid,shot_power:shot_power,tower_level:tower_level});
    }
    return _data;
}
function wp_validate_save(_s) {
    if(!wp_fields(_s,["version","gold","hp","wave","kills","elapsed","time_scale","next_uid","route","active","spawn_index","spawn_timer","towers","enemies","projectiles"]))return false;
    if(_s.version!=WP_SAVE_VERSION||!wp_integer(_s.gold,0,1000000)||!wp_integer(_s.hp,1,20)||!wp_integer(_s.wave,0,8)||!wp_integer(_s.kills,0,100000)||!wp_number(_s.elapsed,0,10000000)||!wp_integer(_s.time_scale,1,2)||!wp_integer(_s.next_uid,1,1000000)||!is_bool(_s.active)||!wp_integer(_s.spawn_index,0,100)||!wp_number(_s.spawn_timer,-1,20))return false;
    if(!is_array(_s.route)||array_length(_s.route)<2||array_length(_s.route)>256||!is_array(_s.towers)||array_length(_s.towers)>256||!is_array(_s.enemies)||array_length(_s.enemies)>256||!is_array(_s.projectiles)||array_length(_s.projectiles)>1024)return false;
    for(var _i=0;_i<array_length(_s.route);++_i) {
        var _r=_s.route[_i];if(!is_array(_r)||array_length(_r)!=2||!wp_number(_r[0],-1000,10000)||!wp_number(_r[1],-1000,10000))return false;
    }
    if(_s.active&&_s.wave==0)return false;
    if(_s.wave==8&&!_s.active)return false;
    if(_s.spawn_index>array_length(wp_wave_list(max(1,_s.wave))))return false;
    if(!_s.active&&array_length(_s.enemies)>0)return false;
    var _keys={};
    for(var _j=0;_j<array_length(_s.towers);++_j) {
        var _t=_s.towers[_j];
        if(!wp_fields(_t,["pad_key","kind","level","invested","cooldown","x","y"]))return false;
        if(!is_string(_t.pad_key)||string_length(_t.pad_key)>100||variable_struct_exists(_keys,_t.pad_key)||!wp_integer(_t.kind,0,2)||!wp_integer(_t.level,1,3)||!wp_integer(_t.invested,0,10000)||!wp_number(_t.cooldown,-1,10)||!wp_number(_t.x,-1000,10000)||!wp_number(_t.y,-1000,10000))return false;
        // Targeting mode was added in 1.2; saves without it are still valid and default to "first".
        if(variable_struct_exists(_t,"mode")&&!wp_integer(_t.mode,0,3))return false;
        _keys[$ _t.pad_key]=true;
    }
    var _uids={};
    for(var _k=0;_k<array_length(_s.enemies);++_k) {
        var _e=_s.enemies[_k];
        if(!wp_fields(_e,["uid","kind","x","y","hp","max_hp","path_i","progress","slow_t","slow_factor"]))return false;
        if(!wp_integer(_e.uid,1,_s.next_uid-1)||variable_struct_exists(_uids,string(_e.uid))||!wp_integer(_e.kind,0,3)||!wp_number(_e.x,-1000,10000)||!wp_number(_e.y,-1000,10000)||!wp_number(_e.max_hp,1,100000)||!wp_number(_e.hp,.001,_e.max_hp)||!wp_integer(_e.path_i,0,array_length(_s.route)-2)||!wp_number(_e.progress,0,10000000)||!wp_number(_e.slow_t,0,10)||!wp_number(_e.slow_factor,.1,1))return false;
        _uids[$ string(_e.uid)]=true;
    }
    for(var _p=0;_p<array_length(_s.projectiles);++_p) {
        var _b=_s.projectiles[_p];
        if(!wp_fields(_b,["kind","x","y","target_uid","shot_power","tower_level"]))return false;
        if(!wp_integer(_b.kind,0,2)||!wp_number(_b.x,-1000,10000)||!wp_number(_b.y,-1000,10000)||!wp_integer(_b.target_uid,1,1000000)||!variable_struct_exists(_uids,string(_b.target_uid))||!wp_number(_b.shot_power,1,10)||!wp_integer(_b.tower_level,1,3))return false;
    }
    return true;
}
function wp_read_save() {
    var _s=wp_read_json(global.file_prefix+"save.json");
    if(wp_validate_save(_s))return _s;
    _s=wp_read_json(global.file_prefix+"save.bak");
    if(wp_validate_save(_s)) {wp_notice(wp_tr("Recovered the backup save.","Відновлено резервне збереження."));return _s;}
    return undefined;
}
function wp_save(_quiet=false) {
    if(room==rm_test)return false;
    if(!instance_exists(obj_game)||!obj_game.ready||obj_game.result!=0)return false;
    var _s=wp_snapshot();
    if(!wp_validate_save(_s)) {wp_notice(wp_tr("Cannot save this game state.","Цей стан гри неможливо зберегти."));return false;}
    var _file=global.file_prefix+"save.json";
    // Keep the previous verified state even if writing the new file is interrupted.
    if(wp_validate_save(wp_read_json(_file))) {
        var _bak=global.file_prefix+"save.bak";
        if(file_exists(_bak))file_delete(_bak);
        file_copy(_file,_bak);
    }
    var _ok=wp_write_json(_file,_s);
    if(!_quiet||!_ok)wp_notice(_ok?wp_tr("Expedition saved.","Похід збережено."):wp_tr("Save failed. Previous backup retained.","Помилка запису. Резервна копія збережена."));
    return _ok;
}
function wp_load() {
    if(room==rm_test)return false;
    var _s=wp_read_save();
    if(is_undefined(_s)) {wp_notice(wp_tr("Save is missing or damaged.","Збереження відсутнє або пошкоджене."));return false;}
    global.pending_load=_s;
    wp_room_goto(rm_game);
    return true;
}
function wp_restore(_s) {
    if(!wp_validate_save(_s))return false;
    // Reject stale map saves safely, before modifying any instance or economy.
    if(array_length(_s.route)!=array_length(obj_game.route))return false;
    for(var _r=0;_r<array_length(_s.route);++_r)if(point_distance(_s.route[_r][0],_s.route[_r][1],obj_game.route[_r][0],obj_game.route[_r][1])>.01)return false;
    for(var _i=0;_i<array_length(_s.towers);++_i) {
        var _saved=_s.towers[_i],_pad=wp_pad_by_key(_saved.pad_key);
        if(!instance_exists(_pad)||point_distance(_pad.x,_pad.y,_saved.x,_saved.y)>.01)return false;
    }
    with(obj_enemy)instance_destroy();with(obj_tower)instance_destroy();with(obj_projectile)instance_destroy();with(obj_effect)instance_destroy();
    with(obj_build_pad)tower=noone;
    obj_game.gold=_s.gold;obj_game.base_hp=_s.hp;obj_game.wave=_s.wave;obj_game.kills=_s.kills;obj_game.elapsed=_s.elapsed;obj_game.time_scale=_s.time_scale;obj_game.selected_pad=noone;
    obj_wave.active=_s.active;obj_wave.spawn_index=_s.spawn_index;obj_wave.spawn_timer=_s.spawn_timer;obj_wave.queue=wp_wave_list(max(1,_s.wave));
    for(var _j=0;_j<array_length(_s.towers);++_j) {
        var _t=_s.towers[_j],_p=wp_pad_by_key(_t.pad_key);
        var _new=wp_spawn(global.towers[_t.kind].object,_p.x,_p.y,{tower_kind:_t.kind,level:_t.level});
        _new.pad_key=_t.pad_key;_new.invested=_t.invested;_new.cooldown=_t.cooldown;_new.target_mode=variable_struct_exists(_t,"mode")?_t.mode:0;_p.tower=_new;
    }
    var _lookup={};
    for(var _k=0;_k<array_length(_s.enemies);++_k) {
        var _e=_s.enemies[_k],_n=wp_spawn(global.enemy_objects[_e.kind],_e.x,_e.y,{enemy_kind:_e.kind});
        _n.spawn_t=1;_n.uid=_e.uid;_n.hp=_e.hp;_n.max_hp=_e.max_hp;_n.path_i=_e.path_i;_n.progress=_e.progress;_n.slow_t=_e.slow_t;_n.slow_factor=_e.slow_factor;
        _lookup[$ string(_e.uid)]=_n;
    }
    obj_game.next_uid=_s.next_uid;
    for(var _b=0;_b<array_length(_s.projectiles);++_b) {
        var _shot=_s.projectiles[_b];
        wp_spawn(obj_projectile,_shot.x,_shot.y,{shot_kind:_shot.kind,target:_lookup[$ string(_shot.target_uid)],shot_power:_shot.shot_power,tower_level:_shot.tower_level});
    }
    return true;
}
function wp_new_game() {global.pending_load=undefined;global.resume_text=false;if(room==rm_game||room==rm_test)wp_room_goto(room);else wp_room_goto(rm_game);}
