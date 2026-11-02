draw_sprite(spr_pad,0,x,y);
if(!instance_exists(obj_game))exit;
var _selected=obj_game.selected_pad==id,_hover=global.page=="game"&&point_distance(mouse_x,mouse_y,x,y)<37;
if(_selected||_hover)wp_rune_ground(x,y+2,_selected?48:42,global.ui_time*(_selected?24:9),_selected?global.col.gold:global.col.teal,_selected?.75:.4);
if(!instance_exists(tower))wp_text(x,y-12,"+",fnt_heading,_selected?global.col.gold:global.col.muted,fa_center);
if(_selected) {
    // Hovering a build button previews that tower's range on this foundation.
    preview_kind=-1;
    if(!instance_exists(tower))with(obj_button)if(hovered&&string_copy(action,1,5)=="build")other.preview_kind=real(string_char_at(action,6));
    var _range=instance_exists(tower)?global.towers[tower.tower_kind].range+(tower.level-1)*10:(preview_kind>=0?global.towers[preview_kind].range:175);
    draw_set_color(global.col.teal);draw_set_alpha(.06);draw_circle(x,y,_range,false);draw_set_alpha(.35);draw_circle(x,y,_range,true);draw_set_alpha(1);
}
