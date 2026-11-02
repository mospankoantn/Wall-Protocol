function wp_sound(_sound,_volume=1,_pitch_var=0) {
    if (global.sfx_volume<=0 || !instance_exists(obj_audio)) return;
    // Limit overlapping repetitive sounds without muting other sound categories.
    var _key=string(_sound);
    if(variable_struct_exists(obj_audio.last_play,_key) && global.ui_time-obj_audio.last_play[$ _key]<0.045) return;
    obj_audio.last_play[$ _key]=global.ui_time;
    var _voice=audio_play_sound(_sound,0,false);
    audio_sound_gain(_voice,global.sfx_volume*_volume,0);
    // Small random pitch shifts keep repeated combat sounds from sounding mechanical.
    if(_pitch_var>0)audio_sound_pitch(_voice,1+random_range(-_pitch_var,_pitch_var));
}
function wp_audio_apply() {
    if(instance_exists(obj_audio) && obj_audio.music_voice!=-1) audio_sound_gain(obj_audio.music_voice,global.music_volume,180);
}
// Adaptive score: the drum/bass layer (snd_battle) fades in while a wave is running and out afterwards.
// Both layers loop with identical length, so they stay in sync. Called every frame from obj_app.
function wp_music_update(_dt) {
    if(!instance_exists(obj_audio)||obj_audio.battle_voice==-1)return;
    var _target=0;
    if(instance_exists(obj_game)&&instance_exists(obj_wave)&&obj_wave.active&&obj_game.result==0) {
        _target=obj_game.wave>=8?1:.8;
        if(global.page=="pause"||global.page=="options"||global.page=="language")_target*=.4;
    }
    with(obj_audio) {
        battle_level=lerp(battle_level,_target,min(1,_dt*(_target>battle_level?.9:.7)));
        if(abs(battle_level-_target)<.002)battle_level=_target;
        audio_sound_gain(music_voice,global.music_volume*(1-.22*battle_level),0);
        audio_sound_gain(battle_voice,global.music_volume*.9*battle_level,0);
    }
}
