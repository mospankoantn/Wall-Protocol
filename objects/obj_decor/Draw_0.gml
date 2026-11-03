if(decor_kind==0&&global.theme.tree!=c_white) {
    // Trees of the story maps are tinted (frost, ash, marsh); they sway by a tiny rotation because draw_sprite_pos cannot be tinted.
    var _rot=global.effects?sin(global.ui_time*1.1+x*.043+y*.021)*1.1:0;
    draw_sprite_ext(sprite_index,0,x,y,1,1,_rot,global.theme.tree,1);
} else if(decor_kind==0&&global.effects) {
    // Trees sway slightly: the crown moves, the trunk stays planted.
    var _w=sprite_get_width(sprite_index),_h=sprite_get_height(sprite_index);
    var _sw=sin(global.ui_time*1.1+x*.043+y*.021)*2.4,_l=x-_w/2,_r=x+_w/2,_t=y-_h/2,_b=y+_h/2;
    draw_sprite_pos(sprite_index,0,_l+_sw,_t,_r+_sw,_t,_r,_b,_l,_b,1);
} else draw_sprite_ext(sprite_index,0,x,y,1,1,0,c_white,1);
if(decor_kind==2&&global.effects) {
    var _f=.85+.15*sin(global.ui_time*9+x)+.08*sin(global.ui_time*23+x*3);
    wp_glow(x,y-14,58*_f,make_color_rgb(255,165,70),.42*_f);
    wp_glow(x,y-22,18*_f,make_color_rgb(255,225,150),.5*_f);
}
