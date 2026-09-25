var _dt=min(delta_time/1000000,.05);
global.ui_time+=_dt;
global.notice_time=max(0,global.notice_time-_dt);
global.input_lock=max(0,global.input_lock-1);
if(keyboard_check_pressed(vk_f11))wp_action("fullscreen");
if(global.input_lock>0)exit;
if(keyboard_check_pressed(vk_escape)) {
    switch(global.page) {
        case "game":wp_page("pause");break;
        case "pause":wp_page("game");break;
        case "options":wp_page(global.return_page);break;
        case "language":if(room!=rm_boot)wp_page("options");break;
        case "text":wp_action("back");break;
        case "confirm_new":wp_page("main");break;
    }
}
if(keyboard_check_pressed(vk_tab)||keyboard_check_pressed(vk_down)||keyboard_check_pressed(vk_up)) {
    var _buttons=[];
    with(obj_button)if(page==global.page&&wp_button_enabled(action))array_push(_buttons,id);
    array_sort(_buttons,function(_a,_b){return _a.nav_order-_b.nav_order;});
    var _count=array_length(_buttons),_index=-1;
    for(var _i=0;_i<_count;++_i)if(_buttons[_i]==global.focus_button)_index=_i;
    if(_count>0)global.focus_button=_buttons[(_index+(keyboard_check_pressed(vk_up)?_count-1:1)+_count)mod _count];
}
if(keyboard_check_pressed(vk_enter)&&instance_exists(global.focus_button)) {
    var _b=global.focus_button;
    if(_b.page==global.page&&wp_button_enabled(_b.action))wp_action(_b.action);
}
if(global.page=="options"&&instance_exists(global.focus_button)) {
    var _b=global.focus_button;
    if((_b.action=="music"||_b.action=="sfx")&&(keyboard_check_pressed(vk_left)||keyboard_check_pressed(vk_right))) {
        var _change=keyboard_check_pressed(vk_left)?-.1:.1;
        if(_b.action=="music")global.music_volume=clamp(global.music_volume+_change,0,1);else global.sfx_volume=clamp(global.sfx_volume+_change,0,1);
        wp_audio_apply();wp_settings_save();
    }
}
if(wp_active()) {
    autosave_timer-=_dt;
    if(autosave_timer<=0){wp_save(true);autosave_timer=30;}
}
