from django.shortcuts import render
from .models import Recipe




def recipe_scheduler(request):
    if request.method == 'POST':

        # フォームから送信された選択されたレシピのリスト(id)を取得
        selected_recipes = request.POST.getlist('recipes')
        
        steps = []
        recipe_ingredients = {}
        
        for recipe_id in selected_recipes:

            #idが選択したレシピのモノと一致したらデータベースから取得
            recipe = Recipe.objects.get(id=recipe_id)
            recipe_ingredients[recipe.name] = recipe.ingredients
            
            #レシピに関連するすべての情報を取得
            for step in recipe.steps.all().order_by('number'):
                steps.append({
                    'recipe_name': recipe.name,#レシピ名
                    'detail': step.detail,#詳細
                    'action': step.action,#動作
                    'ingredient': step.ingredient,#材料
                    'action_time': step.action_time,#時間
                })

        #動作を日本語に変換
        action_map = {
            'cut': '切る',
            'boil': '煮込む',
            'grill': '焼く',
            'fry': '揚げる',
            'steam': '蒸す',
            'toss': '和える',
            'mix': '混ぜる',
            'pack': '詰める',
            'microwave': '電子レンジ',
            'boil_water': '茹でる',
            'cook_rice': '炊く',
            'stir_fry': '炒める',
            'arrangement': '盛り付け',
            'keep': '置く'
        }

        #日本語に変更
        tasks = []
        for step in steps:
            tasks.append({
                'recipe_name': step['recipe_name'],
                'detail': step['detail'],
                'action': action_map.get(step['action'], step['action']),
                'ingredient': step['ingredient'],
                'action_time': step['action_time'],
            })

        #　ここから各レシピの待ち時間を計算し、優先順位を決定する
        # レシピごとに作業の流れをまとめる
        recipe_schedules = {}

        #taskには選択したレシピの手順がすべて入っている
        for task in tasks:
            if task['recipe_name'] not in recipe_schedules:

                #レシピ名をキーとして辞書にリストを追加
                recipe_schedules[task['recipe_name']] = []

            #レシピごとにタスクを辞書に追加
            recipe_schedules[task['recipe_name']].append(task)

        # 各レシピの待ち時間を計算
        wait_total_times = {}
        for recipe_name, tmp in recipe_schedules.items():
            total_time = 0
            wait_time = 0
            for task in tmp:
                total_time += task['action_time']
                if task['action'] in ['炊く', '茹でる','煮込む','蒸す','置く','電子レンジ']:
                    wait_time += task['action_time']
            wait_total_times[recipe_name] = wait_time

        # 待ち時間が長い順にレシピを並び替え
        sorted_recipes = sorted(recipe_schedules.items(), key=lambda x: wait_total_times[x[0]], reverse=True)       

        schedule = []
        already_scheduled = set()  # すでにスケジュール済みのタスクを管理
        total_time:int = 0

        for recipe_name, task_list in sorted_recipes:  # タプルを分解
            for task in task_list:
                if (task['recipe_name'], task['detail'], task['action'], task['ingredient']) not in already_scheduled:

                    # スケジュールに追加
                    schedule.append({
                        'recipe_name': task['recipe_name'],
                        'detail': task['detail'],
                        'action': task['action'],
                        'ingredient': task['ingredient'],
                        'action_time': task['action_time'],
                    })
                    already_scheduled.add((task['recipe_name'], task['detail'], task['action'], task['ingredient']))

                    # 待ち時間が発生する場合
                    if task['action'] in ['炊く', '茹でる', '煮込む', '蒸す', '置く', '電子レンジ']:
                        wait_time = task['action_time']
                        print(task['recipe_name'] + task['action'] + 'で待ち時間発生')

                        remaining_wait_time = wait_time  # 残りの待ち時間
                        while remaining_wait_time > 0:
                            added_task = False  # 待ち時間中に追加できたか

                            for next_recipe_name, next_task_list in sorted_recipes:
                                for next_task in next_task_list:
                                    if next_task['recipe_name'] != task['recipe_name'] and \
                                    (next_task['recipe_name'], next_task['detail'], next_task['action'], next_task['ingredient']) not in already_scheduled:

                                        print(next_task['recipe_name'] + next_task['action'] + 'を割り込み追加')

                                        # スケジュールに追加
                                        schedule.append({
                                            'recipe_name': next_task['recipe_name'],
                                            'detail': next_task['detail'],
                                            'action': next_task['action'],
                                            'ingredient': next_task['ingredient'],
                                            'action_time': next_task['action_time'],
                                        })
                                        already_scheduled.add((next_task['recipe_name'], next_task['detail'], next_task['action'], next_task['ingredient']))

                                        # 作業時間計算
                                        remaining_wait_time -= next_task['action_time']
                                        added_task = True

                                        # もし待ち時間がなくなれば終了
                                        if remaining_wait_time <= 0:
                                            break  

                                # ループから抜ける
                                if remaining_wait_time <= 0:
                                    break  

                            # もし何も追加できなかったら、残り時間をそのまま進める
                            if not added_task:
                                print(f"待ち時間 {remaining_wait_time} 秒 経過")
                                remaining_wait_time = 0  # 待ち時間を初期化


        return render(request, 'recipes/scheduler.html',  {'schedule': schedule, 'recipe_ingredients': recipe_ingredients})

    recipes = Recipe.objects.all()
    return render(request, 'recipes/select_recipes.html', {'recipes': recipes})

