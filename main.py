import telebot
import json
import requests
import sqlite3
import telegram
import os
TMDB_API = "5307bf927319fafbb85a482634b37473"
old = '1004646133:AAFan1Fh3Ke4KsiEcmiCYbTkUBSe5WO9WZc'
bot = telebot.TeleBot("5023163546:AAENN6w5oJXRB4594-Nu-ihMc3YjmOj4Gww")
types = telebot.types
data_ids = []
data_names = []
data_types = []
type = ''
MY_CHAT_ID = 156956400
types = telebot.types
def add(message, activity):
    conn = sqlite3.connect( 'chats.db' )
    c = conn.cursor()
    c.execute(f"INSERT INTO activity (first_name, last_name, username, chatid, activity) VALUES('{message.chat.first_name}', '{message.chat.last_name}', '{message.chat.username}', '{message.chat.id}', '{activity}')" )
    conn.commit()
    conn.close()
    print("added")
def search_in_valyria(key):
    return f"https://stoic-poitras-d9ed33.netlify.app/search/{key}"
def image_handler(url):
    return f'https://image.tmdb.org/t/p/original{url}'
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "https://stoic-poitras-d9ed33.netlify.app/Home")
    conn = sqlite3.connect( 'chats.db' )
    c = conn.cursor()
    c.execute( f"SELECT chatid from chats where chatid == {message.chat.id}" )
    rescheck = c.fetchall()
    if len( rescheck ) == 0:
        c.execute(
            f"INSERT INTO chats (firstname, lastname, username, chatid) VALUES('{message.chat.first_name}', '{message.chat.last_name}', '{message.chat.username}', '{message.chat.id}')" )
    conn.commit()
    conn.close()

def Searching(message):
    data = requests.get(
        f"https://api.themoviedb.org/3/search/multi?api_key={TMDB_API}&language=en-US&page=1&include_adult=false&query={message.text}" ).text
    add(message, f"searching==>{message.text}")
    datas = json.loads(data)['results']
    if len(datas) > 0:
        for i in datas:
            try:
                print(i['original_title'])
                bot.send_message(message.chat.id, i['original_title'])
            except KeyError:
                print(i['name'])
                bot.send_message(message.chat.id, i['name'])
        print(f"==>{message.text}")
        bot.send_message(message.chat.id, search_in_valyria(message.text))
    else:
        bot.send_message(message.chat.id, "No Results...")

@bot.message_handler(commands=['search'])
def Search(message):
    name = bot.reply_to(message, "Send The Name Movie, TVShow and Actors")
    bot.register_next_step_handler(name, pack_in_btns)
    if message.chat.id != MY_CHAT_ID:
        bot.send_message(MY_CHAT_ID, str(message.json), disable_notification=True)
    print(f"==>Search")

@bot.message_handler(commands=['trending'])
def Trending(message):
    keyboard = types.InlineKeyboardMarkup()
    data_ids.clear()
    data_names.clear()
    data_types.clear()
    day = types.InlineKeyboardButton( text='Day', callback_data='day' )
    week = types.InlineKeyboardButton( text='Week', callback_data="week" )
    keyboard.add( day )
    keyboard.add( week )
    if message.chat.id != MY_CHAT_ID:
        bot.send_message(MY_CHAT_ID, str(message.json), disable_notification=True)
    print(f"==>Trending")

    bot.send_message( message.chat.id, "Choose one:", reply_markup=keyboard )
@bot.message_handler(commands=['most_popular'])
def popular(message):
    keyboard = types.InlineKeyboardMarkup()
    moviek = types.InlineKeyboardButton( text='Movies', callback_data='movie' )
    keyboard.add( moviek )
    tv = types.InlineKeyboardButton( text='TVShows', callback_data='tv')
    keyboard.add(tv)
    print(f"==>Popular")
    bot.send_message( message.chat.id, "Choose one:", reply_markup=keyboard )
    if message.chat.id != MY_CHAT_ID:
        bot.send_message(MY_CHAT_ID, str(message.json), disable_notification=True)
def get_data(message):
    data = requests.get(
        f"https://api.themoviedb.org/3/search/multi?api_key={TMDB_API}&language=en-US&page=1&include_adult=false&query={message.text}" ).text
    for n, movie in enumerate(json.loads( data )['results']):
        id = movie['id']
        if movie['media_type'] == "movie":
            base_type = 'original_title'
        if movie['media_type'] == 'tv':
            base_type = 'name'
        if movie['media_type'] == "person":
            base_type = "name"

        name = movie[base_type]
        data_names.append(name)
        data_ids.append(movie['id'])
        data_types.append(movie['media_type'])


    return data_names
def runtime_handle(arr):
    if len(arr) > 0:
        count = 0
        for i in arr:
            count+=i
        return count / len(arr)
    else:
        return int(0)
def format_Time(time):
    if time > 60:
        hours = time / 60
        if time %60 > 9:
            res = time %60
        else:
            res = f"0{time%60}"
        time = f"{int(hours)}:{res}"
    else:
        time = time
    return time

def get_details(message, id, type):
    res = requests.get(f"https://api.themoviedb.org/3/{type}/{id}?api_key={TMDB_API}&language=en-US&append_to_response=external_ids`").text
    data = json.loads(res)
    if len(data) > 0:
        clock_list = ['🕐', '🕑', '🕒', '🕓', '🕔']
        genres = ''
        if type == "movie":
            name = f"🎥{data['original_title']}🎥"
            seasons = ""
            episodes = ""
            started = f"{data['release_date']}"
            runtime = f"{clock_list[int( data['runtime'] / 60 ) - 1]}{format_Time( int( data['runtime'] ) )}{clock_list[int( data['runtime'] / 60 ) - 1]}"
            network = f" Produced by {data['production_companies'][0]['name']}" if len(data['production_companies']) > 0 else ''
            for gen in data['genres']:
                genres += f" {gen['name']}"
            tagline = f"🎤<i>{data['tagline']}</i>🎤" if len( data['tagline'] ) > 0 and data['tagline'] != 'null' else ''
            votes = f"⭐{data['vote_average']} / 10 ({data['vote_count']}) Votes⭐"
            desc = f"📝{data['overview']}📝"
            poster = data['poster_path']
            backdrop = data['backdrop_path']
        if type == "tv":
            name = f"📺{data['name']}📺"
            seasons = f"{data['number_of_seasons']} Season"
            episodes = f"{data['number_of_episodes']} Episodes"
            started = f"{data['first_air_date']} ➡️{data['last_air_date']}"
            print(f"runtime ${data['episode_run_time']}")
            runtime = int( runtime_handle( data['episode_run_time'] ) )
            tagline = f"🎤<i>{data['tagline']}</i>🎤" if len( data['tagline'] ) > 0 and data['tagline'] != 'null' else ''
            network = f" Produced by {data['networks'][0]['name']}"
            desc = f"📝{data['overview']}📝"
            poster = data['poster_path']
            backdrop = data['backdrop_path']
            votes = f"⭐{data['vote_average']} / 10 ({data['vote_count']}) Votes⭐"

        if type == "person":
            name = f"👱{data['name']}👱‍" if data['gender'] == 1 else  f"👱‍{data['name']}👱‍‍"
            desc = data['biography']
            seasons = data['birthday']
            episodes = data['deathday'] if data['deathday'] != 'null' or data['deathday'] != 'None' else ''
            poster = data['profile_path']
            tagline = data['known_for_department']
            network = data['place_of_birth']
            votes, runtime, started = '', '', ''
            try:
                backdrop = data['backdrop_path']
            except KeyError:
                backdrop = ''
        print( f"==>{name}" )
        add(message, f"get details for {name}")
        msg = f"""<a href='{data['homepage']}'><b>{name}</b></a>:\r\n
        ----------------------------\r\n{desc}\r\n{tagline}\r\n{votes}\r\n{runtime}\r\n{seasons}\r\n{episodes}\r\n{started}\r\n{network}\r\n
        """
        print(poster)
        if os.path.exists(f"poster{poster[0:]}") == False:
            file = requests.get(image_handler(poster)).content
            # file.write(requests.get(image_handler(poster)).content)
            # file.close()
        if len(msg) > 1024:
            bot.send_message(message.chat.id, msg, parse_mode="html")
            if poster != '' and poster != 'null':
                bot.send_photo(message.chat.id, requests.get(image_handler(poster)).content)
        else:
            bot.send_photo(message.chat.id, requests.get(image_handler(poster)).content, msg, parse_mode="html")
        if backdrop != '' and backdrop != 'null':
            print(f"backdrop{backdrop[0:]}")
            if os.path.exists(f"backdrop{backdrop[0:]}") == False:
                file = requests.get(image_handler(backdrop)).content
                # file.write(requests.get(image_handler(backdrop)).content)
                # file.close()
            if len(msg) > 1024:
                bot.send_message(message.chat.id, msg, parse_mode="html")
                if backdrop != '' and backdrop != 'null':
                    bot.send_photo(message.chat.id, requests.get(image_handler(backdrop)).content)
            else:
                bot.send_photo(message.chat.id, requests.get(image_handler(backdrop)).content)
        bot.send_message( message.chat.id, f"https://stoic-poitras-d9ed33.netlify.app/Movie/{type}/{data['id']}" )
        if type == "person":
            data = requests.get(f"https://api.themoviedb.org/3/person/{data['id']}/images?api_key=5307bf927319fafbb85a482634b37473").text
            profiles = []
            profiles = json.loads(data)
            profiles = profiles['profiles']
            fixed_img = []
            if len(profiles) > 0:
                s = bot.send_message(message.chat.id, "Sending Photos...")
                for img in profiles:
                    img_url = image_handler(img['file_path'])
                    name = os.path.basename(img_url)
                    print(f"actor{name}")

                    file = requests.get(img_url).content
                    # file.write(requests.get(img_url).content)
                    # file.close()
                    fixed_img.append(file)
                inputs = []
                for profile in fixed_img:
                    inputs.append(types.InputMediaPhoto(profile))
                # if len(profiles) == 1:
                #     bot.send_photo(message.chat.id, )
                if len(profiles) < 5:
                    bot.send_media_group(message.chat.id, inputs)
                else:
                    extras_of_group = len(profiles) % 5
                    print(inputs)
                    for n, profile in enumerate(profiles):
                        print(n - 5)
                        print(n)
                        if n % 5 == 0 and n >= 5:
                            print("send")
                            bot.send_media_group(message.chat.id, inputs[n-5:n])
                    if extras_of_group > 0:
                        bot.send_media_group(message.chat.id, inputs[len(inputs)-extras_of_group:])
                    else:
                        bot.send_media_group(message.chat.id, inputs[len(inputs)-5:])
        #bot.delete_message(message.chat.id, s.id)
        bot.send_message(message.chat.id, "End Results...")
    else:
        bot.send_message(message.chat.id, "No Results...")
def pack_in_btns(message):
    keyboard = types.InlineKeyboardMarkup()
    data_ids.clear()
    data_names.clear()
    data_types.clear()
    get_d = get_data(message)
    if len(get_d) > 0:
        for n, d in enumerate(get_d):
            button_x64 = types.InlineKeyboardButton( text=data_names[n], callback_data=f"{data_ids[n]}*|*{data_types[n]}" )
            keyboard.add( button_x64 )
        bot.send_message( message.chat.id,"Choose one:", reply_markup=keyboard )
    else:
        bot.send_message(message.chat.id, "No Results...")
        Search(message)
def send_handler(id, name_poster, files, msg, url):
    print(name_poster)
    if len(msg) <= 1024:
        cap = msg
    else:
        cap = ''
    if name_poster in files:
        print("here")
        img = requests.get(url).content
    else:
        print("not here")
        # f = open(name_poster, 'wb')
        # f.write(requests.get(url).content)
        # f.close()
        img = requests.get(url).content
    bot.send_photo(id, img)
    # img.close()
def datas_handler(id, data):
    files = os.listdir()
    for n, movie in enumerate(data['results']):
        poster = movie['poster_path'] if movie['poster_path'] != 'null' and movie['poster_path'] != '' else ''
        votes = f"⭐{movie['vote_average']}⭐" if movie['vote_average'] != 'null' and movie['vote_average'] != '' else ''
        desc = f"📝{movie['overview']}📝" if movie['overview'] != 'null' and movie['overview'] != '' else ''
        try:  # movie
            name = f"🎥{movie['original_title']}🎥"
            release_date = movie['release_date'] if movie['release_date'] != 'null' and movie['release_date'] != '' else ''
            url = f"------https://stoic-poitras-d9ed33.netlify.app/Movie/movie/{movie['id']}"
        except KeyError:  # tv
            name = f"📺{movie['original_name']}📺"
            release_date = movie['first_air_date'] if movie['first_air_date'] != 'null' and movie['first_air_date'] != '' else ''
            url = f"------https://stoic-poitras-d9ed33.netlify.app/Movie/tv/{movie['id']}"

        msg = f"""#{n+1}{name}\r\n{release_date}\r\n{votes}\r\n{desc}\r\n{url}"""
        bot.send_message( id, msg, parse_mode='html' )

        print(files)
        if poster != '' and poster != 'null' and poster != None:
            url = image_handler(poster)
            name_poster = f"poster/{movie['poster_path'][1:]}"
            print(name_poster)

            send_handler(id, name_poster, files, msg, url)

        if movie['backdrop_path'] != '' and movie['backdrop_path'] != 'null' and movie['backdrop_path'] != None:
            print(movie['backdrop_path'])
            url = image_handler(movie['backdrop_path'])
            name_backdrop = f"backdrop/{movie['backdrop_path'][1:]}"
            send_handler(id, name_backdrop, files, msg, url)
        # else:
        #     bot.send_photo( id, image_handler( poster ), msg, parse_mode='html' )


    bot.send_message(id, "End Results...")
def handle_messages(message):
    print("update")

@bot.callback_query_handler( func=lambda call: True )
def callback_worker(call):
    if call.message.chat.id != MY_CHAT_ID:
        bot.send_message( MY_CHAT_ID, f"{str( call.message.json)} ", disable_notification=True)
    if call.data.find("*|*") > -1:
        datas = call.data.split("*|*")
        print(datas)
        print(call.message.chat.id)
        get_details(call.message, datas[0], datas[1])
    if call.data == "day" or call.data == "week":
        add(call.message, f"trending.{call.data}")
        datas = requests.get(f"https://api.themoviedb.org/3/trending/all/{call.data}?api_key={TMDB_API}").text
        data = json.loads(datas)
        datas_handler(call.message.chat.id, data)
    if call.data == 'movie' or call.data == 'tv':
        add(call.message, f"popular.{call.data}")
        datas=requests.get(f"https://api.themoviedb.org/3/discover/{call.data}?api_key={TMDB_API}&language=enUS&sort_by=popularity.desc&include_adult=false&include_video=false&page=1&with_watch_monetization_types=flatrate").text
        data = json.loads(datas)
        datas_handler(call.message.chat.id, data)

bot.set_update_listener(handle_messages)
bot.polling()
