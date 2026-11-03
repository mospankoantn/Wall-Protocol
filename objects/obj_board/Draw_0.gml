draw_clear(global.col.bg);
// Screen shake: everything below the HUD is drawn through a shifted world matrix (reset at the top of obj_hud).
if(global.shake>0)matrix_set(matrix_world,matrix_build(random_range(-1,1)*global.shake*14,random_range(-1,1)*global.shake*14,0,0,0,0,1,1,1));
draw_set_color(make_color_rgb(27,43,43));draw_rectangle(0,0,WP_FIELD,WP_H,false);
var _th=global.theme;   // per-map look (ground, road, fog, weather); map 0 equals the 1.3 look
draw_sprite_tiled_ext(_th.ground,0,0,0,1,1,_th.blend,1);
if(instance_exists(obj_game)&&obj_game.ready) {
    var _route=obj_game.route;
    for(var _pass=0;_pass<3;++_pass) {
        var _width=[78,65,51][_pass];
        draw_set_color(_th.road[_pass]);
        for(var _i=0;_i<array_length(_route)-1;++_i) {
            draw_line_width(_route[_i][0],_route[_i][1],_route[_i+1][0],_route[_i+1][1],_width);
            draw_circle(_route[_i][0],_route[_i][1],_width/2,false);
        }
        var _last=_route[array_length(_route)-1];draw_circle(_last[0],_last[1],_width/2,false);
    }
    for(var _s=0;_s<array_length(_route)-1;++_s) {
        var _a=_route[_s],_b=_route[_s+1],_len=point_distance(_a[0],_a[1],_b[0],_b[1]),_dir=point_direction(_a[0],_a[1],_b[0],_b[1]);
        for(var _d=9;_d<_len;_d+=24) {
            var _px=_a[0]+lengthdir_x(_d,_dir),_py=_a[1]+lengthdir_y(_d,_dir);
            draw_set_color(_th.stone[0]);draw_line(_px+lengthdir_x(23,_dir+90),_py+lengthdir_y(23,_dir+90),_px+lengthdir_x(23,_dir-90),_py+lengthdir_y(23,_dir-90));
            draw_line(_px,_py,_px+lengthdir_x(24,_dir),_py+lengthdir_y(24,_dir));
            draw_set_color(_th.stone[1]);
            draw_line(_px+lengthdir_x(21,_dir+90)+2,_py+lengthdir_y(21,_dir+90)+2,_px+lengthdir_x(2,_dir-90)+2,_py+lengthdir_y(2,_dir-90)+2);
            draw_set_color(merge_color(_th.stone[1],c_white,.08));draw_circle(_px+3,_py+3,1.3,false);
        }
    }
}
if(global.effects) {
    // Two slow fog layers drifting in opposite directions, then floating motes of light.
    draw_sprite_tiled_ext(spr_mist,0,global.ui_time*9,global.ui_time*3,1.8,1.8,_th.fog[0],_th.fog_a[0]);
    draw_sprite_tiled_ext(spr_mist,0,-global.ui_time*6+90,global.ui_time*5,2.6,2.6,_th.fog[1],_th.fog_a[1]);
    for(var _m=0;_m<26;++_m) {
        var _mx=(_m*79+global.ui_time*(6+_m mod 5))mod 1040,_my=96+((_m*131-global.ui_time*(5+_m mod 4))mod 570+570)mod 570;
        wp_glow(_mx,_my,7+3*sin(global.ui_time*1.3+_m),_m mod 3==0?_th.mote[0]:_th.mote[1],.22+.12*sin(global.ui_time+_m*1.7));
    }
    // Weather of the map: 1 snow, 2 rising embers, 3 drifting spores, 4 slow violet wisps.
    if(_th.weather>0) {
        for(var _w=0;_w<70;++_w) {
            var _wx,_wy,_wr,_wc=_th.mote[_w mod 2],_wa=.5;
            switch(_th.weather) {
                case 1: _wx=((_w*61+global.ui_time*(7+_w mod 5)+sin(global.ui_time*.8+_w)*22)mod 1060+1060)mod 1060;_wy=77+((_w*97+global.ui_time*(30+_w mod 7*5))mod 620);_wr=2+(_w mod 3);_wa=.65;break;
                case 2: _wx=((_w*53+sin(global.ui_time*.7+_w)*26)mod 1060+1060)mod 1060;_wy=696-((_w*89+global.ui_time*(24+_w mod 6*6))mod 620);_wr=2+(_w mod 2);_wa=.55*(.5+.5*sin(global.ui_time*3+_w));break;
                case 3: _wx=((_w*71+global.ui_time*(4+_w mod 4)+sin(global.ui_time*.5+_w)*30)mod 1060+1060)mod 1060;_wy=96+((_w*113+sin(global.ui_time*.6+_w*2)*40)mod 580);_wr=3+(_w mod 3);_wa=.3+.25*sin(global.ui_time*1.2+_w);break;
                default: _wx=((_w*83+sin(global.ui_time*.4+_w)*40)mod 1060+1060)mod 1060;_wy=696-((_w*67+global.ui_time*(8+_w mod 5*2))mod 620);_wr=5+(_w mod 4);_wa=.3+.2*sin(global.ui_time+_w);break;
            }
            wp_glow(_wx,_wy,_wr*1.6,_wc,_wa);
        }
    }
}
draw_sprite_stretched_ext(spr_vignette,0,0,0,WP_FIELD,WP_H,c_black,.62);
