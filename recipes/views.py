from django.shortcuts import render
from .models import Recipe


def recipe_scheduler(request):
    if request.method == 'POST':
        # フォームから送信された選択されたレシピのリスト(id)を取得
        selected_recipes = request.POST.getlist('recipes')
        #デバッグ
        #print('レシピid' + str(selected_recipes))
        steps = []
        for recipe_id in selected_recipes:
            #idが選択したレシピのモノと一致したらデータベースから取得
            recipe = Recipe.objects.get(id=recipe_id)
            #print('レシピ名:' + str(recipe))
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

        # レシピごとに作業の流れをまとめる
        recipe_schedules = {}

        #taskには選択したレシピの手順がすべて入っている
        for task in tasks:
            #デバッグ
            #print(task)
            if task['recipe_name'] not in recipe_schedules:
                #レシピ名をキーとして辞書にリストを追加
                recipe_schedules[task['recipe_name']] = []
            #レシピごとにタスクを辞書に追加
            recipe_schedules[task['recipe_name']].append(task)
        #デバッグ
        #print(recipe_schedules)
            
        # 各レシピの所要時間を計算
        recipe_times = {}
        #キー(レシピ名)と値(レシピの手順すべて)を取得
        for recipe_name, tasks in recipe_schedules.items():
            #デバッグ
            #print("キー:" + str(recipe_name) + "値:" + str(tasks))
            total_time = 0
            for task in tasks:
                #炊く、茹でるの待ち時間を除いた時間を計算
                if task['action'] not in ['炊く', '茹でる']:
                    total_time += task['action_time']
            #レシピごとの所要時間を設定
            recipe_times[recipe_name] = total_time
        # 所要時間が長い順にレシピを並び替え
        sorted_recipes = sorted(recipe_times.items(), key=lambda x: x[1], reverse=True)

        schedule = []
        already_scheduled = set()  # すでにスケジュール済みのタスクを管理
        skipped_tasks = [] #スキップした調理を保存
        skipped_tasks_oven = [] #スキップした調理を保存(電子レンジ用)
        now_time = 0
        now_time_oven = 0
        boil_time = 0
        total_time = 0
        oven = 0
        boil_start = False
        break_flag = False
        oven_start = False

        # 最優先でご飯を炊く
        for recipe_name, _ in sorted_recipes:
            #デバッグ
            #print(recipe_name)#レシピ名
            tasks = recipe_schedules[recipe_name]
            #デバッグ
            #print(tasks)#レシピの詳細
            for task in tasks:
                #ご飯を炊くのみスケジュールに追加
                if task['action'] == '炊く':
                    schedule.append({
                        'recipe_name': task['recipe_name'],
                        'detail': task['detail'],
                        'action': task['action'],
                        'ingredient': task['ingredient'],
                        'action_time': task['action_time'],
                    })
                    already_scheduled.add((task['recipe_name'], task['detail'],task['action'], task['ingredient']))
                    break

        #次に茹でるを優先
        for recipe_name, _ in sorted_recipes:
            #デバッグ
            #print(recipe_name)#レシピ名
            tasks = recipe_schedules[recipe_name]
            #デバッグ
            #print(tasks)#レシピの詳細
            for task in tasks:
                #茹でると置くのみスケジュールに追加
                if task['action'] in ['茹でる','置く']:
                    schedule.append({
                        'recipe_name': task['recipe_name'],
                        'detail': task['detail'],
                        'action': task['action'],
                        'ingredient': task['ingredient'],
                        'action_time': task['action_time'],
                    })
                    already_scheduled.add((task['recipe_name'], task['detail'],task['action'], task['ingredient']))
                    break

        # ご飯を炊く、茹でる後の作業のスケジュールを実行
        while True:
            all_tasks_processed = True
            for recipe_name, _ in sorted_recipes:
                tasks = recipe_schedules[recipe_name]
                for task in tasks:
                    #もしすでに追加されていたらスキップ
                    if (task['recipe_name'], task['detail'], task['action'], task['ingredient']) in already_scheduled:
                        continue

                    # 煮込み中ならスキップ
                    if task['action'] in ['焼く', '煮込む','蒸す'] and boil_time > now_time:
                        #デバッグ
                        # schedule.append({
                        #     'recipe_name': task['recipe_name'],
                        #     'action': task['action'],
                        #     'ingredient': '煮込み中のためスキップ',
                        #     'action_time': task['action_time'],
                        # })
                        #スキップした動作は保存しておく
                        skipped_tasks.append(task)
                        print("煮込み中のため" + str(task['recipe_name']) + str(task['action']) + "をスキップ")
                        #デバッグ
                        #print(skipped_tasks)
                        continue

                    # 電子レンジ使用中ならスキップ
                    if task['action'] in ['電子レンジ'] and oven > now_time_oven:
                        #スキップした動作は保存しておく
                        skipped_tasks_oven.append(task)
                        #デバッグ
                        #print(skipped_tasks)
                        continue

                    #煮込みが終了したら
                    if boil_time <= now_time and boil_start:
                        #スキップした動作を追加していく
                        while skipped_tasks:
                            #0番目のスキップした動作を消してスケジュールに追加
                            skipped_task = skipped_tasks.pop(0)
                            #print(skipped_task)
                            if (skipped_task['recipe_name'], skipped_task['action'], skipped_task['ingredient']) not in already_scheduled:
                                schedule.append({
                                    'recipe_name': skipped_task['recipe_name'],
                                    'detail': skipped_task['detail'],
                                    'action': skipped_task['action'],
                                    'ingredient': skipped_task['ingredient'],
                                    'action_time': skipped_task['action_time'],
                                })
                                #print(f"スキップをスケジュール追加: {task['recipe_name']} - {task['action']} - {task['ingredient']} - {task['action_time']}分")
                                already_scheduled.add((skipped_task['recipe_name'], skipped_task['detail'],skipped_task['action'], skipped_task['ingredient']))
                                if(skipped_task['action'] in ['煮込む','蒸す']):
                                    skip_flag = True
                                    break
                        #もし待ち時間が発生するものが追加されなかったら
                        if skip_flag == False:
                            boil_start = False
                        elif skip_flag:
                            skip_flag = False
                            break
                        print("時間が来たので煮込み終了")
                        boil_time = 0
                        now_time = 0

                    #電子レンジの使用が終了したら
                    if oven <= now_time_oven and skipped_tasks_oven:
                        #0番目のスキップした動作を消してスケジュールに追加
                        skipped_task_oven = skipped_tasks_oven.pop(0)
                        #print(skipped_task)
                        if (skipped_task_oven['recipe_name'], skipped_task_oven['action'], skipped_task_oven['ingredient']) not in already_scheduled:
                            schedule.append({
                                'recipe_name': skipped_task_oven['recipe_name'],
                                'detail': skipped_task_oven['detail'],
                                'action': skipped_task_oven['action'],
                                'ingredient': skipped_task_oven['ingredient'],
                                'action_time': skipped_task_oven['action_time'],
                            })
                            #print(f"スキップをスケジュール追加: {task['recipe_name']} - {task['action']} - {task['ingredient']} - {task['action_time']}分")
                            already_scheduled.add((skipped_task_oven['recipe_name'], skipped_task_oven['detail'],skipped_task_oven['action'], skipped_task_oven['ingredient']))
                    oven_start = False
                    oven = 0
                        
                    
                    if task['action'] in ['煮込む','蒸す']:
                        #もし煮込む動作が来たらboil_timeに時間を代入
                        boil_time = task['action_time']
                        #煮込み開始フラグを立てる
                        boil_start = True
                        print('煮込み開始:時間:' + str(boil_time))
                        #continue

                    #煮込み中に待ち時間が発生しない動作がきたらnow_timeに時間を足す
                    if task['action'] not in ['煮込む','蒸す','電子レンジ'] and boil_start == True:
                        now_time += task['action_time']
                        print('現在の時間:' + str(now_time) + ':+' +str(task['action_time']))

                    if task['action'] in ['電子レンジ']:
                        #もし電子レンジ動作が来たらovenに時間を代入
                        oven = task['action_time']
                        #電子レンジ開始フラグを立てる
                        oven_start = True
                        print('電子レンジ開始:時間:' + str(oven))

                    #電子レンジ使用中に待ち時間が発生しない動作がきたらnow_time_ovenに時間を足す
                    if task['action'] not in ['煮込む','蒸す','電子レンジ'] and oven_start == True:
                        now_time_oven += task['action_time']

                    if (task['recipe_name'],task['detail'], task['action'], task['ingredient']) not in already_scheduled:
                        schedule.append({
                            'recipe_name': task['recipe_name'],
                            'detail': task['detail'],
                            'action': task['action'],
                            'ingredient': task['ingredient'],
                            'action_time': task['action_time'],
                        })
                    already_scheduled.add((task['recipe_name'], task['detail'],task['action'], task['ingredient']))

                    # スキップしたタスクがない場合に終了
                    if not skipped_tasks:
                        skipped_tasks.clear()  # skipped_tasksをクリア
                        break_flag = True
                        for recipe_name, _ in sorted_recipes:
                            tasks = recipe_schedules[recipe_name]
                            for task in tasks:
                                if (task['recipe_name'], task['detail'],task['action'], task['ingredient']) not in already_scheduled:
                                    break_flag = False
                                    break
                            if not break_flag:
                                break

            #すべてのタスクを終えても煮込み時間を超えなかった場合
            if all_tasks_processed and now_time < boil_time:
                #強制的に煮込みを終了
                boil_start = False
                print("超えなかったため煮込み終了")
                boil_time = 0
                #continue

            if break_flag and all_tasks_processed:
                break

        return render(request, 'recipes/scheduler.html', {'schedule': schedule})

    recipes = Recipe.objects.all()
    return render(request, 'recipes/select_recipes.html', {'recipes': recipes})
