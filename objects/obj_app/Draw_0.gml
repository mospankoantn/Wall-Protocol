matrix_set(matrix_world,matrix_build_identity());
if(global.notice_time>0) {
    // Toast slides up and fades in, then fades out during its last third of a second.
    var _t=global.notice_time,_in=clamp((3-_t)/.2,0,1),_a=min(_in,clamp(_t/.35,0,1));
    draw_set_font(fnt_ui);
    var _width=min(1180,string_width(global.notice)+64),_ny=706+(1-_in)*14;
    wp_panel((WP_W-_width)/2,_ny,_width,44,.98*_a);
    wp_text_a(WP_W/2,_ny+10,global.notice,fnt_ui,global.col.gold,fa_center,_a);
}
if(global.fade_a>0){draw_set_alpha(global.fade_a);draw_set_color(c_black);draw_rectangle(0,0,WP_W,WP_H,false);draw_set_alpha(1);}
