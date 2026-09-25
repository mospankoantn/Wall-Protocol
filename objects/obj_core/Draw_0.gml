draw_set_color(global.col.teal);draw_set_alpha(.07+.02*sin(global.ui_time*2));draw_circle(x,y-22,84,false);draw_set_alpha(1);
draw_sprite_ext(spr_core,0,x,y-30,1,1,0,flash>0?global.col.red:c_white,1);
wp_text(x,y+51,wp_tr("THE CORE","ЯДРО"),fnt_ui,global.col.teal,fa_center);
