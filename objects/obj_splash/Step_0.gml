timer+=min(delta_time/1000000,.05);
if(global.page=="splash"&&(timer>3.5||(timer>.6&&(keyboard_check_pressed(vk_enter)||mouse_check_button_pressed(mb_left))))) {
    if(global.language_chosen)room_goto(rm_menu);else wp_page("language");
}
if(global.test_mode&&timer>.3)room_goto(rm_game);
