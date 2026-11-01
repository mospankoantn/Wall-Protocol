sim_dt=0;
if(!ready||result!=0)exit;
if(global.input_lock<=0&&global.page=="game") {
    if(keyboard_check_pressed(ord("P"))){wp_page("pause");exit;}
    if(keyboard_check_pressed(vk_space))wp_start_wave();
    if(keyboard_check_pressed(ord("F")))time_scale=time_scale==1?2:1;
    for(var _k=0;_k<3;++_k)if(keyboard_check_pressed(ord("1")+_k)||keyboard_check_pressed(vk_numpad1+_k))wp_build(selected_pad,_k);
    if(keyboard_check_pressed(ord("U")))wp_upgrade(wp_selected_tower());
    if(keyboard_check_pressed(ord("X")))wp_sell(wp_selected_tower());
    if(keyboard_check_pressed(ord("T")))wp_cycle_target(wp_selected_tower());
    if(mouse_check_button_pressed(mb_right))selected_pad=noone;
}
if(wp_active())sim_dt=(global.test_mode?1/60:min(delta_time/1000000,.05))*time_scale;
