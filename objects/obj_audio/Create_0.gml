wp_init();
if(instance_number(obj_audio)>1){instance_destroy();exit;}
persistent=true;last_play={};music_voice=audio_play_sound(snd_ambience,-10,true);
battle_level=0;battle_voice=audio_play_sound(snd_battle,-10,true);audio_sound_gain(battle_voice,0,0);
wp_audio_apply();
