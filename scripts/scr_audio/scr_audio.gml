function wp_sound(_sound,_volume=1) {
    if (global.sfx_volume<=0 || !instance_exists(obj_audio)) return;
    // Limit overlapping repetitive sounds without muting other sound categories.
    var _key=string(_sound);
    if(variable_struct_exists(obj_audio.last_play,_key) && global.ui_time-obj_audio.last_play[$ _key]<0.045) return;
    obj_audio.last_play[$ _key]=global.ui_time;
    var _voice=audio_play_sound(_sound,0,false);
    audio_sound_gain(_voice,global.sfx_volume*_volume,0);
}
function wp_audio_apply() {
    if(instance_exists(obj_audio) && obj_audio.music_voice!=-1) audio_sound_gain(obj_audio.music_voice,global.music_volume,180);
}
