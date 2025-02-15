# Generated by Django 5.1.5 on 2025-01-24 09:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0006_remove_recipe_description_alter_recipe_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='step',
            name='action',
            field=models.CharField(choices=[('cut', '切る'), ('boil', '煮込む'), ('grill', '焼く'), ('steam', '蒸す'), ('fry', '揚げる'), ('boil_water', '茹でる'), ('cook_rice', '炊く'), ('stir_fry', '炒める'), ('mix', '和える'), ('microwave', '電子レンジ')], max_length=20),
        ),
    ]
