ticks++;
switch(phase) {
    case 0:
        check(instance_number(obj_build_pad)==12,"12 authored build pads");
        check(array_length(obj_game.route)==10,"10 authored route nodes");
        check(instance_number(obj_app)==1&&instance_number(obj_audio)==1,"persistent services are unique");
        var _pad=wp_pad_by_key("pad_01");obj_game.selected_pad=_pad;
        var _gold=obj_game.gold;
        check(wp_build(_pad,0),"build tower");
        check(obj_game.gold==_gold-90&&!wp_build(_pad,1),"build cost and occupied-pad guard");
        check(wp_upgrade(_pad.tower),"upgrade tower");
        check(_pad.tower.level==2&&_pad.tower.invested==180,"upgrade investment");
        check(wp_sell(_pad.tower)&&obj_game.gold==226,"sell returns 70 percent of total investment");
        obj_game.gold=280;
        check(wp_build(_pad,0),"rebuild tower");
        check(wp_start_wave(),"start wave");
        phase=1;ticks=0;break;
    case 1:
        if(ticks<120)break;
        wp_page("pause");
        var _e=instance_find(obj_enemy,0);
        _e.slow_t=1.85;_e.slow_factor=.46;
        wp_spawn(obj_projectile,300,280,{shot_kind:2,target:_e,shot_power:1.58,tower_level:2});
        saved=wp_snapshot();
        check(array_length(saved.enemies)>0,"active enemies exist");
        check(array_length(saved.projectiles)>0,"snapshot includes in-flight projectiles");
        check(wp_validate_save(saved),"active battle schema validation");
        check(wp_save(),"save active battle");
        check(wp_save(),"save creates previous-state backup");
        var _read=wp_read_save();
        check(!is_undefined(_read),"JSON save readback");
        check(wp_restore(_read),"restore active battle");
        check(json_stringify(wp_snapshot())==json_stringify(saved),"exact battle round trip, including timers");
        var _bad=json_parse(json_stringify(saved));_bad.enemies[0].hp="bad";
        check(!wp_validate_save(_bad),"malformed enemy rejected");
        _bad=json_parse(json_stringify(saved));_bad.version=999;
        check(!wp_validate_save(_bad),"future save version rejected");
        _bad=json_parse(json_stringify(saved));_bad.route[0][0]+=20;
        check(!wp_restore(_bad),"changed map rejected before restore");
        check(json_stringify(wp_snapshot())==json_stringify(saved),"failed restore leaves battle untouched");
        var _f=file_text_open_write(global.file_prefix+"save.json");file_text_write_string(_f,"{broken");file_text_close(_f);
        check(wp_validate_save(wp_read_save()),"corrupt primary recovers backup");
        paused_snapshot=json_stringify(wp_snapshot());phase=2;ticks=0;break;
    case 2:
        if(ticks<12)break;
        check(paused_snapshot==json_stringify(wp_snapshot()),"pause freezes all simulation state");
        global.lang="uk";global.music_volume=.3;global.sfx_volume=.4;global.effects=false;wp_settings_save();
        global.lang="en";wp_settings_load();
        check(global.lang=="uk"&&global.music_volume==.3&&!global.effects,"settings and Ukrainian language persist");
        global.effects=true;global.notice_time=0;capture_name="wp_test_pause_uk.png";
        phase=3;ticks=0;break;
    case 3:
        if(ticks<4)break;
        wp_action("options");capture_name="wp_test_options_uk.png";phase=4;ticks=0;break;
    case 4:
        if(ticks<4)break;
        wp_action("back");check(global.page=="pause","options return to pause");
        wp_action("guide");phase=5;ticks=0;break;
    case 5:
        if(ticks<4)break;
        check(room==rm_text,"text room navigation");capture_name="wp_test_guide_uk.png";phase=6;ticks=0;break;
    case 6:
        if(ticks<4)break;
        wp_action("back");phase=7;ticks=0;break;
    case 7:
        if(ticks<4)break;
        check(room==rm_game&&global.page=="pause","field guide returns to paused game");
        check(json_stringify(wp_snapshot())==json_stringify(saved),"field guide preserves battle");
        wp_action("menu");phase=8;ticks=0;break;
    case 8:
        if(ticks<4)break;
        check(room==rm_menu,"main menu navigation");
        capture_name="wp_test_menu_uk.png";phase=9;ticks=0;break;
    case 9:
        if(ticks<4)break;
        global.lang="en";global.notice_time=0;capture_name="wp_test_menu_en.png";phase=10;ticks=0;break;
    case 10:
        if(ticks<4)break;
        wp_action("continue");phase=11;ticks=0;break;
    case 11:
        if(ticks<4)break;
        check(room==rm_game&&global.page=="pause","continue loads into pause");
        check(json_stringify(wp_snapshot())==json_stringify(saved),"menu continue restores battle");
        wp_new_game();phase=12;ticks=0;break;
    case 12:
        if(ticks<4)break;
        check(instance_number(obj_tower)==0&&instance_number(obj_enemy)==0&&obj_game.gold==280,"new game resets entities and economy");
        // Authored coordinates must survive fallback recovery.
        var _pad=wp_pad_by_key("pad_01");_pad.x+=9;
        with(obj_button)if(action=="pause")instance_destroy();
        var _count=instance_number(obj_button);wp_ensure_buttons();
        check(instance_number(obj_button)==_count+1,"missing button is restored once");
        check(_pad.x==257,"fallback preserves edited pad coordinates");_pad.x-=9;
        wp_ensure_buttons();check(instance_number(obj_button)==_count+1,"fallback is idempotent");
        campaign=0;last_wave=-1;phase=13;ticks=0;break;
    case 13:
        if(ticks>60000){check(false,"campaign timeout");break;}
        if(obj_game.result==2){check(false,"campaign must be winnable without bonus gold");break;}
        if(obj_game.result==1) {
            check(true,"eight waves won at "+string(campaign+1)+"x speed, HP "+string(obj_game.base_hp)+", kills "+string(obj_game.kills));
            capture_name="wp_test_victory_"+string(campaign)+".png";
            phase=14;ticks=0;break;
        }
        if(!obj_wave.active&&last_wave!=obj_game.wave) {
            last_wave=obj_game.wave;
            var _order=[1,4,6,7,3,9,0,5,11,10,8,2];
            var _kinds=[0,0,0,2,1,1,0,1,2,0,0,0];
            for(var _i=0;_i<array_length(_order);++_i) {
                var _n=_order[_i],_key="pad_"+(_n<10?"0":"")+string(_n),_p=wp_pad_by_key(_key);
                if(!instance_exists(_p.tower))wp_build(_p,_kinds[_i]);
            }
            for(var _j=0;_j<array_length(_order);++_j) {
                var _n=_order[_j],_p=wp_pad_by_key("pad_"+(_n<10?"0":"")+string(_n));
                if(instance_exists(_p.tower))wp_upgrade(_p.tower);
            }
            obj_game.time_scale=campaign+1;wp_start_wave();
            test_log("Campaign "+string(campaign+1)+", wave "+string(obj_game.wave)+", gold "+string(obj_game.gold));
        }
        if(obj_game.wave==5&&ticks mod 100==0)capture_name="wp_test_battle_en.png";
        break;
    case 14:
        if(ticks<4)break;
        if(campaign==0){campaign=1;last_wave=-1;wp_new_game();phase=13;ticks=0;break;}
        wp_new_game();phase=15;ticks=0;break;
    case 15:
        if(ticks<4)break;
        // Exercise actual breach/death path at the end of the editable route.
        obj_game.base_hp=1;obj_game.wave=1;obj_wave.active=true;obj_wave.queue=[];
        var _r=obj_game.route,_last=array_length(_r)-1;
        var _enemy=wp_spawn(obj_skeleton,_r[_last][0],_r[_last][1]);_enemy.path_i=_last-1;
        phase=16;ticks=0;break;
    case 16:
        if(ticks<4)break;
        check(obj_game.result==2&&global.page=="result","core breach causes defeat");
        capture_name="wp_test_defeat_en.png";phase=17;ticks=0;break;
    case 17:
        if(ticks<4)break;
        wp_new_game();phase=18;ticks=0;break;
    case 18:
        if(ticks<4)break;
        wp_page("pause");wp_save(true);wp_save(true);
        campaign_save=json_stringify(wp_read_json(global.file_prefix+"save.json"));
        campaign_backup=json_stringify(wp_read_json(global.file_prefix+"save.bak"));
        wp_action("menu");phase=19;ticks=0;break;
    case 19:
        if(ticks<4)break;
        wp_action("sandbox");phase=20;ticks=0;break;
    case 20:
        if(ticks<4)break;
        check(room==rm_test&&global.page=="pause","test room opens paused from main menu");
        check(instance_number(obj_sandbox)==1&&instance_number(obj_tower)==3&&instance_number(obj_enemy)==4,"authored test controller, three towers and four enemies");
        check(obj_game.gold==5000&&obj_sandbox.invulnerable&&obj_game.wave==4,"editable test starting values");
        check(instance_number(obj_build_pad)==6&&array_length(obj_game.route)==6,"dedicated authored test map");
        var _e=instance_find(obj_runner,0);
        check(_e.path_i==2&&_e.progress==550,"authored enemy progress matches its route position");
        check(!wp_save(true)&&!wp_load(),"test room blocks expedition save and load");
        wp_action("resume");global.lang="en";global.notice_time=0;capture_name="wp_test_sandbox_en.png";
        phase=21;ticks=0;break;
    case 21:
        if(ticks<4)break;
        obj_app.autosave_timer=0;
        global.lang="uk";capture_name="wp_test_sandbox_uk.png";phase=22;ticks=0;break;
    case 22:
        if(ticks<4)break;
        check(campaign_save==json_stringify(wp_read_json(global.file_prefix+"save.json"))&&campaign_backup==json_stringify(wp_read_json(global.file_prefix+"save.bak")),"periodic autosave leaves expedition files untouched in test room");
        wp_action("lab_clear");
        check(instance_number(obj_enemy)==0&&instance_number(obj_projectile)==0&&!obj_wave.active,"test clear resets enemies, projectiles and wave queue");
        for(var _k=0;_k<4;++_k)wp_action("lab_spawn"+string(_k));
        wp_action("lab_swarm");
        check(instance_number(obj_enemy)==16&&instance_number(obj_boss)==1&&!obj_wave.active,"manual spawn of every enemy and swarm");
        wp_action("lab_clear");var _g=obj_game.gold;wp_action("lab_gold");
        check(obj_game.gold==_g+1000,"test aether grant");
        obj_game.base_hp=3;wp_action("lab_heal");check(obj_game.base_hp==20,"test core repair");
        for(var _k=0;_k<4;++_k)wp_action("lab_cycle");
        check(obj_sandbox.test_wave==8&&wp_button_enabled("wave"),"select final test wave");
        check(wp_start_wave()&&obj_game.wave==8&&obj_wave.queue[array_length(obj_wave.queue)-1]==3,"test final wave includes boss");
        wp_action("lab_cycle");check(obj_sandbox.test_wave==8,"wave selector locked during assault");
        wp_action("lab_clear");
        var _e=wp_sandbox_spawn(3),_r=obj_game.route,_last=array_length(_r)-1;
        _e.x=_r[_last][0];_e.y=_r[_last][1];_e.path_i=_last-1;
        phase=23;ticks=0;break;
    case 23:
        if(ticks<4)break;
        check(obj_game.base_hp==20&&obj_game.result==0,"test invulnerability prevents breach damage without ending manual spawns");
        wp_action("lab_god");
        var _e=wp_sandbox_spawn(0),_r=obj_game.route,_last=array_length(_r)-1;
        _e.x=_r[_last][0];_e.y=_r[_last][1];_e.path_i=_last-1;
        phase=24;ticks=0;break;
    case 24:
        if(ticks<4)break;
        check(obj_game.base_hp==19,"test invulnerability can be disabled");
        wp_action("lab_victory");check(global.page=="result"&&obj_game.result==1,"test victory screen");
        check(campaign_save==json_stringify(wp_read_json(global.file_prefix+"save.json"))&&campaign_backup==json_stringify(wp_read_json(global.file_prefix+"save.bak")),"test victory preserves primary and backup expedition saves");
        wp_action("retry");phase=25;ticks=0;break;
    case 25:
        if(ticks<4)break;
        check(room==rm_test&&obj_game.result==0&&obj_game.gold==5000&&instance_number(obj_enemy)==4&&global.page=="pause","retry restores test room and authored entities");
        wp_action("resume");wp_action("lab_defeat");check(obj_game.result==2&&obj_game.base_hp==0,"test defeat screen");
        check(campaign_save==json_stringify(wp_read_json(global.file_prefix+"save.json"))&&campaign_backup==json_stringify(wp_read_json(global.file_prefix+"save.bak")),"test defeat preserves primary and backup expedition saves");
        wp_action("retry");phase=26;ticks=0;break;
    case 26:
        if(ticks<4)break;
        var _moved=noone;
        with(obj_button)if(action=="lab_gold"){x+=5;_moved=id;}
        with(obj_button)if(action=="lab_heal")instance_destroy();
        var _count=instance_number(obj_button);wp_ensure_buttons();wp_ensure_buttons();
        check(instance_number(obj_button)==_count+1&&_moved.x==233,"test button fallback is idempotent and preserves editor positions");
        wp_action("lab_reset");phase=27;ticks=0;break;
    case 27:
        if(ticks<4)break;
        check(room==rm_test&&global.page=="pause"&&instance_number(obj_tower)==3,"test reset action restarts room");
        wp_action("menu");phase=28;ticks=0;break;
    case 28:
        if(ticks<4)break;
        check(room==rm_menu,"test pause returns to main menu without saving");
        wp_action("continue");phase=29;ticks=0;break;
    case 29:
        if(ticks<4)break;
        check(room==rm_game&&global.page=="pause"&&campaign_save==json_stringify(wp_snapshot()),"expedition resumes unchanged after test room");
        test_log("ALL TESTS PASSED: "+string(checks));
        wp_write_json("wp_test_results.json",{passed:true,checks:checks,log:global.test_log});
        game_end();break;
}
