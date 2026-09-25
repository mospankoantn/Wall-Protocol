function wp_text(_x,_y,_text,_font=fnt_ui,_color=undefined,_align=fa_left) {
    draw_set_font(_font);draw_set_color(is_undefined(_color)?global.col.text:_color);
    draw_set_halign(_align);draw_set_valign(fa_top);draw_set_alpha(1);
    draw_text(_x,_y,_text);
    draw_set_halign(fa_left);
}
function wp_wrap(_x,_y,_text,_width,_color=undefined) {
    draw_set_font(fnt_ui);draw_set_color(is_undefined(_color)?global.col.muted:_color);
    draw_set_halign(fa_left);draw_set_valign(fa_top);draw_set_alpha(1);
    draw_text_ext(_x,_y,_text,27,_width);
}
function wp_panel(_x,_y,_w,_h,_alpha=1) {
    draw_set_alpha(_alpha);draw_set_color(global.col.panel);draw_rectangle(_x,_y,_x+_w,_y+_h,false);
    draw_set_color(global.col.line);draw_rectangle(_x,_y,_x+_w,_y+_h,true);draw_set_alpha(1);
}
function wp_rule(_x,_y,_w) { draw_set_color(global.col.line);draw_line(_x,_y,_x+_w,_y); }
function wp_overlay() {
    if(global.page=="game" || global.page=="main" || global.page=="text" || global.page=="splash") return;
    draw_set_alpha(.80);draw_set_color(global.col.bg);draw_rectangle(0,0,WP_W,WP_H,false);draw_set_alpha(1);
    wp_panel(447,112,472,574,.98);
    draw_sprite_ext(spr_emblem,0,683,160,.28,.28,0,c_white,1);
    var _title="";var _sub="";
    switch(global.page) {
        case "language": _title="Language / Мова";_sub="Choose your language / Оберіть мову";break;
        case "options":_title=wp_tr("Options","Налаштування");_sub=wp_tr("Make yourself at home.","Налаштуйте гру під себе.");break;
        case "pause":_title=room==rm_test?wp_tr("Test range paused","Полігон на паузі"):wp_tr("Watch suspended","Варту призупинено");_sub=room==rm_test?wp_tr("Resume to try the test controls.","Продовжіть, щоб почати тестування."):wp_tr("The wall can wait a moment.","Стіна зачекає на ваше повернення.");break;
        case "confirm_new":_title=wp_tr("A new watch?","Нова варта?");_sub=wp_tr("This will replace your saved expedition.","Попередній похід буде перезаписано.");break;
        case "result":
            _title=obj_game.result==1?wp_tr("The wall holds","Стіна вистояла"):wp_tr("The ward has fallen","Оберіг зруйновано");
            _sub=wp_tr("Waves held: ","Відбиті хвилі: ")+string(obj_game.wave)+" / 8";
            wp_text(683,330,wp_tr("Enemies defeated: ","Знищено ворогів: ")+string(obj_game.kills),fnt_ui,global.col.gold,fa_center);
            wp_text(683,371,wp_tr("Core integrity: ","Міцність ядра: ")+string(obj_game.base_hp)+" / 20",fnt_ui,global.col.teal,fa_center);
            break;
    }
    wp_text(683,213,_title,fnt_heading,global.col.text,fa_center);
    wp_text(683,265,_sub,fnt_ui,global.col.muted,fa_center);
}
function wp_button_label(_action) {
    if(string_copy(_action,1,4)=="lab_")return wp_sandbox_label(_action);
    switch(_action) {
        case "sandbox":return wp_tr("Test room [F2]","Тестова кімната [F2]");
        case "continue":return wp_tr("Continue expedition","Продовжити похід");
        case "new":case "confirm_new":return wp_tr("Begin a new watch","Почати нову варту");
        case "retry":return wp_tr("Try again","Спробувати знову");
        case "options":return wp_tr("Options","Налаштування");
        case "guide":return wp_tr("Field guide","Польовий довідник");
        case "credits":return wp_tr("About & credits","Про гру та авторів");
        case "quit":return wp_tr("Exit game","Вийти з гри");
        case "back":return wp_tr("Back","Назад");
        case "cancel":return wp_tr("Keep current expedition","Залишити поточний похід");
        case "english":return "English";
        case "ukrainian":return "Українська";
        case "language":return wp_tr("Language: English","Мова: українська");
        case "music":return wp_tr("Music","Музика")+"     "+string(round(global.music_volume*100))+"%";
        case "sfx":return wp_tr("Sound effects","Звукові ефекти")+"     "+string(round(global.sfx_volume*100))+"%";
        case "fullscreen":return wp_tr("Fullscreen","Повний екран")+": "+(global.fullscreen?wp_tr("on","так"):wp_tr("off","ні"));
        case "effects":return wp_tr("Ambient effects","Ефекти оточення")+": "+(global.effects?wp_tr("on","так"):wp_tr("off","ні"));
        case "resume":return wp_tr("Resume","Продовжити");
        case "save":return wp_tr("Save expedition","Зберегти похід");
        case "load":return wp_tr("Load saved expedition","Завантажити похід");
        case "menu":return room==rm_test||(instance_exists(obj_game)&&obj_game.result!=0)?wp_tr("Main menu","Головне меню"):wp_tr("Save & main menu","Зберегти й до меню");
        case "text_next":return wp_tr("Next page","Наступна сторінка");
        case "wave":return instance_exists(obj_wave)&&obj_wave.active?wp_tr("Wave in progress","Хвиля триває"):wp_tr("Start wave  [Space]","Почати хвилю [Пробіл]");
        case "speed":return wp_tr("Speed ","Темп ")+string(obj_game.time_scale)+"x";
        case "pause":return wp_tr("Pause [Esc]","Пауза [Esc]");
        case "build0":case "build1":case "build2":
            var _k=real(string_char_at(_action,6));return string(_k+1)+"  "+wp_tower_name(_k)+"   "+string(global.towers[_k].cost);
        case "upgrade":
            var _t=wp_selected_tower();
            return instance_exists(_t)&&_t.level>=3?wp_tr("Maximum level","Найвищий рівень"):wp_tr("Upgrade [U]","Покращити [U]")+(instance_exists(_t)?"   "+string(wp_upgrade_cost(_t)):"");
        case "sell":
            var _t=wp_selected_tower();return wp_tr("Sell [X]","Продати [X]")+(instance_exists(_t)?"  +"+string(round(_t.invested*.7)):"");
    }
    return _action;
}
function wp_button_enabled(_action) {
    if(room==rm_test&&(_action=="save"||_action=="load"||_action=="guide"))return false;
    if(_action=="lab_cycle")return !obj_wave.active;
    switch(_action) {
        case "continue":case "load":return file_exists(global.file_prefix+"save.json") || file_exists(global.file_prefix+"save.bak");
        case "wave":return instance_exists(obj_wave)&&!obj_wave.active&&(room==rm_test||obj_game.wave<8);
        case "build0":case "build1":case "build2":
            var _k=real(string_char_at(_action,6));
            return instance_exists(obj_game.selected_pad)&&!instance_exists(wp_selected_tower())&&obj_game.gold>=global.towers[_k].cost;
        case "upgrade":var _t=wp_selected_tower();return instance_exists(_t)&&_t.level<3&&obj_game.gold>=wp_upgrade_cost(_t);
        case "sell":return instance_exists(wp_selected_tower());
    }
    return true;
}
function wp_action(_action) {
    wp_sound(snd_click,.65);
    if(string_copy(_action,1,4)=="lab_"){wp_sandbox_action(_action);return;}
    switch(_action) {
        case "sandbox":global.pending_load=undefined;global.resume_text=false;room_goto(rm_test);break;
        case "continue":case "load":wp_load();break;
        case "new":
            if(file_exists(global.file_prefix+"save.json")) wp_page("confirm_new");else wp_new_game();break;
        case "confirm_new":case "retry":wp_new_game();break;
        case "cancel":wp_page("main");break;
        case "quit":game_end();break;
        case "options":global.return_page=global.page;wp_page("options");break;
        case "language":wp_page("language");break;
        case "english":case "ukrainian":
            global.lang=_action=="english"?"en":"uk";global.language_chosen=true;global.notice_time=0;wp_settings_save();
            if(room==rm_boot)room_goto(rm_menu);else wp_page("options");break;
        case "music":global.music_volume=round(global.music_volume*10)/10+.1;if(global.music_volume>1.01)global.music_volume=0;wp_audio_apply();wp_settings_save();break;
        case "sfx":global.sfx_volume=round(global.sfx_volume*10)/10+.1;if(global.sfx_volume>1.01)global.sfx_volume=0;wp_settings_save();break;
        case "fullscreen":global.fullscreen=!global.fullscreen;window_set_fullscreen(global.fullscreen);wp_settings_save();break;
        case "effects":global.effects=!global.effects;wp_settings_save();break;
        case "back":
            if(room==rm_text){global.resume_text=global.text_return==rm_game;room_goto(global.text_return);}else wp_page(global.return_page);break;
        case "guide":case "credits":
            global.text_page=_action=="credits"?2:0;global.text_return=instance_exists(obj_game)?rm_game:rm_menu;
            if(instance_exists(obj_game)) { if(!wp_save()) break; global.pending_load=wp_read_save(); }
            room_goto(rm_text);break;
        case "text_next":global.text_page=(global.text_page+1)mod 3;break;
        case "pause":wp_page("pause");break;
        case "resume":wp_page("game");break;
        case "save":wp_save();break;
        case "menu":
            if(room!=rm_test&&instance_exists(obj_game)&&obj_game.result==0)if(!wp_save())break;
            global.pending_load=undefined;room_goto(rm_menu);break;
        case "wave":wp_start_wave();break;
        case "speed":obj_game.time_scale=obj_game.time_scale==1?2:1;break;
        case "build0":case "build1":case "build2":wp_build(obj_game.selected_pad,real(string_char_at(_action,6)));break;
        case "upgrade":wp_upgrade(wp_selected_tower());break;
        case "sell":wp_sell(wp_selected_tower());break;
    }
}
