draw_clear(global.col.bg);
draw_set_color(make_color_rgb(27,43,43));draw_rectangle(0,0,WP_FIELD,WP_H,false);
// Deterministic ground detail; Draw does not change simulation or random state.
for(var _gy=80;_gy<WP_H;_gy+=23)for(var _gx=0;_gx<WP_FIELD;_gx+=29) {
    var _shade=(_gx*17+_gy*31)mod 13;
    draw_set_color(make_color_rgb(25+_shade,39+_shade,38+_shade));
    draw_rectangle(_gx,_gy,_gx+28,_gy+22,false);
    draw_set_color(make_color_rgb(43,61,57));draw_line(_gx+7,_gy+9,_gx+9,_gy+5);
}
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
            draw_set_color(make_color_rgb(91,96,86));draw_circle(_px+3,_py+3,1.3,false);
        }
    }
}
if(global.effects) {
    draw_set_alpha(.11);draw_set_color(global.col.teal);
    for(var _m=0;_m<18;++_m)draw_circle((_m*79+global.ui_time*7)mod 1040,110+((_m*131)mod 570),1.5+sin(global.ui_time+_m),false);
    draw_set_alpha(1);
}
