draw_clear(c_black);
var _alpha=clamp(timer/.7,0,1);
draw_sprite_stretched_ext(spr_studio,0,323,100,720,480,c_white,_alpha);
wp_text(683,610,WP_STUDIO,fnt_heading,global.col.text,fa_center);
wp_text(683,668,wp_tr("P R E S E N T S","П Р Е Д С Т А В Л Я Є"),fnt_ui,global.col.muted,fa_center);
wp_overlay();
