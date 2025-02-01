from django.db import models

# 動作の種類を示す選択肢
class ActionType(models.TextChoices):
    CUT = 'cut', '切る'
    FRY = 'fry', '焼く'
    BOIL = 'boil', '茹でる'
    STEAM = 'steam', '蒸す'
    MIX = 'mix', '混ぜる'
    TOSS = 'toss', '和える'
    pack = 'pack', '詰める'
    BOIL_WATER = 'boil_water', 'お湯を沸かす'
    COOK_RICE = 'cook_rice', 'ご飯を炊く'
    STIR_FRY = 'stir_fry', '炒める'
    MICROWAVE = 'microwave', '電子レンジ'
    ARRANGEMENT = 'arrangement', '盛り付け'
    KEEP = 'keep','置く'

class Recipe(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Step(models.Model):
    # 料理のレシピ
    recipe = models.ForeignKey('Recipe', on_delete=models.CASCADE, related_name='steps')

    #順番
    number = models.IntegerField(null=True) 
    
    # 動作の選択肢
    ACTION_CHOICES = [
        ('cut', '切る'),
        ('boil', '煮込む'),
        ('grill', '焼く'),
        ('steam', '蒸す'),
        ('fry', '揚げる'),
        ('boil_water', '茹でる'),
        ('cook_rice', '炊く'),
        ('stir_fry', '炒める'),
        ('mix', '混ぜる'),
        ('toss','和える'),
        ('pack', '詰める'),
        ('keep','置く'),
        ('microwave', '電子レンジ'),
        ('arrangement', '盛り付け')
    ]

    # 動作を選ぶ
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    
    # 材料名
    ingredient = models.CharField(max_length=255)

    #詳細
    detail = models.TextField(blank=True, null=True)  
    
    # 実行時間（手を動かす時間）
    action_time = models.IntegerField()

    def __str__(self):
        return f"{self.action} {self.ingredient} (Action Time: {self.action_time} min)"
    
    def get_total_duration(self):
        return self.action_time
    
    def save(self, *args, **kwargs):
        if self.action in ['boil', 'steam', 'boil_water', 'cook_rice', 'microwave']:
            pass
        super(Step, self).save(*args, **kwargs)
        