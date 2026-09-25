if(!wp_active()||global.input_lock>0)exit;
if(mouse_check_button_pressed(mb_left)&&point_distance(mouse_x,mouse_y,x,y)<=37)obj_game.selected_pad=id;
