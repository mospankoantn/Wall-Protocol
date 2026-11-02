draw_clear(global.col.bg);
// Screen shake: everything below the HUD is drawn through a shifted world matrix (reset at the top of obj_hud).
if(global.shake>0)matrix_set(matrix_world,matrix_build(random_range(-1,1)*global.shake*14,random_range(-1,1)*global.shake*14,0,0,0,0,1,1,1));
draw_set_color(make_color_rgb(27,43,43));draw_rectangle(0,0,WP_FIELD,WP_H,false);
draw_sprite_tiled_ext(spr_ground,0,0,0,1,1,make_color_rgb(155,175,175),1);
if(instance_exists(obj_game)&&obj_game.ready) {
    var _route=obj_game.route;
    for(var _pass=0;_pass<3;++_pass) {
        var _width=[78,65,51][_pass];
        draw_set_color([make_color_rgb(16,26,29),make_color_rgb(53,63,63),make_color_rgb(73,79,75)][_pass]);
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
            draw_set_color(make_color_rgb(59,67,65));draw_line(_px+lengthdir_x(23,_dir+90),_py+lengthdir_y(23,_dir+90),_px+lengthdir_x(23,_dir-90),_py+lengthdir_y(23,_dir-90));
            draw_line(_px,_py,_px+lengthdir_x(24,_dir),_py+lengthdir_y(24,_dir));
            draw_set_color(make_color_rgb(85+_s mod 6,91,83));
            draw_line(_px+lengthdir_x(21,_dir+90)+2,_py+lengthdir_y(21,_dir+90)+2,_px+lengthdir_x(2,_dir-90)+2,_py+lengthdir_y(2,_dir-90)+2);
            draw_set_color(make_color_rgb(91,96,86));draw_circle(_px+3,_py+3,1.3,false);
        }
    }
}
if(global.effects) {
    // Two slow fog layers drifting in opposite directions, then floating motes of light.
    draw_sprite_tiled_ext(spr_mist,0,global.ui_time*9,global.ui_time*3,1.8,1.8,make_color_rgb(150,195,195),.10);
    draw_sprite_tiled_ext(spr_mist,0,-global.ui_time*6+90,global.ui_time*5,2.6,2.6,make_color_rgb(120,170,180),.07);
    for(var _m=0;_m<26;++_m) {
        var _mx=(_m*79+global.ui_time*(6+_m mod 5))mod 1040,_my=96+((_m*131-global.ui_time*(5+_m mod 4))mod 570+570)mod 570;
        wp_glow(_mx,_my,7+3*sin(global.ui_time*1.3+_m),_m mod 3==0?global.col.gold:global.col.teal,.22+.12*sin(global.ui_time+_m*1.7));
    }
}
draw_sprite_stretched_ext(spr_vignette,0,0,0,WP_FIELD,WP_H,c_black,.62);
