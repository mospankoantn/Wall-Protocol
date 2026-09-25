#macro WP_W 1366
#macro WP_H 768
#macro WP_FIELD 1060
#macro WP_STUDIO "Eclipse Wire"
#macro WP_SAVE_VERSION 2

function wp_init() {
    if (variable_global_exists("wp_ready")) return;
    global.wp_ready = true;
    global.test_mode = false;
    for (var _i = 1; _i <= parameter_count(); ++_i) {
        if (parameter_string(_i) == "--wp-test") global.test_mode = true;
    }
    global.file_prefix = global.test_mode ? "wp_test_" : "wp_";
    global.lang = "en";
    global.language_chosen = false;
    global.music_volume = 0.45;
    global.sfx_volume = 0.65;
    global.fullscreen = false;
    global.effects = true;
    global.page = "main";
    global.return_page = "main";
    global.text_page = 0;
    global.text_return = rm_menu;
    global.pending_load = undefined;
    global.resume_text = false;
    global.notice = "";
    global.notice_time = 0;
    global.ui_time = 0;
    global.focus_button = noone;
    global.input_lock = 0;
    global.col = {bg:make_color_rgb(10,18,25),panel:make_color_rgb(17,29,37),line:make_color_rgb(57,77,83),text:make_color_rgb(230,229,215),muted:make_color_rgb(146,166,170),gold:make_color_rgb(213,175,101),teal:make_color_rgb(92,207,204),red:make_color_rgb(225,102,103),purple:make_color_rgb(167,125,231)};
    global.towers = [
        {cost:90,damage:20,range:175,rate:0.55,sprite:spr_archer,object:obj_tower_archer,sound:snd_arrow},
        {cost:135,damage:34,range:165,rate:1.05,sprite:spr_rune,object:obj_tower_rune,sound:snd_rune},
        {cost:110,damage:11,range:155,rate:0.72,sprite:spr_frost,object:obj_tower_frost,sound:snd_frost}
    ];
    global.enemy_objects = [obj_skeleton,obj_brute,obj_runner,obj_boss];
    global.enemy_sprites = [spr_skeleton,spr_brute,spr_runner,spr_boss];
    global.default_route = [[70,385],[145,385],[145,210],[350,210],[350,525],[560,525],[560,300],[775,300],[775,475],[965,475]];
    global.default_pads = [[84,266],[248,320],[250,116],[454,159],[460,406],[469,635],[660,413],[670,203],[870,203],[885,365],[891,611],[711,619]];
    wp_settings_load();
    game_set_speed(60,gamespeed_fps);
    window_set_caption("Wall Protocol | " + WP_STUDIO);
    window_set_fullscreen(global.fullscreen);
    gpu_set_texfilter(true);
    draw_set_circle_precision(32);
}

function wp_tr(_en, _uk) { return global.lang == "uk" ? _uk : _en; }
function wp_tower_name(_kind) {
    return [wp_tr("Warden ballista","Вартова баліста"),wp_tr("Runic spire","Рунний шпиль"),wp_tr("Frost ward","Крижаний оберіг")][_kind];
}
function wp_tower_desc(_kind) {
    return [wp_tr("Fast, precise single-target shots.","Швидкі точні постріли в одну ціль."),wp_tr("Explosions damage nearby enemies.","Вибух завдає шкоди групі ворогів."),wp_tr("Slows enemies, buying you time.","Сповільнює ворогів, виграючи час.")][_kind];
}
function wp_notice(_text) { global.notice = _text; global.notice_time = 3; }
function wp_page(_page) {
    global.page = _page;
    global.focus_button = noone;
    global.input_lock = 2;
}
function wp_active() {
    return instance_exists(obj_game) && obj_game.ready && obj_game.result == 0 && global.page == "game";
}
function wp_dt() { return wp_active() ? obj_game.sim_dt : 0; }
function wp_spawn(_obj,_x,_y,_vars=undefined) {
    var _layer = layer_get_id("Instances");
    if (_layer == -1) _layer = layer_create(0,"Instances");
    if (is_undefined(_vars)) return instance_create_layer(_x,_y,_layer,_obj);
    return instance_create_layer(_x,_y,_layer,_obj,_vars);
}

function wp_wave_list(_wave) {
    var _list=[];
    var _count=6+_wave*2;
    for(var _i=0;_i<_count;++_i) {
        var _kind=0;
        if(_wave>=2 && _i mod 4==2) _kind=2;
        if(_wave>=4 && _i mod 5==4) _kind=1;
        array_push(_list,_kind);
    }
    if(_wave==8) array_push(_list,3);
    return _list;
}
function wp_wave_summary(_wave) {
    var _list=wp_wave_list(_wave),_counts=[0,0,0,0];
    for(var _i=0;_i<array_length(_list);++_i) _counts[_list[_i]]++;
    var _names=[wp_tr("Risen","Мерці"),wp_tr("Brutes","Громили"),wp_tr("Runners","Бігуни"),wp_tr("Colossus","Колос")];
    var _out="";
    for(var _j=0;_j<4;++_j) if(_counts[_j]>0) _out+=(_out==""?"":"  /  ")+_names[_j]+" "+string(_counts[_j]);
    return _out;
}
