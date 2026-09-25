wp_init();image_speed=0;cooldown=0;recoil=0;target=noone;pad_key="";
tower_kind=clamp(tower_kind,0,2);level=clamp(level,1,3);invested=global.towers[tower_kind].cost;
for(var _l=1;_l<level;++_l)invested+=round(global.towers[tower_kind].cost*(.65+.35*_l));
sprite_index=global.towers[tower_kind].sprite;depth=-y;
