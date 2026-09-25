if(global.page=="main"&&global.input_lock<=0&&keyboard_check_pressed(vk_f2))wp_action("sandbox");
if(global.test_mode&&variable_global_exists("test_intro")&&global.test_intro) {
    menu_timer+=min(delta_time/1000000,.05);
    if(menu_timer>.2){global.test_intro=false;wp_new_game();}
}
