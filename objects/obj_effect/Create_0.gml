if(!variable_instance_exists(id,"fx_kind"))fx_kind=0;
if(!variable_instance_exists(id,"tint"))tint=c_white;
if(!variable_instance_exists(id,"radius"))radius=30;
if(!variable_instance_exists(id,"fx_text"))fx_text="";
if(!variable_instance_exists(id,"ghost_sprite"))ghost_sprite=-1;
if(!variable_instance_exists(id,"ghost_frame"))ghost_frame=0;
if(!variable_instance_exists(id,"ghost_face"))ghost_face=1;
// fx_kind: 0 sparks, 1 shock ring, 2 floating text, 3 flare burst, 4 rising ghost of a fallen enemy
life=[.5,.55,1,.38,.75][clamp(fx_kind,0,4)];max_life=life;depth=-920;seed=irandom(359);
