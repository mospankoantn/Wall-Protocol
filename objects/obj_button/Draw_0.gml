if(page!=global.page)exit;
if(action=="target"&&!instance_exists(wp_selected_tower()))exit;
var _enabled=wp_button_enabled(action),_hot=_enabled&&(hovered||global.focus_button==id);
var _by=y+((_hot&&hovered&&mouse_check_button(mb_left))?1:0);
var _inner=_enabled?merge_color(make_color_rgb(27,40,47),make_color_rgb(62,66,56),hover_t):make_color_rgb(16,27,33);
var _outer=_enabled?merge_color(make_color_rgb(14,24,30),make_color_rgb(34,38,33),hover_t):make_color_rgb(12,20,26);
draw_set_alpha(.97);draw_roundrect_color(x,_by,x+button_w,_by+button_h,_inner,_outer,false);
draw_set_color(_hot?global.col.gold:global.col.line);draw_roundrect(x,_by,x+button_w,_by+button_h,true);
draw_set_alpha(.12+.14*hover_t);draw_set_color(c_white);draw_line(x+8,_by+2,x+button_w-8,_by+2);draw_set_alpha(1);
if(hover_t>.02){draw_set_alpha(hover_t);draw_set_color(global.col.gold);draw_rectangle(x,_by+10,x+2+3*hover_t,_by+button_h-10,false);draw_set_alpha(1);}
draw_set_font(fnt_ui);draw_set_valign(fa_top);
if(string_copy(action,1,5)=="build") {
    // Tower buttons: icon, hotkey, name and aether cost (red when it cannot be afforded).
    var _k=real(string_char_at(action,6)),_cfg=global.towers[_k];
    var _afford=instance_exists(obj_game)&&obj_game.gold>=_cfg.cost,_ty=_by+(button_h-string_height("A"))/2;
    draw_sprite_ext(_cfg.sprite,0,x+28,_by+button_h/2,.44,.44,0,_enabled?c_white:make_color_rgb(120,135,140),_enabled?1:.6);
    draw_set_halign(fa_left);
    draw_set_color(_enabled?(_hot?global.col.gold:global.col.text):make_color_rgb(94,113,119));
    draw_text(x+56,_ty,string(_k+1)+"  "+wp_tower_name(_k));
    draw_sprite_ext(spr_aether,0,x+button_w-58,_by+button_h/2,.26,.26,0,c_white,_afford?1:.5);
    draw_set_color(_afford?global.col.gold:global.col.red);draw_text(x+button_w-44,_ty,string(_cfg.cost));
} else {
    draw_set_halign(fa_center);
    draw_set_color(_enabled?(_hot?global.col.gold:global.col.text):make_color_rgb(94,113,119));
    var _label=wp_button_label(action),_scale=min(1,(button_w-24)/max(1,string_width(_label)));
    draw_text_transformed(x+button_w/2,_by+(button_h-string_height(_label)*_scale)/2,_label,_scale,_scale,0);
}
draw_set_halign(fa_left);
if(action=="music"||action=="sfx") {
    var _v=action=="music"?global.music_volume:global.sfx_volume;
    draw_set_color(global.col.line);draw_rectangle(x+16,_by+button_h-7,x+button_w-16,_by+button_h-5,false);
    draw_set_color(global.col.teal);draw_rectangle(x+16,_by+button_h-7,x+16+(button_w-32)*_v,_by+button_h-5,false);
}
