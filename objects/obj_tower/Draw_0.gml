draw_set_color(c_black);draw_set_alpha(.25);draw_ellipse(x-26,y-12,x+26,y+10,false);draw_set_alpha(1);
draw_sprite_ext(sprite_index,0,x,y-20-recoil*3,1,1,0,c_white,1);
for(var _i=0;_i<level;++_i) {draw_set_color(global.col.gold);draw_circle(x+(_i-(level-1)/2)*9,y+15,2.5,false);}
if(wp_selected_tower()==id&&instance_exists(target)) {draw_set_color(global.col.gold);draw_circle(target.x,target.y,21,true);}
