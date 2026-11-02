var _p=1-life/max_life,_i,_ang,_d,_s,_a;
switch(fx_kind) {
    case 2:
        wp_text_a(x,y-30*sqrt(_p),fx_text,fnt_ui,tint,fa_center,1-_p*_p);
        break;
    case 3:
        wp_glow(x,y,radius*(.55+.8*_p),tint,(1-_p)*.85);
        wp_flare(x,y,radius*(1+.5*_p),_p*50,c_white,1-_p);
        break;
    case 4:
        if(ghost_sprite!=-1) {
            _s=1+_p*.2;_a=(1-_p)*.8;
            wp_glow(x,y-26-_p*36,30+_p*24,global.col.teal,(1-_p)*.4);
            draw_sprite_ext(ghost_sprite,ghost_frame,x,y-15-_p*36,ghost_face*_s,_s,0,make_color_rgb(170,235,235),_a);
        }
        break;
    case 1:
        wp_glow(x,y,radius*(.3+.7*_p),tint,(1-_p)*.22);
        wp_ring_fx(x,y,max(6,radius*_p),tint,(1-_p)*1.1);
        break;
    default:
        for(_i=0;_i<8;++_i) {
            _ang=_i*45+seed;_d=radius*sqrt(_p);
            wp_glow(x+lengthdir_x(_d,_ang),y+lengthdir_y(_d,_ang)-_p*10,3+5*(1-_p),tint,1-_p);
        }
}
draw_set_alpha(1);
