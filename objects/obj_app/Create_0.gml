wp_init();
if(instance_number(obj_app)>1){instance_destroy();exit;}
persistent=true;depth=-10000;
autosave_timer=30;
