var _in=clamp(spawn_t/.5,0,1),_sh=[15,19,13,32][enemy_kind];
draw_set_color(c_black);draw_set_alpha(.32*_in);draw_ellipse(x-_sh,y-_sh*.47,x+_sh,y+_sh*.47,false);draw_set_alpha(1);
var _tint=hit_flash>0?merge_color(c_white,global.col.gold,.65):(slow_t>0?make_color_rgb(150,226,255):c_white);
if(enemy_kind==3){wp_glow(x,y-4,52,global.col.purple,.18+.07*sin(global.ui_time*4));}
var _bob=abs(sin(walk_time*pi))*2.5,_sx=face*(.82+.18*_in),_sy=.82+.18*_in;
if(hit_flash>0){_sx*=1.07;_sy*=.93;}
draw_sprite_ext(sprite_index,floor(walk_time)mod 2,x,y-15-_bob,_sx,_sy,0,_tint,_in);
if(slow_t>0)wp_glow(x,y-22,26,global.col.teal,.2+.08*sin(global.ui_time*9));
if(hp<max_hp||enemy_kind==3) {
    var _width=enemy_kind==3?64:36;
    draw_set_color(global.col.bg);draw_rectangle(x-_width/2-1,y-49,x+_width/2+1,y-42,false);
    var _bc=enemy_kind==3?global.col.purple:global.col.red;
    draw_rectangle_color(x-_width/2,y-48,x-_width/2+_width*max(0,hp/max_hp),y-43,merge_color(_bc,c_white,.4),merge_color(_bc,c_white,.4),_bc,_bc,false);
}
if(slow_t>0){draw_set_color(global.col.teal);draw_set_alpha(.7);draw_ellipse(x-18,y-7,x+18,y+7,true);draw_set_alpha(1);}
