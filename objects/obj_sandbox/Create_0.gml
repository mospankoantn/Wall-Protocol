// Editable room properties are applied before Create.
depth=-1050;
starting_aether=clamp(round(starting_aether),0,1000000);
test_wave=clamp(round(test_wave),1,8);
invulnerable=invulnerable!=0;
if(instance_exists(obj_game)) {obj_game.gold=starting_aether;obj_game.wave=test_wave;}
