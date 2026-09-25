/// Explicit --wp-test only. Uses isolated wp_test_* files, never the player's save.
if(!global.test_mode){instance_destroy();exit;}
if(instance_number(obj_test)>1){instance_destroy();exit;}
persistent=true;phase=0;ticks=0;capture_name="";checks=0;campaign=0;last_wave=-1;
game_set_speed(1000,gamespeed_fps);display_reset(0,false);
global.test_log="";
test_log=function(_s){global.test_log+=_s+"\n";show_debug_message(_s);};
check=function(_condition,_label) {
    if(!_condition){test_log("FAIL: "+_label);wp_write_json("wp_test_results.json",{passed:false,checks:checks,log:global.test_log});game_end();throw _label;}
    checks++;test_log("PASS: "+_label);
};
test_log("Wall Protocol runtime integration test");
