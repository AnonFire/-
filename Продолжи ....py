# -*- coding: utf-8 -*-
from flask import Flask, request
import logging
import json
import random
from info import latin, poslov, stixi

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

sessionStorage = {}
frasa = None


@app.route('/post', methods=['POST'])
def main():
    logging.info('Request: %r', request.json)
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }
    handle_dialog(response, request.json)
    logging.info('Response: %r', response)
    return json.dumps(response)


def handle_dialog(res, req):
    global frasa
    user_id = req['session']['user_id']
    if req['session']['new']:
        res['response']['text'] = 'Привет! Назови своё имя!'
        sessionStorage[user_id] = {
            'first_name': None,  # здесь будет храниться имя
            'game_started': False,
            'resim': 0,
            'frasi': []
            # здесь информация о том, что пользователь начал игру.
            # По умолчанию False
        }
        return

    if sessionStorage[user_id]['first_name'] is None:
        first_name = get_first_name(req)
        if first_name is None:
            res['response']['text'] = 'Не расслышала имя. Повтори, пожалуйста!'
        else:
            sessionStorage[user_id]['first_name'] = first_name[:]
            # создаём пустой массив, в который будем записывать фразы,
            # которые пользователь уже отгадал
            # как видно из предыдущего навыка, сюда мы попали,
            # потому что пользователь написал своем имя.
            # Предлагаем ему сыграть и два варианта ответа "Да" и "Нет".
            res['response']['text'] = 'Приятно познакомиться, '
            res['response']['text'] += first_name.title()
            res['response']['text'] += '. Я Алиса. Сыграем?'
            res['response']['buttons'] = [
                {
                    'title': 'Да',
                    'hide': True
                },
                {
                    'title': 'Нет',
                    'hide': True
                },
                {
                    'title': 'Помощь',
                    'hide': True
                 },
            ]
    else:
        # У нас уже есть имя, и теперь мы ожидаем ответ на предложение сыграть.
        # В sessionStorage[user_id]['game_started'] хранится True или False
        # в зависимости от того,
        # начал пользователь игру или нет.
        if not sessionStorage[user_id]['game_started']:
            # игра не начата, значит мы ожидаем ответ на предложение сыграть.
            if 'да' in req['request']['nlu']['tokens']:
                sessionStorage[user_id]['game_started'] = True
                fn = sessionStorage[user_id]["first_name"][:]
                res['response']['text'] = fn.title()
                res['response']['text'] += ', во что ты хочешь сыграть?\n'
                res['response']['text'] += ' Продолжить известную стихотворную'
                res['response']['text'] += ' строчку, знаменитую латинскую фра'
                res['response']['text'] += 'зу или пословицу?'
                res['response']['buttons'] = [
                    {
                        'title': 'стихотворную строчку',
                        'hide': True
                    },
                    {
                        'title': 'латинскую фразу',
                        'hide': True
                    },
                    {
                        'title': 'пословицу',
                        'hide': True
                    },
                    {
                        'title': 'Помощь',
                        'hide': True
                    },
                    {
                        'title': 'Смешной совет',
                        'hide': True
                    }
                    ]
            elif 'нет' in req['request']['nlu']['tokens']:
                res['response']['text'] = 'Ну и ладно!'
                res['end_session'] = True
            elif 'помощь' in req['request']['nlu']['tokens']:
                res['response']['text'] = 'Я предлагаю тебе сыграть в игру. Я г'
                res['response']['text'] += 'оворю тебе начало известной латинск'
                res['response']['text'] += 'ой фразы/пословицы/стихотворной стр'
                res['response']['text'] += 'очки (что выберешь), а ты продолжае'
                res['response']['text'] += 'шь мою фразу. Сегодня я очень добра'
                res['response']['text'] += 'я, поэтому дам тебе 3 варианта (оди'
                res['response']['text'] += 'н из них верный)'
                res['response']['buttons'] = [
                    {
                        'title': 'Да',
                        'hide': True
                    },
                    {
                        'title': 'Нет',
                        'hide': True
                    },
                    {
                        'title': 'Помощь',
                        'hide': True
                     }
                    ]
            else:
                res['response']['text'] = 'Не поняла ответа! Так да или нет?'
                res['response']['buttons'] = [
                    {
                        'title': 'Да',
                        'hide': True
                    },
                    {
                        'title': 'Нет',
                        'hide': True
                    },
                    {
                        'title': 'Помощь',
                        'hide': True
                     }
                ]
        elif not sessionStorage[user_id]['resim']:
            lt = 'латинскую' in req['request']['nlu']['tokens']
            lt = lt or 'фразу' in req['request']['nlu']['tokens']
            smesh = 'Смешной' in req['request']['nlu']['tokens']
            smesh = smesh or 'совет' in req['request']['nlu']['tokens']
            if 'стихотворную' in req['request']['nlu']['tokens']:
                sessionStorage[user_id]['frasi'] = []
                sessionStorage[user_id]['resim'] = 1
                games[0](res, req)
                sessionStorage[user_id]['frasi'] = []
            elif lt:
                sessionStorage[user_id]['frasi'] = []
                sessionStorage[user_id]['resim'] = 2
                games[sessionStorage[user_id]['resim'] - 1](res, req)
                sessionStorage[user_id]['frasi'] = []
            elif 'пословицу' in req['request']['nlu']['tokens']:
                sessionStorage[user_id]['frasi'] = []
                sessionStorage[user_id]['resim'] = 3
                sessionStorage[user_id]['frasi'] = []
                games[sessionStorage[user_id]['resim'] - 1](res, req)
            elif 'помощь' in req['request']['nlu']['tokens']:
                res['response']['text'] = 'Я предлагаю тебе сыграть в игру. Я г'
                res['response']['text'] += 'оворю тебе начало известной латинск'
                res['response']['text'] += 'ой фразы/пословицы/стихотворной стр'
                res['response']['text'] += 'очки (что выберешь), а ты продолжае'
                res['response']['text'] += 'шь мою фразу. Сегодня я очень добра'
                res['response']['text'] += 'я, поэтому дам тебе 3 варианта (оди'
                res['response']['text'] += 'н из них верный)'
                res['response']['buttons'] = [
                    {
                        'title': 'стихотворную строчку',
                        'hide': True
                    },
                    {
                        'title': 'латинскую фразу',
                        'hide': True
                    },
                    {
                        'title': 'пословицу',
                        'hide': True
                    },
                    {
                        'title': 'Помощь',
                        'hide': True
                    },
                    {
                        'title': 'Смешной совет',
                        'hide': True
                    }
                ]
            elif 'хватит' in req['request']['nlu']['tokens']:
                res['response']['text'] = 'Ну и ладно!'
                res['end_session'] = True
            elif smesh:
                res['response']['text'] = 'Внимательно читай материальную часть'
                res['response']['text'] += '!)'
                res['response']['buttons'] = [
                    {
                        'title': 'стихотворную строчку',
                        'hide': True
                    },
                    {
                        'title': 'латинскую фразу',
                        'hide': True
                    },
                    {
                        'title': 'пословицу',
                        'hide': True
                    },
                    {
                        'title': 'Помощь',
                        'hide': True
                    },
                    {
                        'title': 'Смешной совет',
                        'hide': True
                    }
                ]
            else:
                res['response']['text'] = 'Не поняла ответа! Так что ты выбир'
                res['response']['text'] += 'аешь?'
                res['response']['buttons'] = [
                    {
                        'title': 'стихотворную строчку',
                        'hide': True
                    },
                    {
                        'title': 'латинскую фразу',
                        'hide': True
                    },
                    {
                        'title': 'пословицу',
                        'hide': True
                    },
                    {
                        'title': 'Помощь',
                        'hide': True
                    },
                    {
                        'title': 'Смешной совет',
                        'hide': True
                    }
                ]
        else:
            ng = not frasa and 'да' in req['request']['nlu']['tokens']
            ng = ng or sessionStorage[user_id]['frasi'] == []
            ng = ng or frasa
            if ng:
                games[sessionStorage[user_id]['resim'] - 1](res, req)
            elif 'нет' in req['request']['nlu']['tokens']:
                res['response']['text'] = 'Ну и ладно!'
                res['end_session'] = True
            elif 'помощь' in req['request']['nlu']['tokens']:
                if sessionStorage[user_id]['resim'] == 1:
                    res['response']['text'] = 'Я говорю тебе начало стихотворно'
                    res['response']['text'] += 'й строчки, а ты должен её продо'
                    res['response']['text'] += 'лжить. Всё просто. Я дам тебе 3'
                    res['response']['text'] += ' варианта ответа, но только оди'
                    res['response']['text'] += 'н из них правильный. Удачи!'
                elif sessionStorage[user_id]['resim'] == 2:
                    res['response']['text'] = 'Я говорю тебе начало известной л'
                    res['response']['text'] += 'атинской фразы, а ты должен её '
                    res['response']['text'] += 'продолжить. Всё просто. Я дам т'
                    res['response']['text'] += 'ебе 3 варианта ответа, но тольк'
                    res['response']['text'] += 'о один из них правильный. Удачи'
                    res['response']['text'] += '!'
                else:
                    res['response']['text'] = 'Я говорю тебе начало известной '
                    res['response']['text'] += 'пословицы, а ты должен её '
                    res['response']['text'] += 'продолжить. Всё просто. Я дам т'
                    res['response']['text'] += 'ебе 3 варианта ответа, но тольк'
                    res['response']['text'] += 'о один из них правильный. Удачи'
                    res['response']['text'] += '!'
                res['response']['buttons'] = [
                    {
                        'title': 'Да',
                        'hide': True
                    },
                    {
                        'title': 'Нет',
                        'hide': True
                    },
                    {
                        'title': 'Помощь',
                        'hide': True
                     }
                    ]
            else:
                res['response']['text'] = 'Не поняла ответа! Так да или нет?'
                res['response']['buttons'] = [
                    {
                        'title': 'Да',
                        'hide': True
                    },
                    {
                        'title': 'Нет',
                        'hide': True
                    },
                    {
                        'title': 'Помощь',
                        'hide': True
                     }
                ]


def lat(res, req):
    global latin, frasa
    user_id = req['session']['user_id']
    if len(sessionStorage[user_id]['frasi']) == len(latin.keys()):
        res['response']['text'] = 'Ты победил!'
        return
    if not frasa:
        frasa = random.choice(list(latin.keys()))
        while frasa in sessionStorage[user_id]['frasi']:
            frasa = random.choice(list(latin.eys()))
        res['response']['text'] = frasa
        random.shuffle(latin[frasa])
        res['response']['buttons'] = []
        for i in latin[frasa]:
            res['response']['buttons'].append(
                {
                    'title': i[1:],
                    'hide': True
                })
    elif f(latin[frasa]) == req["request"]['original_utterance']:
        sessionStorage[user_id]['frasi'].append(frasa)
        frasa = None
        if len(sessionStorage[user_id]['frasi']) == len(latin.keys()):
            res['response']['text'] = 'Ты победил!'
            res['end_session'] = True
            return
        res['response']['text'] = 'Правильно! Сыграем ещё?'
        res['response']['buttons'] = [
                    {
                        'title': 'Да',
                        'hide': True
                    },
                    {
                        'title': 'Нет',
                        'hide': True
                    },
                    {
                        'title': 'Помощь',
                        'hide': True
                     }
                ]
    else:
        frasa = None
        res['response']['text'] = 'Неправильно( Сыграем ещё?'
        res['response']['buttons'] = [
                    {
                        'title': 'Да',
                        'hide': True
                    },
                    {
                        'title': 'Нет',
                        'hide': True
                    },
                    {
                        'title': 'Помощь',
                        'hide': True
                     }
                ]
    # сюда попадаем, если попытка отгадать не первая
    # проверяем есть ли правильный ответ в сообщение
    return


def stix(res, req):
    global stixi, frasa
    user_id = req['session']['user_id']
    if len(sessionStorage[user_id]['frasi']) == len(stixi.keys()):
        res['response']['text'] = 'Ты победил!'
        return
    if not frasa:
        frasa = random.choice(list(stixi.keys()))
        while frasa in sessionStorage[user_id]['frasi']:
            frasa = random.choice(list(stixi.eys()))
        res['response']['text'] = frasa
        random.shuffle(stixi[frasa])
        res['response']['buttons'] = []
        for i in stixi[frasa]:
            res['response']['buttons'].append(
                {
                    'title': i[1:],
                    'hide': True
                })
    elif f(stixi[frasa]) == req["request"]['original_utterance']:
        sessionStorage[user_id]['frasi'].append(frasa)
        frasa = None
        if len(sessionStorage[user_id]['frasi']) == len(stixi.keys()):
            res['response']['text'] = 'Ты победил!'
            res['end_session'] = True
            return
        res['response']['text'] = 'Правильно! Сыграем ещё?'
        res['response']['buttons'] = [
                    {
                        'title': 'Да',
                        'hide': True
                    },
                    {
                        'title': 'Нет',
                        'hide': True
                    },
                    {
                        'title': 'Помощь',
                        'hide': True
                     }
                ]
    else:
        frasa = None
        res['response']['text'] = 'Неправильно( Сыграем ещё?'
        res['response']['buttons'] = [
                    {
                        'title': 'Да',
                        'hide': True
                    },
                    {
                        'title': 'Нет',
                        'hide': True
                    },
                    {
                        'title': 'Помощь',
                        'hide': True
                     }
                ]
    # сюда попадаем, если попытка отгадать не первая
    # проверяем есть ли правильный ответ в сообщение
    return


def posl(res, req):
    global poslov, frasa
    user_id = req['session']['user_id']
    if len(sessionStorage[user_id]['frasi']) == len(poslov.keys()):
        res['response']['text'] = 'Ты победил!'
        return
    if not frasa:
        frasa = random.choice(list(poslov.keys()))
        while frasa in sessionStorage[user_id]['frasi']:
            frasa = random.choice(list(poslov.eys()))
        res['response']['text'] = frasa
        random.shuffle(poslov[frasa])
        res['response']['buttons'] = []
        for i in poslov[frasa]:
            res['response']['buttons'].append(
                {
                    'title': i[1:],
                    'hide': True
                })
    elif f(poslov[frasa]) == req["request"]['original_utterance']:
        sessionStorage[user_id]['frasi'].append(frasa)
        frasa = None
        if len(sessionStorage[user_id]['frasi']) == len(poslov.keys()):
            res['response']['text'] = 'Ты победил!'
            res['end_session'] = True
            return
        res['response']['text'] = 'Правильно! Сыграем ещё?'
        res['response']['buttons'] = [
                    {
                        'title': 'Да',
                        'hide': True
                    },
                    {
                        'title': 'Нет',
                        'hide': True
                    },
                    {
                        'title': 'Помощь',
                        'hide': True
                     }
                ]
    else:
        frasa = None
        res['response']['text'] = 'Неправильно( Сыграем ещё?'
        res['response']['buttons'] = [
                    {
                        'title': 'Да',
                        'hide': True
                    },
                    {
                        'title': 'Нет',
                        'hide': True
                    },
                    {
                        'title': 'Помощь',
                        'hide': True
                     }
                ]
    # сюда попадаем, если попытка отгадать не первая
    # проверяем есть ли правильный ответ в сообщение
    return


games = [stix, lat, posl]


def get_first_name(req):
    # перебираем сущности
    for entity in req['request']['nlu']['entities']:
        # находим сущность с типом 'YANDEX.FIO'
        if entity['type'] == 'YANDEX.FIO':
            # Если есть сущность с ключом 'first_name', то возвращаем её
            # значение.
            # Во всех остальных случаях возвращаем None.
            return entity['value'].get('first_name', None)


def f(mas):
    for i in mas:
        if i[0] == '1':
            return i[1:]


if __name__ == '__main__':
    app.run()
