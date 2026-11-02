var _pulse=.5+.5*sin(global.ui_time*2),_c=flash>0?global.col.red:global.col.teal;
wp_glow(x,y-48,118+14*_pulse,_c,.2+.08*_pulse);
draw_sprite_ext(spr_core,0,x,y-30,1,1,0,flash>0?global.col.red:c_white,1);
wp_glow(x,y-52,46,_c,.45+.2*_pulse);
for(var _i=0;_i<3;++_i) {
    var _a=global.ui_time*55+_i*120;
    wp_glow(x+lengthdir_x(48,_a),y-52+lengthdir_y(48,_a)*.38,6,c_white,.6);
}
