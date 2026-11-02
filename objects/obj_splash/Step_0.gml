timer+=min(delta_time/1000000,.05);
if(global.test_mode) {
    if(timer>1.2&&test_stage==1){wp_page("language");test_stage=2;}
    if(timer>1.4&&test_stage==3)wp_action("ukrainian");
    exit;
}
if(global.page=="splash"&&(timer>3.5||(timer>.6&&(keyboard_check_pressed(vk_enter)||mouse_check_button_pressed(mb_left))))) {
    if(global.language_chosen)wp_room_goto(rm_menu);else wp_page("language");
}
