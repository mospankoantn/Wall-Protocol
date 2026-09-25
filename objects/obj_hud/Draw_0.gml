if(!instance_exists(obj_game)||!obj_game.ready)exit;
var _g=obj_game;
wp_panel(0,0,1060,77,.97);
draw_sprite_ext(spr_emblem,0,42,38,.23,.23,0,c_white,1);
wp_text(79,14,"WALL PROTOCOL",fnt_ui,global.col.gold);
wp_text(79,41,wp_tr("THE LAST WARD","ОСТАННІЙ ОБЕРІГ"),fnt_ui,global.col.muted);
wp_text(433,15,wp_tr("CORE INTEGRITY","МІЦНІСТЬ ЯДРА"),fnt_ui,global.col.muted);
draw_set_color(global.col.line);draw_rectangle(434,46,634,55,false);
draw_set_color(_g.base_hp>6?global.col.teal:global.col.red);draw_rectangle(434,46,434+200*max(0,_g.base_hp/20),55,false);
wp_text(653,35,string(max(0,_g.base_hp))+" / 20",fnt_ui,global.col.text);
wp_text(819,15,wp_tr("WAVE","ХВИЛЯ"),fnt_ui,global.col.muted);
wp_text(819,41,string(_g.wave)+" / 8",fnt_ui,global.col.gold);
wp_text(1028,41,string(floor(_g.elapsed/60))+":"+(floor(_g.elapsed)mod 60<10?"0":"")+string(floor(_g.elapsed)mod 60),fnt_ui,global.col.muted,fa_right);
wp_panel(1060,0,306,768,.99);
wp_text(1084,26,wp_tr("DEFENSE COMMAND","ОБОРОНА РУБЕЖУ"),fnt_ui,global.col.gold);
draw_sprite_ext(spr_aether,0,1103,83,.57,.57,0,c_white,1);
wp_text(1140,55,string(_g.gold),fnt_heading,global.col.text);
wp_text(1141,99,wp_tr("aether available","доступного ефіру"),fnt_ui,global.col.muted);
wp_rule(1084,142,258);
wp_text(1084,288,wp_tr("NEXT ASSAULT","НАСТУПНИЙ ШТУРМ"),fnt_ui,global.col.gold);
wp_wrap(1084,320,wp_wave_summary(min(8,_g.wave+(obj_wave.active?0:1))),258);
var _tower=wp_selected_tower(),_pad=_g.selected_pad;
if(instance_exists(_pad)) {
    wp_text(28,708,instance_exists(_tower)?wp_tower_name(_tower.tower_kind)+"  /  "+wp_tr("Level ","Рівень ")+string(_tower.level):wp_tr("Empty foundation / Choose a defense","Вільна основа / Оберіть оборону"),fnt_ui,global.col.gold);
    if(instance_exists(_tower)) {
        var _cfg=global.towers[_tower.tower_kind];
        wp_text(28,738,wp_tr("Damage ","Шкода ")+string(round(_cfg.damage*(1+(_tower.level-1)*.58)))+"   /   "+wp_tr("Range ","Радіус ")+string(_cfg.range+(_tower.level-1)*10),fnt_ui,global.col.muted);
    }
} else {
    wp_text(28,710,wp_tr("Select a stone foundation to raise a tower.","Оберіть кам'яну основу, щоб збудувати вежу."),fnt_ui,global.col.gold);
    wp_text(28,740,wp_tr("1/2/3 Build   U Upgrade   X Sell   F Speed   Esc Pause","1/2/3 Будувати   U Покращити   X Продати   F Темп   Esc Пауза"),fnt_ui,global.col.muted);
}
// Inspectable tower stats appear beside the field, away from the buttons.
if(global.page=="game")with(obj_button) {
    if(hovered&&string_copy(action,1,5)=="build") {
        var _kind=real(string_char_at(action,6)),_cfg=global.towers[_kind];
        wp_panel(708,555,335,132,.98);
        wp_text(724,568,wp_tower_name(_kind),fnt_ui,global.col.gold);
        wp_wrap(724,599,wp_tower_desc(_kind),300);
        wp_text(724,654,wp_tr("DMG ","ШК ")+string(_cfg.damage)+" / "+wp_tr("RNG ","РАД ")+string(_cfg.range)+" / "+string(_cfg.rate)+wp_tr(" s"," с"),fnt_ui,global.col.teal);
    }
}
wp_text(1084,719,wp_tr("Auto-save enabled","Автозбереження ввімкнено"),fnt_ui,global.col.muted);
wp_overlay();
