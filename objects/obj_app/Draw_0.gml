if(global.notice_time>0) {
    draw_set_font(fnt_ui);
    var _width=min(1180,string_width(global.notice)+64);
    wp_panel((WP_W-_width)/2,706,_width,44,.98);
    wp_text(WP_W/2,716,global.notice,fnt_ui,global.col.gold,fa_center);
}
