wp_init();
if(instance_number(obj_audio)>1){instance_destroy();exit;}
persistent=true;last_play={};music_voice=audio_play_sound(snd_ambience,-10,true);wp_audio_apply();
