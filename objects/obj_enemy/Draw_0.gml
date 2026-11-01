draw_set_color(c_black);draw_set_alpha(.3);draw_ellipse(x-15,y-7,x+15,y+7,false);draw_set_alpha(1);
var _tint=hit_flash>0?merge_color(c_white,global.col.gold,.65):(slow_t>0?make_color_rgb(150,226,255):c_white);
if(enemy_kind==3){draw_set_color(global.col.purple);draw_set_alpha(.14+.05*sin(global.ui_time*4));draw_ellipse(x-34,y-12,x+34,y+12,false);draw_set_alpha(1);}
var _bob=abs(sin(walk_time*pi))*2.5;
draw_sprite_ext(sprite_index,floor(walk_time)mod 2,x,y-15-_bob,face,1,0,_tint,1);
if(hp<max_hp||enemy_kind==3) {
    var _width=enemy_kind==3?64:36;
    draw_set_color(global.col.bg);draw_rectangle(x-_width/2,y-48,x+_width/2,y-43,false);
    draw_set_color(enemy_kind==3?global.col.purple:global.col.red);draw_rectangle(x-_width/2,y-48,x-_width/2+_width*max(0,hp/max_hp),y-43,false);
}
if(slow_t>0){draw_set_color(global.col.teal);draw_set_alpha(.7);draw_ellipse(x-18,y-7,x+18,y+7,true);draw_set_alpha(1);}
