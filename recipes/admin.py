from django.contrib import admin
from .models import Recipe, Step

# StepAdminでget_total_duration()を表示
class StepAdmin(admin.ModelAdmin):
    list_display = ('recipe','number','action', 'ingredient', 'detail','action_time', 'get_total_duration')
    
    # 動作の選択肢をより見やすく表示する
    def get_total_duration(self, obj):
        return obj.get_total_duration()
    get_total_duration.short_description = 'Total Duration'

# RecipeとStepモデルを管理画面に登録
admin.site.register(Recipe)
admin.site.register(Step, StepAdmin)
