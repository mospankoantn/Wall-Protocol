if(!instance_exists(obj_game)||!obj_game.ready)exit;
var _g=obj_game;
var _low=_g.base_hp<=6;
// Wave progress: enemies still to spawn plus those alive on the road.
var _total=array_length(obj_wave.queue);
var _left=obj_wave.active?instance_number(obj_enemy)+max(0,_total-obj_wave.spawn_index):0;
var _progress=(obj_wave.active&&_total>0)?clamp(1-_left/_total,0,1):0;
wp_panel(0,0,1060,77,.97);
draw_sprite_ext(spr_emblem,0,42,38,.23,.23,0,c_white,1);
wp_text(79,14,"WALL PROTOCOL",fnt_ui,global.col.gold);
wp_text(79,41,wp_tr("THE LAST WARD","ОСТАННІЙ ОБЕРІГ"),fnt_ui,global.col.muted);
wp_text(433,15,wp_tr("CORE INTEGRITY","МІЦНІСТЬ ЯДРА"),fnt_ui,global.col.muted);
draw_set_color(global.col.line);draw_rectangle(434,46,634,55,false);
draw_set_color(_low?merge_color(global.col.red,c_white,.18+.18*sin(global.ui_time*8)):global.col.teal);draw_rectangle(434,46,434+200*max(0,_g.base_hp/20),55,false);
wp_text(653,35,string(max(0,_g.base_hp))+" / 20",fnt_ui,_low?global.col.red:global.col.text);
wp_text(819,15,wp_tr("WAVE","ХВИЛЯ"),fnt_ui,global.col.muted);
wp_text(819,41,string(_g.wave)+" / 8",fnt_ui,global.col.gold);
draw_set_color(global.col.line);draw_rectangle(886,46,970,55,false);
draw_set_color(global.col.gold);draw_rectangle(886,46,886+84*_progress,55,false);
wp_text(1028,41,wp_clock(_g.elapsed),fnt_ui,global.col.muted,fa_right);
wp_panel(1060,0,306,768,.99);
wp_text(1084,26,wp_tr("DEFENSE COMMAND","ОБОРОНА РУБЕЖУ"),fnt_ui,global.col.gold);
draw_sprite_ext(spr_aether,0,1103,83,.57,.57,0,c_white,1);
wp_text(1140,55,string(_g.gold),fnt_heading,global.col.text);
wp_text(1141,99,wp_tr("aether available","доступного ефіру"),fnt_ui,global.col.muted);
wp_rule(1084,142,258);
wp_text(1084,288,obj_wave.active?wp_tr("CURRENT ASSAULT","ПОТОЧНИЙ ШТУРМ"):wp_tr("NEXT ASSAULT","НАСТУПНИЙ ШТУРМ"),fnt_ui,global.col.gold);
if(obj_wave.active)wp_text(1342,288,wp_tr(string(_left)+" left","ще "+string(_left)),fnt_ui,global.col.muted,fa_right);
// Composition of the wave as enemy icons with counts. Hover an icon to read the enemy name.
var _counts=wp_wave_counts(room==rm_test?obj_sandbox.test_wave:clamp(_g.wave+(obj_wave.active?0:1),1,8));
var _names=[wp_tr("Risen","Мерці"),wp_tr("Brutes","Громили"),wp_tr("Runners","Бігуни"),wp_tr("Colossus","Колос")];
var _slot=0;
for(var _k=0;_k<4;++_k) {
    if(_counts[_k]<=0)continue;
    var _sx=1084+_slot*64;
    draw_sprite_ext(global.enemy_sprites[_k],0,_sx+14,332,.48,.48,0,c_white,1);
    wp_text(_sx+32,320,string(_counts[_k]),fnt_ui,global.col.text);
    if(point_in_rectangle(mouse_x,mouse_y,_sx,314,_sx+62,350))wp_text(1084,352,_names[_k],fnt_ui,global.col.muted);
    _slot++;
}
var _tower=wp_selected_tower(),_pad=_g.selected_pad;
wp_panel(0,696,1060,72,.94);
if(instance_exists(_pad)) {
    wp_text(28,708,instance_exists(_tower)?wp_tower_name(_tower.tower_kind)+"  /  "+wp_tr("Level ","Рівень ")+string(_tower.level):wp_tr("Empty foundation / Choose a defense","Вільна основа / Оберіть оборону"),fnt_ui,global.col.gold);
    if(instance_exists(_tower)) {
        var _cfg=global.towers[_tower.tower_kind];
        wp_text(28,738,wp_tr("Damage ","Шкода ")+string(round(_cfg.damage*(1+(_tower.level-1)*.58)))+"   /   "+wp_tr("Range ","Радіус ")+string(_cfg.range+(_tower.level-1)*10),fnt_ui,global.col.muted);
    }
} else {
    wp_text(28,710,wp_tr("Select a stone foundation to raise a tower.","Оберіть кам'яну основу, щоб збудувати вежу."),fnt_ui,global.col.gold);
    wp_text(28,740,wp_tr("1/2/3 Build   U Upgrade   X Sell   T Target   F Speed   Esc Pause","1/2/3 Будувати   U Покращити   X Продати   T Ціль   F Темп   Esc Пауза"),fnt_ui,global.col.muted);
}
// Inspectable tower stats appear beside the field, away from the buttons.
if(global.page=="game"&&room!=rm_test)with(obj_button) {
    if(hovered&&string_copy(action,1,5)=="build") {
        var _kind=real(string_char_at(action,6)),_cfg=global.towers[_kind];
        wp_panel(708,555,335,132,.98);
        wp_text(724,568,wp_tower_name(_kind),fnt_ui,global.col.gold);
        wp_wrap(724,599,wp_tower_desc(_kind),300);
        wp_text(724,654,wp_tr("DMG ","ШК ")+string(_cfg.damage)+" / "+wp_tr("RNG ","РАД ")+string(_cfg.range)+" / "+string(_cfg.rate)+wp_tr(" s"," с"),fnt_ui,global.col.teal);
    } else if(hovered&&action=="upgrade") {
        // Preview of what the next level changes (same formulas as obj_tower / obj_projectile).
        var _up=wp_selected_tower();
        if(instance_exists(_up)&&_up.level<3) {
            var _uk=_up.tower_kind,_uc=global.towers[_uk],_l=_up.level;
            wp_panel(708,555,335,132,.98);
            wp_text(724,568,wp_tower_name(_uk)+"  /  "+wp_tr("Level ","Рівень ")+string(_l)+" > "+string(_l+1),fnt_ui,global.col.gold);
            wp_text(724,599,wp_tr("Damage ","Шкода ")+string(round(_uc.damage*(1+(_l-1)*.58)))+" > "+string(round(_uc.damage*(1+_l*.58))),fnt_ui,global.col.text);
            wp_text(724,626,wp_tr("Range ","Радіус ")+string(_uc.range+(_l-1)*10)+" > "+string(_uc.range+_l*10),fnt_ui,global.col.text);
            if(_uk==0)wp_text(724,653,wp_tr("Shot every ","Постріл кожні ")+string(round(_uc.rate/(1+(_l-1)*.12)*100)/100)+" > "+string(round(_uc.rate/(1+_l*.12)*100)/100)+wp_tr(" s"," с"),fnt_ui,global.col.teal);
            else if(_uk==1)wp_text(724,653,wp_tr("Blast radius ","Радіус вибуху ")+string(58+(_l-1)*7)+" > "+string(58+_l*7),fnt_ui,global.col.teal);
            else wp_text(724,653,wp_tr("Slow ","Сповільнення ")+string(round((1-max(.42,.6-(_l-1)*.07))*100))+"% > "+string(round((1-max(.42,.6-_l*.07))*100))+"%",fnt_ui,global.col.teal);
        }
    }
}
wp_text(1084,719,room==rm_test?wp_tr("Test: saves disabled","Тест: запис вимкнено"):wp_tr("Auto-save enabled","Автозбереження ввімкнено"),fnt_ui,global.col.muted);
// The core label lives here (not in obj_core) so decorations can never cover it.
if(instance_exists(obj_core)) {
    var _core_label=wp_tr("THE CORE","ЯДРО");
    draw_set_font(fnt_ui);
    var _cw=string_width(_core_label)+20;
    draw_set_color(global.col.bg);draw_set_alpha(.72);
    draw_roundrect(obj_core.x-_cw/2,obj_core.y+48,obj_core.x+_cw/2,obj_core.y+75,false);
    draw_set_alpha(1);
    wp_text(obj_core.x,obj_core.y+51,_core_label,fnt_ui,global.col.teal,fa_center);
    // Red frame while the core is being hit.
    if(obj_core.flash>0) {
        draw_set_color(global.col.red);draw_set_alpha(min(.4,obj_core.flash*.7));
        draw_rectangle(0,77,WP_FIELD,113,false);draw_rectangle(0,660,WP_FIELD,696,false);
        draw_rectangle(0,113,36,660,false);draw_rectangle(WP_FIELD-36,113,WP_FIELD,660,false);
        draw_set_alpha(1);
    }
}
// Wave banner: fades in, holds, fades out (timer lives in obj_wave and only runs while the game runs).
if(obj_wave.banner_t>0&&global.page=="game") {
    var _bt=obj_wave.banner_t,_ba=clamp(min((2.4-_bt)/.3,_bt/.6),0,1),_final=_g.wave>=8;
    var _bc=_final?global.col.red:global.col.gold;
    draw_set_color(global.col.bg);draw_set_alpha(.55*_ba);draw_rectangle(0,282,WP_FIELD,372,false);
    draw_set_color(_bc);draw_set_alpha(.5*_ba);draw_line(0,282,WP_FIELD,282);draw_line(0,372,WP_FIELD,372);
    draw_set_alpha(1);
    wp_text_a(WP_FIELD/2,291,_final?wp_tr("FINAL WAVE","ОСТАННЯ ХВИЛЯ"):wp_tr("WAVE ","ХВИЛЯ ")+string(_g.wave),fnt_heading,_bc,fa_center,_ba);
    wp_text_a(WP_FIELD/2,336,_final?wp_tr("The Bone Colossus marches.","Кістяний колос наближається."):wp_tr("The dead are on the road.","Мерці на дорозі."),fnt_ui,global.col.muted,fa_center,_ba);
}
wp_overlay();
