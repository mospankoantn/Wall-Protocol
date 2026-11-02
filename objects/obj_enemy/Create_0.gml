wp_init();enemy_kind=clamp(enemy_kind,0,3);
var _wave=instance_exists(obj_game)?obj_game.wave:1;
max_hp=[70+_wave*13,180+_wave*32,88+_wave*17,950+_wave*80][enemy_kind];hp=max_hp;
move_speed=[56,38,84,30][enemy_kind];reward=[10,19,15,100][enemy_kind];breach_damage=[1,2,1,6][enemy_kind];
path_i=0;progress=0;slow_t=0;slow_factor=1;hit_flash=0;walk_time=0;face=1;spawn_t=0;image_speed=0;
sprite_index=global.enemy_sprites[enemy_kind];depth=-y;
uid=instance_exists(obj_game)?obj_game.next_uid++:1;
