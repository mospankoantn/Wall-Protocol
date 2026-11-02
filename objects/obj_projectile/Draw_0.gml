var _col=[global.col.gold,global.col.purple,global.col.teal][shot_kind],_n=array_length(trail);
for(var _i=0;_i<_n;++_i) {
    var _f=(_i+1)/_n;
    wp_glow(trail[_i][0],trail[_i][1],(3+_f*7)*(shot_kind==1?1.7:1),_col,_f*.45);
}
if(shot_kind!=0)wp_glow(x,y,shot_kind==1?28:18,_col,.55+.2*sin(global.ui_time*18));
draw_self();
