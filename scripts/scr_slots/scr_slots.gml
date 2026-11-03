/// Save slots (1.4). Slot 0 is the autosave and keeps the 1.1-1.3 file names (wp_save.json / wp_save.bak), so old saves
/// load unchanged. Slots 1-3 are manual: wp_slot1.json ... with their own .bak backup.
#macro WP_SLOTS 4

function wp_slot_file(_slot) { return global.file_prefix+(_slot==0?"save":"slot"+string(_slot))+".json"; }
function wp_slot_bak(_slot) { return global.file_prefix+(_slot==0?"save":"slot"+string(_slot))+".bak"; }
function wp_slot_exists(_slot) { return file_exists(wp_slot_file(_slot))||file_exists(wp_slot_bak(_slot)); }
function wp_any_save() {
    for(var _i=0;_i<WP_SLOTS;++_i)if(wp_slot_exists(_i))return true;
    return false;
}
// Reads a slot: the main file if it validates, otherwise its backup. Returns {data,recovered} or undefined.
function wp_slot_read(_slot) {
    var _s=wp_read_json(wp_slot_file(_slot));
    if(wp_validate_save(_s))return {data:_s,recovered:false};
    _s=wp_read_json(wp_slot_bak(_slot));
    if(wp_validate_save(_s))return {data:_s,recovered:true};
    return undefined;
}
// Summary shown on a slot card. state: "empty", "ok", "recovered" (read from the backup) or "damaged".
function wp_slot_info(_slot) {
    var _info={state:"empty",mode:0,chapter:0,wave:0,total:8,hp:20,gold:0,elapsed:0,stamp:0};
    if(!wp_slot_exists(_slot))return _info;
    var _r=wp_slot_read(_slot);
    if(is_undefined(_r)){_info.state="damaged";return _info;}
    var _s=_r.data;
    _info.state=_r.recovered?"recovered":"ok";
    _info.mode=wp_save_mode(_s);_info.chapter=wp_save_chapter(_s);
    _info.wave=_s.wave;_info.total=wp_rules_for(_info.mode,_info.chapter).total;
    _info.hp=_s.hp;_info.gold=_s.gold;_info.elapsed=_s.elapsed;
    _info.stamp=wp_save_stamp(_s);
    return _info;
}
function wp_slots_refresh() {
    var _list=[];
    for(var _i=0;_i<WP_SLOTS;++_i)array_push(_list,wp_slot_info(_i));
    global.slot_info=_list;
}
// Newest readable slot (the one "Continue" resumes), or -1.
function wp_latest_slot() {
    var _best=-1,_stamp=-1;
    for(var _i=0;_i<WP_SLOTS;++_i) {
        var _info=wp_slot_info(_i);
        if(_info.state=="ok"||_info.state=="recovered") {
            if(_best<0||_info.stamp>_stamp){_best=_i;_stamp=_info.stamp;}
        }
    }
    return _best;
}
function wp_slot_name(_slot) { return _slot==0?wp_tr("Autosave","Автозбереження"):wp_tr("Slot ","Слот ")+string(_slot); }

// Writes the current battle to a slot, keeping the previous verified file as that slot's backup.
function wp_save_slot(_slot,_quiet=false) {
    if(room==rm_test||_slot<0||_slot>=WP_SLOTS)return false;
    if(!instance_exists(obj_game)||!obj_game.ready||obj_game.result!=0)return false;
    var _s=wp_snapshot();
    // The timestamp is added here (not in wp_snapshot) so that snapshots stay comparable in tests.
    _s.meta={stamp:date_current_datetime(),game:WP_VERSION};
    if(!wp_validate_save(_s)){wp_notice(wp_tr("Cannot save this game state.","Цей стан гри неможливо зберегти."));return false;}
    var _file=wp_slot_file(_slot),_bak=wp_slot_bak(_slot);
    if(wp_validate_save(wp_read_json(_file))) {
        if(file_exists(_bak))file_delete(_bak);
        file_copy(_file,_bak);
    }
    var _ok=wp_write_json(_file,_s);
    if(_ok)global.save_flash=1.6;
    if(!_quiet||!_ok) {
        if(_ok)wp_notice(_slot==0?wp_tr("Expedition saved.","Похід збережено."):wp_tr("Saved to slot ","Збережено в слот ")+string(_slot)+".");
        else wp_notice(wp_tr("Save failed. Previous backup retained.","Помилка запису. Резервна копія збережена."));
    }
    return _ok;
}
function wp_load_slot(_slot) {
    if(room==rm_test||_slot<0||_slot>=WP_SLOTS)return false;
    var _r=wp_slot_read(_slot);
    if(is_undefined(_r)){wp_notice(wp_tr("Save is missing or damaged.","Збереження відсутнє або пошкоджене."));return false;}
    if(_r.recovered)wp_notice(wp_tr("Recovered the backup save.","Відновлено резервне збереження."));
    global.pending_load=_r.data;
    wp_room_goto(rm_game);
    return true;
}
function wp_delete_slot(_slot) {
    if(_slot<0||_slot>=WP_SLOTS)return false;
    var _f=wp_slot_file(_slot),_b=wp_slot_bak(_slot);
    if(file_exists(_f))file_delete(_f);
    if(file_exists(_b))file_delete(_b);
    wp_slots_refresh();
    wp_notice(wp_tr("Deleted ","Видалено: ")+wp_slot_name(_slot)+".");
    return !wp_slot_exists(_slot);
}
// A click on a slot card: load it, save into an empty slot, or ask before overwriting.
function wp_slot_click(_slot) {
    global.slot_target=_slot;
    if(global.slot_mode=="load"){wp_load_slot(_slot);return;}
    if(global.slot_info[_slot].state=="empty"){wp_save_slot(_slot);wp_slots_refresh();}
    else wp_page("confirm_overwrite");
}
function wp_slots_open(_mode) {
    global.slot_mode=_mode;
    wp_slots_refresh();
    global.return_page=global.page;
    wp_page("slots");
}

// ---- text for the slot cards and the slots screen
function wp_slot_title(_slot) {
    var _i=global.slot_info[_slot];
    var _head=wp_slot_name(_slot);
    if(_i.state=="empty"||_i.state=="damaged")return _head;
    return _head+"   -   "+(_i.mode==1?wp_roman(_i.chapter)+"  "+wp_chapter_title(_i.chapter):wp_tr("Survival","Виживання"));
}
function wp_slot_detail(_slot) {
    var _i=global.slot_info[_slot];
    switch(_i.state) {
        case "empty":return _slot==0?wp_tr("No autosave yet.","Автозбереження ще немає."):wp_tr("Empty slot","Порожній слот");
        case "damaged":return wp_tr("Damaged save - it cannot be loaded. You can delete it.","Пошкоджене збереження - його неможливо завантажити. Можна видалити.");
    }
    return wp_tr("Wave ","Хвиля ")+string(_i.wave)+" / "+string(_i.total)+"     "+wp_tr("Core ","Ядро ")+string(_i.hp)+" / 20     "+wp_tr("Aether ","Ефір ")+string(_i.gold)+"     "+wp_clock(_i.elapsed);
}
function wp_slot_date(_slot) {
    var _i=global.slot_info[_slot];
    var _text=_i.stamp>0?date_datetime_string(_i.stamp):"";
    if(_i.state=="recovered")_text+=(_text==""?"":"     ")+wp_tr("Recovered from backup","Відновлено з резервної копії");
    return _text;
}
function wp_slots_draw() {
    var _a=global.overlay_t,_save=global.slot_mode=="save";
    wp_panel(300,96,766,590,.98*_a);
    wp_text_a(683,116,_save?wp_tr("Save game","Зберегти гру"):wp_tr("Load game","Завантажити гру"),fnt_heading,global.col.gold,fa_center,_a);
    wp_text_a(683,160,_save?wp_tr("Choose a slot. The autosave is reserved for the game.","Оберіть слот. Автозбереження зарезервоване для гри."):wp_tr("Pick an expedition to resume. A loaded battle starts paused.","Оберіть похід, щоб продовжити. Завантажений бій починається на паузі."),fnt_ui,global.col.muted,fa_center,_a);
}
