if(global.page!="game")exit;
wp_panel(0,0,405,77);
wp_text(24,14,wp_tr("TEST RANGE","ТЕСТОВИЙ ПОЛІГОН"),fnt_ui,global.col.gold);
wp_text(24,41,wp_tr("Experiment. Reset. Repeat.","Експериментуйте й починайте знову."),fnt_ui,global.col.muted);
wp_panel(12,500,1036,187,.97);
wp_text(28,510,wp_tr("Enemies: ","Ворогів: ")+string(instance_number(obj_enemy))+"   /   "+wp_tr("Towers: ","Веж: ")+string(instance_number(obj_tower)),fnt_ui,global.col.teal);
wp_text(1030,510,wp_tr("Expedition saves are protected","Збереження походу захищені"),fnt_ui,global.col.muted,fa_right);
