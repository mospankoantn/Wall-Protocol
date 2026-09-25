hovered=page==global.page&&point_in_rectangle(mouse_x,mouse_y,x,y,x+button_w,y+button_h);
if(!hovered||global.input_lock>0)exit;
if(mouse_check_button_pressed(mb_left)&&wp_button_enabled(action)) {
    global.focus_button=id;
    if(action=="music"||action=="sfx") {
        var _value=clamp(round((mouse_x-x-16)/(button_w-32)*10)/10,0,1);
        if(action=="music")global.music_volume=_value;else global.sfx_volume=_value;
        wp_sound(snd_click,.5);wp_audio_apply();wp_settings_save();
    } else wp_action(action);
    global.input_lock=2;
}
