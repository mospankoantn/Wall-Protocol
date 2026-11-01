draw_clear(global.col.bg);
draw_sprite_stretched(spr_menu_art,0,0,0,WP_W,WP_H);
draw_set_alpha(.25);draw_set_color(global.col.bg);draw_rectangle(0,0,510,WP_H,false);draw_set_alpha(1);
wp_text(80,62,WP_STUDIO+"  /  "+wp_tr("A TOWER DEFENSE TALE","ІСТОРІЯ ПРО ОСТАННЮ ВАРТУ"),fnt_ui,global.col.gold);
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
    for(var _i=0;_i<28;++_i){var _px=540+((_i*97+global.ui_time*8)mod 820),_py=760-((_i*53+global.ui_time*(8+_i mod 4))mod 760);draw_set_alpha(.2+.15*sin(global.ui_time+_i));draw_set_color(global.col.gold);draw_circle(_px,_py,1.4,false);}
    draw_set_alpha(1);
}
wp_overlay();
