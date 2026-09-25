draw_sprite(spr_pad,0,x,y);
if(!instance_exists(obj_game))exit;
var _selected=obj_game.selected_pad==id,_hover=global.page=="game"&&point_distance(mouse_x,mouse_y,x,y)<37;
if(_selected||_hover) {
    draw_set_color(_selected?global.col.gold:global.col.teal);draw_set_alpha(.8);draw_ellipse(x-37,y-23,x+37,y+23,true);draw_set_alpha(1);
}
if(!instance_exists(tower))wp_text(x,y-12,"+",fnt_heading,_selected?global.col.gold:global.col.muted,fa_center);
if(_selected) {
    var _range=instance_exists(tower)?global.towers[tower.tower_kind].range+(tower.level-1)*10:175;
    draw_set_color(global.col.teal);draw_set_alpha(.06);draw_circle(x,y,_range,false);draw_set_alpha(.35);draw_circle(x,y,_range,true);draw_set_alpha(1);
}
