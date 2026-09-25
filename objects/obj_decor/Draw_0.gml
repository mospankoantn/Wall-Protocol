draw_sprite_ext(sprite_index,0,x,y,1,1,0,c_white,1);
if(decor_kind==2&&global.effects){draw_set_alpha(.06+.02*sin(global.ui_time*7+x));draw_set_color(global.col.gold);draw_circle(x,y-13,50,false);draw_set_alpha(1);}
