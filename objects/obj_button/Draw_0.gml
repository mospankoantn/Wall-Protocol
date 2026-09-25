if(page!=global.page)exit;
var _enabled=wp_button_enabled(action),_hot=_enabled&&(hovered||global.focus_button==id);
var _c=_hot?global.col.gold:global.col.line;
draw_set_alpha(.97);draw_set_color(_hot?make_color_rgb(43,48,45):global.col.panel);draw_roundrect(x,y,x+button_w,y+button_h,false);
draw_set_color(_c);draw_roundrect(x,y,x+button_w,y+button_h,true);draw_set_alpha(1);
if(_hot){draw_set_color(global.col.gold);draw_rectangle(x,y+10,x+3,y+button_h-10,false);}
draw_set_font(fnt_ui);draw_set_halign(fa_center);draw_set_valign(fa_top);
draw_set_color(_enabled?(_hot?global.col.gold:global.col.text):make_color_rgb(94,113,119));
var _label=wp_button_label(action),_scale=min(1,(button_w-24)/max(1,string_width(_label)));
draw_text_transformed(x+button_w/2,y+(button_h-string_height(_label)*_scale)/2,_label,_scale,_scale,0);draw_set_halign(fa_left);
if(action=="music"||action=="sfx") {
    var _v=action=="music"?global.music_volume:global.sfx_volume;
    draw_set_color(global.col.line);draw_rectangle(x+16,y+button_h-7,x+button_w-16,y+button_h-5,false);
    draw_set_color(global.col.teal);draw_rectangle(x+16,y+button_h-7,x+16+(button_w-32)*_v,y+button_h-5,false);
}
