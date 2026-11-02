var _accent=[global.col.gold,global.col.purple,global.col.teal][tower_kind],_sel=(wp_selected_tower()==id);
// Rune circle on the ground for upgraded or selected towers.
if(level>1||_sel)wp_rune_ground(x,y+8,32+level*4,global.ui_time*(10+level*5)*(tower_kind==2?-1:1),_accent,_sel?.6:.12+.09*level);
draw_set_color(c_black);draw_set_alpha(.25);draw_ellipse(x-26,y-12,x+26,y+10,false);draw_set_alpha(1);
// Idle glow of the crystal towers.
if(tower_kind==1)wp_glow(x,y-52,34+level*4,global.col.purple,.26+.1*sin(global.ui_time*3+x));
if(tower_kind==2)wp_glow(x,y-50,32+level*4,global.col.teal,.24+.1*sin(global.ui_time*2.4+x));
var _flip=(tower_kind==0&&instance_exists(target)&&target.x<x)?-1:1;
draw_sprite_ext(sprite_index,0,x,y-20-recoil*3,_flip,1,0,c_white,1);
// Muzzle flash right after a shot.
if(recoil>.5)wp_flare(x+(tower_kind==0?_flip*20:0),y-(tower_kind==0?46:54),22+26*recoil,0,_accent,recoil);
for(var _i=0;_i<level;++_i) {draw_set_color(global.col.gold);draw_circle(x+(_i-(level-1)/2)*9,y+15,2.5,false);}
if(_sel&&instance_exists(target)) {draw_set_color(global.col.gold);draw_circle(target.x,target.y,21,true);}
