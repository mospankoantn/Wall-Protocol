var _p=1-life/max_life;
draw_set_color(tint);draw_set_alpha(1-_p);
if(fx_kind==1){draw_circle(x,y,radius*_p,true);draw_set_alpha((1-_p)*.15);draw_circle(x,y,radius*_p,false);}
else for(var _i=0;_i<6;++_i)draw_circle(x+lengthdir_x(radius*_p,_i*60),y+lengthdir_y(radius*_p,_i*60),2*(1-_p),false);
draw_set_alpha(1);
