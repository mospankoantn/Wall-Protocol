draw_clear(global.col.bg);
// Slow "camera drift" over the key art, drifting fog and a pulsing glow on the crystal.
var _zoom=1.045+.025*sin(global.ui_time*.12),_zw=WP_W*_zoom,_zh=WP_H*_zoom;
draw_sprite_stretched(spr_menu_art,0,(WP_W-_zw)/2+sin(global.ui_time*.07)*12,(WP_H-_zh)/2+cos(global.ui_time*.05)*6,_zw,_zh);
if(global.effects) {
    draw_sprite_tiled_ext(spr_mist,0,global.ui_time*12,global.ui_time*2,2.2,2.2,make_color_rgb(140,185,190),.13);
    wp_glow(1088,178,140,global.col.teal,.16+.07*sin(global.ui_time*1.6));
}
draw_set_alpha(.25);draw_set_color(global.col.bg);draw_rectangle(0,0,510,WP_H,false);draw_set_alpha(1);
wp_text(80,62,WP_STUDIO+"  /  "+wp_tr("A TOWER DEFENSE TALE","ІСТОРІЯ ПРО ОСТАННЮ ВАРТУ"),fnt_ui,global.col.gold);
wp_glow(250,200,230,global.col.gold,.05+.025*sin(global.ui_time*1.2));
wp_text(76,122,"WALL",fnt_title,global.col.text);
wp_text(76,193,"PROTOCOL",fnt_title,global.col.text);
wp_rule(80,287,360);
wp_text(80,302,wp_tr("Hold the line. Keep the light.","Втримай рубіж. Збережи світло."),fnt_ui,global.col.muted);
wp_text(80,728,WP_VERSION+"  /  "+wp_tr("THE LAST WARD","ОСТАННІЙ ОБЕРІГ"),fnt_ui,global.col.muted);
if(global.page=="main"&&global.best_stars>0) {
    wp_stars(94,709,global.best_stars,9);
    wp_text(80+66+14,698,wp_tr("Best: ","Рекорд: ")+wp_clock(global.best_time),fnt_ui,global.col.gold);
}
wp_text(1288,728,wp_tr("Mouse or Tab + Enter","Миша або Tab + Enter"),fnt_ui,global.col.muted,fa_right);
if(global.effects) {
    for(var _i=0;_i<34;++_i){var _px=540+((_i*97+global.ui_time*8)mod 820),_py=760-((_i*53+global.ui_time*(8+_i mod 4))mod 760);wp_glow(_px,_py,5+2*sin(global.ui_time+_i),global.col.gold,.3+.2*sin(global.ui_time+_i));}
}
wp_overlay();
