var _p=.5+.5*sin(global.ui_time*3);
wp_glow(x,y-26,74+8*_p,global.col.purple,.34+.12*_p);
draw_sprite_ext(spr_portal,0,x,y-25,1,1,0,c_white,.9+.1*sin(global.ui_time*3));
for(var _i=0;_i<4;++_i) {
    var _t=frac(global.ui_time*.32+_i*.25);
    wp_glow(x+sin(global.ui_time*1.7+_i*2)*14,y-8-_t*62,2+7*(1-_t),global.col.purple,(1-_t)*.75);
}
