import telebot
from data import db_session, folders, notes, users, music, photos, documents

TOKEN = TOKEN
bot = telebot.TeleBot(TOKEN)
keyboard1 = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)


@bot.message_handler(commands=['start'])
def start_message(message):
    keyboard1 = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    sessions = db_session.create_session()
    try:
        sessions = db_session.create_session()
        all_folders = sessions.query(folders.Folder).all()
        for i in all_folders:
            if i.user_id == message.from_user.id:
                keyboard1.add(str(i.names_folders))
        keyboard1.add('Добавить Папку')
    except Exception:
        keyboard1.add('Добавить Папку')
    all_users = sessions.query(users.User).all()
    all_users_id = []
    if len(all_users) != 0:
        for i in all_users:
            all_users_id.append(i.user_id)
    if message.from_user.id not in all_users_id:
        user = users.User(user_id=message.from_user.id)
        sessions.add(user)
        sessions.commit()
    bot.send_message(message.chat.id, "Привет 👋\nЯ бот, который поможет вам хранить все ваши записи/музыку "
                                      "удобным способом! Вы можете добавлять папки и "
                                      "хранить любые заметки/музыку в них 🙂",
                     reply_markup=keyboard1)


@bot.message_handler(content_types=['text'])
def dropper(message):
    sessions = db_session.create_session()
    all_folders = sessions.query(folders.Folder).filter(
        folders.Folder.user_id == message.from_user.id).all()
    temp = False
    for i in range(len(all_folders)):
        if message.text == all_folders[i].names_folders:
            temp = True
            break
        else:
            temp = False
    if message.text == 'Добавить Папку':
        keyboard_cancle = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard_cancle.add("Отменить")
        send = bot.send_message(message.chat.id, "Введите название папки",
                                reply_markup=keyboard_cancle)
        bot.register_next_step_handler(send, addFolder)
    elif temp:
        all_folders = sessions.query(folders.Folder).filter(
            folders.Folder.user_id == message.from_user.id and message.text ==
            folders.Folder.names_folders).all()
        for i in all_folders:
            if i.in_folder == "now" and i.user_id == message.from_user.id:
                i.in_folder = ""
                sessions.commit()
            if i.names_folders == message.text and i.user_id == message.from_user.id:
                i.in_folder = "now"
                sessions.commit()
        keyboard_folder = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard_folder.add("Добавить Запись 📝")
        keyboard_folder.add("Переименовать Папку ✏️")
        keyboard_folder.add("Удалить Папку 🗑")
        keyboard_folder.add("Вернуться ⬅️")
        inline_kb = telebot.types.InlineKeyboardMarkup()
        try:
            all_notes = sessions.query(notes.Note).filter(
                notes.Note.user_id == message.from_user.id and notes.Note.folder_id == all_folders[
                    0].id).all()
            all_folders = sessions.query(folders.Folder).all()
            for i in all_folders:
                if i.in_folder == "now" and i.user_id == message.from_user.id:
                    you_folder_id = i.id
            note_block = None
            count_btn = 1
            for i in all_notes:
                if int(i.folder_id) == int(you_folder_id):
                    note_block = i
            for i in note_block.user_notes.split(";0;"):
                  inline_kb.add(telebot.types.InlineKeyboardButton(i.split("25:07:..04")[0].split(';')[-1], callback_data='btn' + str(count_btn)))
                  count_btn += 1
        except Exception:
            pass
        bot.send_message(message.chat.id, "Вы перешли в папку", reply_markup=keyboard_folder)
        send = bot.send_message(message.chat.id, "*" + str(message.text) + "*", parse_mode="Markdown", reply_markup=inline_kb)
        bot.register_next_step_handler(send, NotesOperations)


def addFolder(message):
    name_folder = message.text
    if message.text == "Отменить":
        sessions = db_session.create_session()
        all_folders = sessions.query(folders.Folder).filter(
            folders.Folder.user_id == message.from_user.id).all()
        keyboard2 = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        for i in range(len(all_folders)):
            keyboard2.add(all_folders[i].names_folders)
        keyboard2.add('Добавить Папку')
        bot.send_message(message.chat.id, "Операция отменена", reply_markup=keyboard2)
    else:
        if type(message.text) is str:
            sessions = db_session.create_session()
            data = sessions.query(folders.Folder).all()
            name_fs = []
            is_next = True
            for i in data:
                if i.user_id == message.from_user.id:
                    name_fs.append(str(i.names_folders))
            if str(name_folder) in name_fs:
                is_next = False
            if is_next:
                sessions = db_session.create_session()
                folder = folders.Folder(user_id=message.from_user.id, names_folders=name_folder,
                                        in_folder='')
                sessions.add(folder)
                sessions.commit()
                all_folders = sessions.query(folders.Folder).filter(
                    folders.Folder.user_id == message.from_user.id).all()
                note = notes.Note(user_id=message.from_user.id, folder_id=all_folders[-1].id,
                                  user_notes='')
                sessions.add(note)
                sessions.commit()
                all_folders = sessions.query(folders.Folder).filter(
                    folders.Folder.user_id == message.from_user.id).all()
                keyboard2 = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
                for i in range(len(all_folders)):
                    keyboard2.add(all_folders[i].names_folders)
                keyboard2.add('Добавить Папку')
                send = bot.send_message(message.chat.id, "Папка успешно добавлена ✅",
                                        reply_markup=keyboard2)
                bot.register_next_step_handler(send, dropper)
            else:
                keyboard2 = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
                for i in name_fs:
                    keyboard2.add(i)
                keyboard2.add('Добавить Папку')
                bot.send_message(message.chat.id, "Папка с таким названием уже существует",
                                 reply_markup=keyboard2)
        else:
            if message.content_type == "audio":
                bot.delete_message(message.chat.id, message.message_id)
            keyboard2 = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            sessions = db_session.create_session()
            data = sessions.query(folders.Folder).all()
            name_fs = []
            for i in data:
                name_fs.append(str(i.names_folders))
            for i in name_fs:
                keyboard2.add(i)
            keyboard2.add('Добавить Папку')
            send = bot.send_message(message.chat.id, "Не корректное имя папки ❌\nВведите название папки",
                             reply_markup=keyboard2)
            bot.register_next_step_handler(send, addFolder)


def choose_type(message, title_note):
    if message.text == "Текстовая":
        keyboard_cancler = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard_cancler.add("Отменить")
        send = bot.send_message(message.chat.id, "Теперь введите содержание заметки",
                                reply_markup=keyboard_cancler)
        bot.register_next_step_handler(send, addNote, title_note)
    elif message.text == "Музыкальная":
        sessions = db_session.create_session()
        all_folders = sessions.query(
            folders.Folder).all()  # нужно проверять folder id с id папки в которыю перешёл пользователь, а я спать 23:00 всё таки!
        for i in all_folders:
            if i.in_folder == "now" and i.user_id == message.from_user.id:
                you_folder_id = i.id
        all_notes = sessions.query(notes.Note).all()
        note_block = None
        for i in all_notes:
            if i.user_id == message.from_user.id and i.folder_id == you_folder_id:
                note_block = i
        if ";-string-;" + str(title_note) not in note_block.user_notes.split("25:07:..04")\
                and ";-music-;" + str(title_note) not in note_block.user_notes.split("25:07:..04")\
                and ";-album-;" + str(title_note) not in note_block.user_notes.split("25:07:..04")\
                and ";-docs-;" + str(title_note) not in note_block.user_notes.split("25:07:..04"):
            note_block.user_notes = note_block.user_notes + ";-music-;" + str(title_note) + "25:07:..04;0;"
            sessions.commit()
            bot.send_message(message.chat.id, "Запись успешно добавлена ✅")
            print_folder(message)
        else:
            bot.send_message(message.chat.id, "Данная запись уже существует в этой папке ❌")
            print_folder(message)
    elif message.text == "Альбомная":

        sessions = db_session.create_session()
        all_folders = sessions.query(
            folders.Folder).all()  # нужно проверять folder id с id папки в которыю перешёл пользователь, а я спать 23:00 всё таки!
        for i in all_folders:
            if i.in_folder == "now" and i.user_id == message.from_user.id:
                you_folder_id = i.id
        all_notes = sessions.query(notes.Note).all()
        note_block = None
        for i in all_notes:
            if i.user_id == message.from_user.id and i.folder_id == you_folder_id:
                note_block = i
        if ";-string-;" + str(title_note) not in note_block.user_notes.split("25:07:..04") \
                and ";-music-;" + str(title_note) not in note_block.user_notes.split("25:07:..04")\
                and ";-album-;" + str(title_note) not in note_block.user_notes.split("25:07:..04")\
                and ";-docs-;" + str(title_note) not in note_block.user_notes.split("25:07:..04"):
            note_block.user_notes = note_block.user_notes + ";-album-;" + str(
                title_note) + "25:07:..04;0;"
            sessions.commit()
            bot.send_message(message.chat.id, "Запись успешно добавлена ✅")
            print_folder(message)
        else:
            bot.send_message(message.chat.id, "Данная запись уже существует в этой папке ❌")
            print_folder(message)
    elif message.text == "Файловая":
        sessions = db_session.create_session()
        all_folders = sessions.query(
            folders.Folder).all()  # нужно проверять folder id с id папки в которыю перешёл пользователь, а я спать 23:00 всё таки!
        for i in all_folders:
            if i.in_folder == "now" and i.user_id == message.from_user.id:
                you_folder_id = i.id
        all_notes = sessions.query(notes.Note).all()
        note_block = None
        for i in all_notes:
            if i.user_id == message.from_user.id and i.folder_id == you_folder_id:
                note_block = i
        if ";-string-;" + str(title_note) not in note_block.user_notes.split("25:07:..04") \
                and ";-music-;" + str(title_note) not in note_block.user_notes.split("25:07:..04")\
                and ";-album-;" + str(title_note) not in note_block.user_notes.split("25:07:..04")\
                and ";-docs-;" + str(title_note) not in note_block.user_notes.split("25:07:..04"):
            note_block.user_notes = note_block.user_notes + ";-docs-;" + str(
                title_note) + "25:07:..04;0;"
            sessions.commit()
            bot.send_message(message.chat.id, "Запись успешно добавлена ✅")
            print_folder(message)
        else:
            bot.send_message(message.chat.id, "Данная запись уже существует в этой папке ❌")
            print_folder(message)

    else:
        if message.content_type == "audio":
            bot.delete_message(message.chat.id, message.message_id)
        send = bot.send_message(message.chat.id, "Вы что-то не то ввели")
        bot.register_next_step_handler(send, choose_type, title_note)


def NotesOperations(message):
    if message.text == "Добавить Запись 📝":
        keyboard_cancler = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard_cancler.add("Отменить")
        send = bot.send_message(message.chat.id, "Введите название записи",
                                reply_markup=keyboard_cancler)
        bot.register_next_step_handler(send, addTitleNote)
    elif message.text == "Удалить Папку 🗑":
        sessions = db_session.create_session()
        all_folders = sessions.query(folders.Folder).filter(
            folders.Folder.user_id == message.from_user.id).all()
        all_notes = sessions.query(notes.Note).all()
        #  Удаление папки
        del_folder = None
        for i in all_folders:
            if i.in_folder == "now" and i.user_id == message.from_user.id:
                del_folder = i
        del_note = None
        for i in all_notes:
            if i.folder_id == del_folder.id:
                del_note = i
        sessions.delete(del_folder)
        sessions.commit()

        del_files_id = []
        del_file_id = []
        for i in del_note.user_notes.split(";0;"):
            if len(i.split(";")) != 1:
                type_note = i.split(";")[1]
                if i.split(";")[1] == "-music-" or i.split(";")[1] == "-docs-" or i.split(";")[1] == "-album-":
                    del_files_id.append(i.split("25:07:..04")[-1].split("_-_"))
        for i in del_files_id:
            for j in i:
                if j != "":
                    del_file_id.append(j)

        #  Удаление м/ф/ф
        files_for_del = []
        for i in del_file_id:
            if type_note == "-music-":
                files_for_del.append(sessions.query(music.Musics).filter(
                    music.Musics.file_id == i).all())
            elif type_note == "-album-":
                files_for_del.append(sessions.query(photos.Photos).filter(
                    photos.Photos.file_id == i).all())
            elif type_note == "-docs-":
                files_for_del.append(sessions.query(documents.Document).filter(
                    documents.Document.file_id == i).all())
        for i in files_for_del:
            if len(i) != 0:
                sessions.delete(i[0])
                sessions.commit()

        sessions.delete(del_note)
        sessions.commit()
        all_folders = sessions.query(folders.Folder).filter(
            folders.Folder.user_id == message.from_user.id).all()
        keyboard2 = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        for i in range(len(all_folders)):
            keyboard2.add(all_folders[i].names_folders)
        keyboard2.add('Добавить Папку')
        send = bot.send_message(message.chat.id, "Папка успешно удалена ✅",
                         reply_markup=keyboard2)
        bot.register_next_step_handler(send, dropper)
    elif message.text == "Переименовать Папку ✏️":
        keyboard_cancler = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard_cancler.add("Отменить")
        send = bot.send_message(message.chat.id, "Введите новое название папки", reply_markup=keyboard_cancler)
        bot.register_next_step_handler(send, renameFolder)
    elif message.text == "Вернуться ⬅️":
        sessions = db_session.create_session()
        all_folders = sessions.query(folders.Folder).filter(
            folders.Folder.user_id == message.from_user.id).all()
        keyboard2 = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        for i in range(len(all_folders)):
            keyboard2.add(all_folders[i].names_folders)
        keyboard2.add('Добавить Папку')
        send = bot.send_message(message.chat.id, "Операция выполнена",
                         reply_markup=keyboard2)
        bot.register_next_step_handler(send, dropper)
    elif message.text == "Изменить Запись ✏️" or message.text == "Переименовать Запись ✏️" \
            or message.text == "Вернуться ↩️" or message.text == "Удалить Запись 🗑" or \
            message.text == "Добавить Аудиозапись 🔊" or message.text == "Удалить Аудиозапись 🔇"\
            or message.text == "Добавить Картинку 🌇" or message.text == "Удалить Картинку 🌃"\
            or message.text == "Добавить Файл 💾" or message.text == "Удалить Файл 📂":
        pass
    else:
        if message.content_type == "audio":
            bot.delete_message(message.chat.id, message.message_id)
        keyboard_folder = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard_folder.add("Добавить Запись 📝")
        keyboard_folder.add("Переименовать Папку ✏️")
        keyboard_folder.add("Удалить Папку 🗑")
        keyboard_folder.add("Вернуться ⬅️")
        send = bot.send_message(message.chat.id, "Вы что-то не то написали",
                                reply_markup=keyboard_folder)
        bot.register_next_step_handler(send, NotesOperations)


def renameFolder(message):
    if message.text == "Отменить":
        send = bot.send_message(message.chat.id, "Операция отменена")
        bot.register_next_step_handler(send, dropper)
        print_folder(message)
    elif type(message.text) is not str:
        if message.content_type == "audio":
            bot.delete_message(message.chat.id, message.message_id)
        keyboard_cancler = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard_cancler.add("Отменить")
        send = bot.send_message(message.chat.id, "Не корректное название папки ❌\nВведите название папки", reply_markup=keyboard_cancler)
        bot.register_next_step_handler(send, renameFolder)
    else:
        sessions = db_session.create_session()
        all_folders = sessions.query(folders.Folder).filter(
            folders.Folder.user_id == message.from_user.id).all()
        rename_folder = None
        for i in all_folders:
            if i.in_folder == "now" and i.user_id == message.from_user.id:
                rename_folder = i
        rename_folder.names_folders = message.text
        sessions.commit()
        send = bot.send_message(message.chat.id, "Папка переименована ✅")
        bot.register_next_step_handler(send, dropper)
        print_folder(message)


def goToTheNote(message, num_note):
    sessions = db_session.create_session()
    all_notes = sessions.query(notes.Note).all()
    note_block = None
    all_folders = sessions.query(folders.Folder).all()
    for i in all_folders:
        if i.in_folder == "now" and i.user_id == message.chat.id:
            you_folder_id = i.id
    for i in all_notes:
        if int(i.folder_id) == int(you_folder_id):
            note_block = i
    right_note = None
    for i in note_block.user_notes.split(";0;"):
        if i.split("25:07:..04")[0] == note_block.user_notes.split(";0;")[int(num_note) - 1].split("25:07:..04")[0]:
            right_note = i
    audio_messages = []
    if right_note is not None:
        keyboard2 = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        if right_note.split(";")[1] == "-music-":
            keyboard2.add("Добавить Аудиозапись 🔊")
            keyboard2.add("Удалить Аудиозапись 🔇")
        elif right_note.split(";")[1] == "-album-":
            keyboard2.add("Добавить Картинку 🌇")
            keyboard2.add("Удалить Картинку 🌃")
        elif right_note.split(";")[1] == "-docs-":
            keyboard2.add("Добавить Файл 💾")
            keyboard2.add("Удалить Файл 📂")
        keyboard2.add("Удалить Запись 🗑")
        if right_note.split(";")[1] == "-music-" or right_note.split(";")[1] == "-album-" or \
                right_note.split(";")[1] == "-docs-":
            keyboard2.add("Переименовать Запись ✏️")
        else:
            keyboard2.add("Изменить Запись ✏️")
        keyboard2.add("Вернуться ↩️")
        if right_note.split(";")[1] == "-music-":
            send = bot.send_message(message.chat.id, "*" +
                             right_note.split("25:07:..04")[0].split(";")[-1] + "*",
                             parse_mode="Markdown",
                             reply_markup=keyboard2)
            try:
                new_l = right_note.split("25:07:..04")[1].split("_-_")
                while "" in new_l:
                    new_l.remove("")
                lst_notes = []
                lst_comp_notes = []
                au_mes = []
                for i in range(len(new_l)):
                    if i % 10 == 0 and i != 0:
                        lst_comp_notes.append(lst_notes)
                        lst_notes = []
                    lst_notes.append(new_l[i])
                lst_comp_notes.append(lst_notes)
                for i in lst_comp_notes:
                    send = bot.send_media_group(message.chat.id,
                                    [telebot.types.InputMediaAudio(music_message)
                                     for music_message in i])
                    au_mes.append(send)
                for i in au_mes:
                    for j in i:
                        audio_messages.append(j)
            except Exception:
                pass
        elif right_note.split(";")[1] == "-album-":
            try:
                send = bot.send_message(message.chat.id, "*" +
                                        right_note.split("25:07:..04")[0].split(";")[-1] + "*",
                                        parse_mode="Markdown",
                                        reply_markup=keyboard2)
                new_l = right_note.split("25:07:..04")[1].split("_-_")
                while "" in new_l:
                    new_l.remove("")
                lst_notes = []
                lst_comp_notes = []
                for i in range(len(new_l)):
                    if i % 10 == 0 and i != 0:
                        lst_comp_notes.append(lst_notes)
                        lst_notes = []
                    lst_notes.append(new_l[i])
                lst_comp_notes.append(lst_notes)
                for i in lst_comp_notes:
                    send = bot.send_media_group(message.chat.id,
                                    [telebot.types.InputMediaPhoto(photo) for photo in i])
            except Exception:
                pass
        elif right_note.split(";")[1] == "-docs-":
            send = bot.send_message(message.chat.id, "*" +
                                    right_note.split("25:07:..04")[0].split(";")[-1] + "*",
                                    parse_mode="Markdown",
                                    reply_markup=keyboard2)
            try:
                new_l = right_note.split("25:07:..04")[1].split("_-_")
                while "" in new_l:
                    new_l.remove("")
                for i in new_l:
                    send = bot.send_document(message.chat.id, data=i)
            except Exception:
                pass
        else:
            send = bot.send_message(message.chat.id, "*" +
                                    right_note.split("25:07:..04")[0].split(";")[-1] + "*\n" +
                                    right_note.split("25:07:..04")[1], parse_mode="Markdown",
                                    reply_markup=keyboard2)
        if type(send) is list:
            send = send[-1]
        bot.register_next_step_handler(send, inNote, right_note.split("25:07:..04")[0], num_note, audio_messages)
    else:
        if message.content_type == "audio":
            bot.delete_message(message.chat.id, message.message_id)
        keyboard_folder = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard_folder.add("Добавить Запись 📝")
        keyboard_folder.add("Переименовать Папку ✏️")
        keyboard_folder.add("Удалить Папку 🗑")
        keyboard_folder.add("Вернуться ⬅️")
        send = bot.send_message(message.chat.id, "Данной записи не существует",
                                reply_markup=keyboard_folder)
        bot.register_next_step_handler(send, NotesOperations)


def inNote(message, name_note, num_note, audio_messages=None):
    if message.text == "Вернуться ↩️":
        if not audio_messages is None:
            for i in audio_messages:
                bot.delete_message(message.chat.id, i.message_id)
        send = bot.send_message(message.chat.id, "Операция выполнена")
        bot.register_next_step_handler(send, dropper)
        print_folder(message)
    elif message.text == "Удалить Запись 🗑":
        sessions = db_session.create_session()
        all_notes = sessions.query(notes.Note).all()
        all_folders = sessions.query(folders.Folder).all()
        for i in all_folders:
            if i.in_folder == "now" and i.user_id == message.from_user.id:
                you_folder_id = i.id
        #  Удаление записи
        del_note = None
        for i in all_notes:
            if int(you_folder_id) == int(i.folder_id):
                del_note = i
        type_note = del_note.user_notes.split(";")[1]
        if del_note.user_notes.split(";")[1] == "-music-" or \
                del_note.user_notes.split(";")[1] == "-docs-" or \
                del_note.user_notes.split(";")[1] == "-album-":
            del_file_id = []
            for i in del_note.user_notes.split("25:07:..04")[-1].split("_-_"):
                if i != "":
                    try:
                        del_file_id.append(i.split(";0;")[0])
                    except Exception:
                        del_file_id.append(i.split)
            #  Удаление м/ф/ф
            files_for_del = []
            for i in del_file_id:
                if type_note == "-music-":
                    files_for_del.append(sessions.query(music.Musics).filter(
                        music.Musics.file_id == i).all())
                elif type_note == "-album-":
                    files_for_del.append(sessions.query(photos.Photos).filter(
                        photos.Photos.file_id == i).all())
                elif type_note == "-docs-":
                    files_for_del.append(sessions.query(documents.Document).filter(
                        documents.Document.file_id == i).all())
            for i in files_for_del:
                if len(i) != 0:
                    sessions.delete(i[0])
                    sessions.commit()
        new_note = []
        for i in del_note.user_notes.split(";0;"):
            if i.split("25:07:..04")[0] != name_note:
                new_note.append(i)
        del_note.user_notes = str(';0;'.join(new_note))
        sessions.commit()
        if not audio_messages is None:
            for i in audio_messages:
                bot.delete_message(message.chat.id, i.message_id)
        bot.send_message(message.chat.id, "Запись удалена ✅")
        print_folder(message)
    elif message.text == "Изменить Запись ✏️":
        keyboard_cancler = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard_cancler.add("Отменить")
        send = bot.send_message(message.chat.id, "Введите новое название записи (0 - неизменять)", reply_markup=keyboard_cancler)
        bot.register_next_step_handler(send, editNoteTitle, name_note, num_note, "str")
    elif message.text == "Переименовать Запись ✏️":
        keyboard_cancler = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        if not audio_messages is None:
            for i in audio_messages:
                bot.delete_message(message.chat.id, i.message_id)
        keyboard_cancler.add("Отменить")
        send = bot.send_message(message.chat.id, "Введите новое название записи (0 - неизменять)",
                                reply_markup=keyboard_cancler)
        bot.register_next_step_handler(send, editNoteTitle, name_note, num_note, "other")
    elif message.text == "Добавить Аудиозапись 🔊":
        keyboard_cancler = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard_cancler.add("Отменить")
        if not audio_messages is None:
            for i in audio_messages:
                bot.delete_message(message.chat.id, i.message_id)
        send = bot.send_message(message.chat.id, "Пришлите мне аудиофайл", reply_markup=keyboard_cancler)
        bot.register_next_step_handler(send, addAudio, name_note, num_note)
    elif message.text == "Удалить Аудиозапись 🔇":
        sessions = db_session.create_session()
        keyboard_cancler = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        all_music = sessions.query(music.Musics).all()
        list_music = []
        count = 1
        # В list_notes сложить все заметки пользователя
        all_notes = sessions.query(notes.Note).all()
        note_block = None
        all_folders = sessions.query(folders.Folder).all()
        for i in all_folders:
            if i.in_folder == "now" and i.user_id == message.chat.id:
                you_folder_id = i.id
        for i in all_notes:
            if int(i.folder_id) == int(you_folder_id):
                note_block = i
        list_notes = note_block.user_notes.split("25:07:..04")[1].split("_-_")
        while "" in list_notes:
            list_notes.remove("")
        for i in all_music:
            if i.file_id + ";0;" in list_notes or i.file_id in list_notes:
                list_music.append(str(count) + ". " + i.name)
                count += 1
        if not audio_messages is None:
            for i in audio_messages:
                bot.delete_message(message.chat.id, i.message_id)
        bot.send_message(message.chat.id, "*" + name_note.split(";")[-1] + "*" + "\n" +
                         "\n".join(list_music),
                         parse_mode="Markdown")
        keyboard_cancler.add("Отменить")
        send = bot.send_message(message.chat.id, "Введите номера аудиозаписей, которые хотите удалить (1) (1, 2, 3)",
                                reply_markup=keyboard_cancler)
        bot.register_next_step_handler(send, deleteAudio, name_note, num_note)
    elif message.text == "Добавить Картинку 🌇":
        keyboard_cancler = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard_cancler.add("Отменить")
        send = bot.send_message(message.chat.id, "Пришлите мне картинку",
                                reply_markup=keyboard_cancler)
        bot.register_next_step_handler(send, addPhoto, name_note, num_note)
    elif message.text == "Удалить Картинку 🌃":
        goToTheNote(message, num_note)
        keyboard_cancler = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard_cancler.add("Отменить")
        send = bot.send_message(message.chat.id,
                                "Введите номера страниц и картинок (через тире), которые хотите удалить (1-1) (1-3, 2-9, 3-2)",
                                reply_markup=keyboard_cancler)
        bot.register_next_step_handler(send, deletePhoto, name_note, num_note)
    elif message.text == "Добавить Файл 💾":
        keyboard_cancler = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard_cancler.add("Отменить")
        send = bot.send_message(message.chat.id, "Пришлите мне файл",
                                reply_markup=keyboard_cancler)
        bot.register_next_step_handler(send, addDoc, name_note, num_note)
    elif message.text == "Удалить Файл 📂":
        sessions = db_session.create_session()
        keyboard_cancler = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        all_docs = sessions.query(documents.Document).all()
        list_docs = []
        count = 1
        # В list_notes сложить все заметки пользователя
        all_notes = sessions.query(notes.Note).all()
        note_block = None
        all_folders = sessions.query(folders.Folder).all()
        for i in all_folders:
            if i.in_folder == "now" and i.user_id == message.chat.id:
                you_folder_id = i.id
        for i in all_notes:
            if int(i.folder_id) == int(you_folder_id):
                note_block = i
        list_notes = note_block.user_notes.split("25:07:..04")[1].split("_-_")
        while "" in list_notes:
            list_notes.remove("")
        for i in all_docs:
            if i.file_id + ";0;" in list_notes or i.file_id in list_notes:
                list_docs.append(str(count) + ". " + i.name)
                count += 1
        bot.send_message(message.chat.id, "*" + name_note.split(";")[-1] + "*" + "\n" +
                         "\n".join(list_docs),
                         parse_mode="Markdown")
        keyboard_cancler.add("Отменить")
        send = bot.send_message(message.chat.id,
                                "Введите номера файлов, которые хотите удалить (1) (1, 2, 3)",
                                reply_markup=keyboard_cancler)
        bot.register_next_step_handler(send, deleteDoc, name_note, num_note)
    else:
        if "-" not in message.text:
            keyboard2 = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard2.add("Удалить Запись 🗑")
            keyboard2.add("Изменить Запись ✏️")
            keyboard2.add("Вернуться ↩️")
            bot.send_message(message.chat.id, "Вы что-то не то ввели",
                             reply_markup=keyboard2)
            goToTheNote(message, num_note)


def addDoc(message, name_note, num_note):
    if message.text == "Отменить":
        bot.send_message(message.chat.id, "Операция отменена")
        keyboard2 = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard2.add("Удалить Запись 🗑")
        keyboard2.add("Изменить Запись ✏️")
        keyboard2.add("Вернуться ↩️")
        goToTheNote(message, num_note)
    else:
        if message.content_type == "document":
            sessions = db_session.create_session()
            all_notes = sessions.query(notes.Note).all()
            all_folders = sessions.query(folders.Folder).all()
            all_docs = sessions.query(photos.Photos).all()
            docs = []
            for i in all_docs:
                docs.append(i)
            if message.document.file_id not in docs:
                ds = documents.Document(name=message.document.file_name,
                                        file_id=message.document.file_id)
                sessions.add(ds)
                sessions.commit()
            for i in all_folders:
                if i.in_folder == "now" and i.user_id == message.from_user.id:
                    you_folder_id = i.id
            edit_note = None
            for i in all_notes:
                if int(you_folder_id) == int(i.folder_id):
                    edit_note = i
            new_note = []
            counter = 0
            for i in edit_note.user_notes.split(";0;"):
                if i.split(":")[0] != name_note:
                    if counter == int(num_note) - 1:
                        temp = i.split("25:07:..04")
                        temp[1] = temp[1] + "_-_" + message.document.file_id
                        new_note.append("25:07:..04".join(temp))
                    else:
                        new_note.append(i)
                    counter += 1
            edit_note.user_notes = str(';0;'.join(new_note))
            sessions.commit()
            bot.send_message(message.chat.id, "Запись успешно добавлена ✅")

            keyboard2 = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard2.add("Удалить Запись 🗑")
            keyboard2.add("Изменить Запись ✏️")
            keyboard2.add("Вернуться ↩️")
            goToTheNote(message, num_note)
        else:
            keyboard_cancler = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard_cancler.add("Отменить")
            send = bot.send_message(message.chat.id, "Не верный формат ❌",
                                    reply_markup=keyboard_cancler)
            bot.register_next_step_handler(send, addAudio, name_note, num_note)


def deleteDoc(message, name_note, num_note):
    if message.text == "Отменить":
        bot.send_message(message.chat.id, "Операция отменена")
        keyboard2 = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard2.add("Удалить Запись 🗑")
        keyboard2.add("Изменить Запись ✏️")
        keyboard2.add("Вернуться ↩️")
        goToTheNote(message, num_note)
    else:
        try:
            sessions = db_session.create_session()
            all_notes = sessions.query(notes.Note).all()
            all_folders = sessions.query(folders.Folder).all()
            for i in all_folders:
                if i.in_folder == "now" and i.user_id == message.from_user.id:
                    you_folder_id = i.id
            edit_note = None
            for i in all_notes:
                if int(you_folder_id) == int(i.folder_id):
                    edit_note = i
            new_note = []
            counter = 0
            del_file_id = []
            for i in edit_note.user_notes.split(";0;"):
                if i.split(":")[0] != name_note:
                    if counter == int(num_note) - 1:
                        temp = i.split("25:07:..04")
                        new_list = temp[1].split("_-_")
                        while "" in new_list:
                            new_list.remove("")
                        if len(message.text) == 1:
                            del_file_id.append(new_list[int(message.text) - 1])
                            new_list.remove(new_list[int(message.text) - 1])
                        else:
                            counter = 1
                            for i in message.text.split(", "):
                                del_file_id.append(new_list[int(i) - counter])
                                new_list.remove(new_list[int(i) - counter])
                                counter += 1
                        new_note.append("_-_".join(new_list))
                    else:
                        new_note.append(i)
                    counter += 1
            edit_note.user_notes = temp[0] + "25:07:..04_-_" + str(';0;'.join(new_note))
            sessions.commit()

            #  Удаление доков
            docs_for_del = []
            for i in del_file_id:
                docs_for_del.append(sessions.query(documents.Document).filter(
                    documents.Document.file_id == i).all())
            for i in docs_for_del:
                sessions.delete(i[0])
                sessions.commit()

            keyboard2 = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard2.add("Удалить Запись 🗑")
            keyboard2.add("Изменить Запись ✏️")
            keyboard2.add("Вернуться ↩️")
            goToTheNote(message, num_note)
        except Exception:
            if message.content_type == "audio":
                bot.delete_message(message.chat.id, message.message_id)
            keyboard_cancler = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard_cancler.add("Отменить")
            send = bot.send_message(message.chat.id, "Не верный формат ❌",
                                    reply_markup=keyboard_cancler)
            bot.register_next_step_handler(send, deleteAudio, name_note, num_note)


def addPhoto(message, name_note, num_note):
    if message.text == "Отменить":
        bot.send_message(message.chat.id, "Операция отменена")
        keyboard2 = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard2.add("Удалить Запись 🗑")
        keyboard2.add("Изменить Запись ✏️")
        keyboard2.add("Вернуться ↩️")
        goToTheNote(message, num_note)
    else:
        if message.content_type == "photo":
            sessions = db_session.create_session()
            all_notes = sessions.query(notes.Note).all()
            all_folders = sessions.query(folders.Folder).all()
            all_photos = sessions.query(photos.Photos).all()
            phots = []
            for i in all_photos:
                phots.append(i)
            if message.photo[0].file_id not in phots:
                ph = photos.Photos(file_id=message.photo[0].file_id)
                sessions.add(ph)
                sessions.commit()
            for i in all_folders:
                if i.in_folder == "now" and i.user_id == message.from_user.id:
                    you_folder_id = i.id
            edit_note = None
            for i in all_notes:
                if int(you_folder_id) == int(i.folder_id):
                    edit_note = i
            new_note = []
            counter = 0
            for i in edit_note.user_notes.split(";0;"):
                if i.split(":")[0] != name_note:
                    if counter == int(num_note) - 1:
                        temp = i.split("25:07:..04")
                        temp[1] = temp[1] + "_-_" + message.photo[0].file_id
                        new_note.append("25:07:..04".join(temp))
                    else:
                        new_note.append(i)
                    counter += 1
            edit_note.user_notes = str(';0;'.join(new_note))
            sessions.commit()
            bot.send_message(message.chat.id, "Запись успешно добавлена ✅")

            keyboard2 = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard2.add("Удалить Запись 🗑")
            keyboard2.add("Изменить Запись ✏️")
            keyboard2.add("Вернуться ↩️")
            goToTheNote(message, num_note)
        else:
            keyboard_cancler = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard_cancler.add("Отменить")
            send = bot.send_message(message.chat.id, "Не верный формат ❌",
                                    reply_markup=keyboard_cancler)
            bot.register_next_step_handler(send, addAudio, name_note, num_note)


def deletePhoto(message, name_note, num_note):
    if message.text == "Отменить":
        bot.send_message(message.chat.id, "Операция отменена")
        keyboard2 = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard2.add("Удалить Запись 🗑")
        keyboard2.add("Изменить Запись ✏️")
        keyboard2.add("Вернуться ↩️")
        goToTheNote(message, num_note)
    else:
        try:
            sessions = db_session.create_session()
            all_notes = sessions.query(notes.Note).all()
            all_folders = sessions.query(folders.Folder).all()
            for i in all_folders:
                if i.in_folder == "now" and i.user_id == message.from_user.id:
                    you_folder_id = i.id
            edit_note = None
            for i in all_notes:
                if int(you_folder_id) == int(i.folder_id):
                    edit_note = i
            new_note = []
            counter = 0
            del_file_id = []
            for i in edit_note.user_notes.split(";0;"):
                if i.split(":")[0] != name_note:
                    if counter == int(num_note) - 1 and i != "":
                        temp = i.split("25:07:..04")
                        new_list = temp[1].split("_-_")
                        while "" in new_list:
                            new_list.remove("")
                        if len(message.text) == 1:
                            del_file_id.append(new_list[int(message.text) - 1])
                            new_list.remove(new_list[int(message.text) - 1])
                        else:
                            counter = 1
                            for i in message.text.split(", "):
                                mathhh = (int(i.split("-")[0]) - 1) * 10 + (int(i.split("-")[1])) - counter
                                del_file_id.append(new_list[mathhh])
                                new_list.remove(new_list[mathhh])
                                counter += 1
                        new_note.append("_-_".join(new_list))
                    else:
                        if i != "":
                            new_note.append((int(i.split("-")[0]) - 1) * 10 + (int(i.split("-")[1])))
                    counter += 1
            edit_note.user_notes = temp[0] + "25:07:..04_-_" + str(';0;'.join(new_note))
            sessions.commit()
            bot.send_message(message.chat.id, "Картинка успешно удалена ✅")

            #  Удаление фотки
            photos_for_del = []
            for i in del_file_id:
                photos_for_del.append(sessions.query(photos.Photos).filter(
                    photos.Photos.file_id == i).all())
            for i in photos_for_del:
                sessions.delete(i[0])
                sessions.commit()
            keyboard2 = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard2.add("Удалить Запись 🗑")
            keyboard2.add("Изменить Запись ✏️")
            keyboard2.add("Вернуться ↩️")
            goToTheNote(message, num_note)
        except Exception:
            if message.content_type == "audio":
                bot.delete_message(message.chat.id, message.message_id)
            keyboard_cancler = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard_cancler.add("Отменить")
            send = bot.send_message(message.chat.id, "Не верный формат ❌",
                                    reply_markup=keyboard_cancler)
            bot.register_next_step_handler(send, deleteAudio, name_note, num_note)


def addAudio(message, name_note, num_note):
    if message.text == "Отменить":
        bot.send_message(message.chat.id, "Операция отменена")
        keyboard2 = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard2.add("Удалить Запись 🗑")
        keyboard2.add("Изменить Запись ✏️")
        keyboard2.add("Вернуться ↩️")
        goToTheNote(message, num_note)
    else:
        if message.content_type == "audio":
            sessions = db_session.create_session()
            all_notes = sessions.query(notes.Note).all()
            all_folders = sessions.query(folders.Folder).all()
            all_music = sessions.query(music.Musics).all()
            musics = []
            for i in all_music:
                musics.append(i)
            if message.audio.file_id not in musics:
                mus = music.Musics(name=message.audio.performer + " - " + message.audio.title,
                                   file_id=message.audio.file_id)
                sessions.add(mus)
                sessions.commit()
            for i in all_folders:
                if i.in_folder == "now" and i.user_id == message.from_user.id:
                    you_folder_id = i.id
            edit_note = None
            for i in all_notes:
                if int(you_folder_id) == int(i.folder_id):
                    edit_note = i
            new_note = []
            counter = 0
            for i in edit_note.user_notes.split(";0;"):
                if i.split(":")[0] != name_note:
                    if counter == int(num_note) - 1:
                        temp = i.split("25:07:..04")
                        temp[1] = temp[1] + "_-_" + message.audio.file_id
                        new_note.append("25:07:..04".join(temp))
                    else:
                        new_note.append(i)
                    counter += 1
            edit_note.user_notes = str(';0;'.join(new_note))
            sessions.commit()
            bot.delete_message(message.chat.id, message.message_id)
            keyboard2 = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard2.add("Добавить Аудиозапись 🔊")
            keyboard2.add("Удалить Аудиозапись 🔇")
            keyboard2.add("Удалить Запись 🗑")
            keyboard2.add("Переименовать Запись ✏️")
            keyboard2.add("Вернуться ↩️")
            bot.send_message(message.chat.id, "Аудиозапись успешно добавлена ✅", reply_markup=keyboard2)

            keyboard2 = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard2.add("Удалить Запись 🗑")
            keyboard2.add("Изменить Запись ✏️")
            keyboard2.add("Вернуться ↩️")
            goToTheNote(message, num_note)
        else:
            keyboard_cancler = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard_cancler.add("Отменить")
            send = bot.send_message(message.chat.id, "Не верный формат ❌",
                                    reply_markup=keyboard_cancler)
            bot.register_next_step_handler(send, addAudio, name_note, num_note)


def deleteAudio(message, name_note, num_note):
    if message.text == "Отменить":
        bot.send_message(message.chat.id, "Операция отменена")
        keyboard2 = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard2.add("Удалить Запись 🗑")
        keyboard2.add("Изменить Запись ✏️")
        keyboard2.add("Вернуться ↩️")
        goToTheNote(message, num_note)
    else:
        try:
            sessions = db_session.create_session()
            all_notes = sessions.query(notes.Note).all()
            all_folders = sessions.query(folders.Folder).all()
            for i in all_folders:
                if i.in_folder == "now" and i.user_id == message.from_user.id:
                    you_folder_id = i.id
            edit_note = None
            for i in all_notes:
                if int(you_folder_id) == int(i.folder_id):
                    edit_note = i
            new_note = []
            counter = 0
            del_file_id = []
            for i in edit_note.user_notes.split(";0;"):
                if i.split(":")[0] != name_note:
                    if counter == int(num_note) - 1:
                        temp = i.split("25:07:..04")
                        new_list = temp[1].split("_-_")
                        while "" in new_list:
                            new_list.remove("")
                        if len(message.text) == 1:
                            del_file_id.append(new_list[int(message.text) - 1])
                            new_list.remove(new_list[int(message.text) - 1])
                        else:
                            counter = 1
                            for i in message.text.split(", "):
                                del_file_id.append(new_list[int(i) - counter])
                                new_list.remove(new_list[int(i) - counter])
                                counter += 1
                        new_note.append("_-_".join(new_list))
                    else:
                        new_note.append(i)
                    counter += 1
            edit_note.user_notes = temp[0] + "25:07:..04_-_" + str(';0;'.join(new_note))
            sessions.commit()

            #  Удаление музыки
            musics_for_del = []
            for i in del_file_id:
                musics_for_del.append(sessions.query(music.Musics).filter(
                    music.Musics.file_id == i).all())
            for i in musics_for_del:
                sessions.delete(i[0])
                sessions.commit()

            keyboard2 = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard2.add("Удалить Запись 🗑")
            keyboard2.add("Изменить Запись ✏️")
            keyboard2.add("Вернуться ↩️")
            goToTheNote(message, num_note)
        except Exception:
            if message.content_type == "audio":
                bot.delete_message(message.chat.id, message.message_id)
            keyboard_cancler = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard_cancler.add("Отменить")
            send = bot.send_message(message.chat.id, "Не верный формат ❌",
                                    reply_markup=keyboard_cancler)
            bot.register_next_step_handler(send, deleteAudio, name_note, num_note)


def editNoteTitle(message, name_note, num_note, type_note):
    if message.text == "Отменить":
        keyboard2 = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard2.add("Удалить Запись 🗑")
        keyboard2.add("Изменить Запись ✏️")
        keyboard2.add("Вернуться ↩️")
        goToTheNote(message, num_note)
    elif type(message.text) is not str:
        if message.content_type == "audio":
            bot.delete_message(message.chat.id, message.message_id)
        keyboard_cancler = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard_cancler.add("Отменить")
        send = bot.send_message(message.chat.id, "Не корректное название записи ❌\nВведите название записи", reply_markup=keyboard_cancler)
        bot.register_next_step_handler(send, editNoteTitle, name_note, num_note)
    else:
        new_title_note = message.text
        if type_note == "str":
            send = bot.send_message(message.chat.id, "Введите новое содержание заметки (0 - неизменять)")
            bot.register_next_step_handler(send, editNoteBody, name_note, num_note, new_title_note)
        else:
            sessions = db_session.create_session()
            all_notes = sessions.query(notes.Note).all()
            all_folders = sessions.query(folders.Folder).all()
            for i in all_folders:
                if i.in_folder == "now" and i.user_id == message.from_user.id:
                    you_folder_id = i.id
            edit_note = None
            for i in all_notes:
                if int(you_folder_id) == int(i.folder_id):
                    edit_note = i
            new_note = []
            counter = 0
            for i in edit_note.user_notes.split(";0;"):
                if i.split(":")[0] != name_note:
                    if counter == int(num_note) - 1:
                        temp = i.split("25:07:..04")
                        if str(new_title_note) != "0":
                            temp[0] = ";" + temp[0].split(";")[1] + ";" + new_title_note
                        new_note.append("25:07:..04".join(temp))
                    else:
                        new_note.append(i)
                    counter += 1
            edit_note.user_notes = str(';0;'.join(new_note))
            sessions.commit()
            bot.send_message(message.chat.id, "Заметка была переименована ✅")
            goToTheNote(message, num_note)


def editNoteBody(message, name_note, num_note, new_title_note):
    if message.text == "Отменить":
        keyboard2 = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard2.add("Удалить Запись 🗑")
        keyboard2.add("Изменить Запись ✏️")
        keyboard2.add("Вернуться ↩️")
        bot.send_message(message.chat.id, "Операция отменена", reply_markup=keyboard2)
        goToTheNote(message, num_note)
    elif type(message.text) is not str:
        if message.content_type == "audio":
            bot.delete_message(message.chat.id, message.message_id)
        keyboard_cancler = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard_cancler.add("Отменить")
        send = bot.send_message(message.chat.id, "Не корректное содержание записи ❌\nВведите содержание записи", reply_markup=keyboard_cancler)
        bot.register_next_step_handler(send, editNoteBody, name_note, num_note, new_title_note)
    else:
        sessions = db_session.create_session()
        all_notes = sessions.query(notes.Note).all()
        all_folders = sessions.query(folders.Folder).all()
        for i in all_folders:
            if i.in_folder == "now" and i.user_id == message.from_user.id:
                you_folder_id = i.id
        edit_note = None
        for i in all_notes:
            if int(you_folder_id) == int(i.folder_id):
                edit_note = i
        new_note = []
        counter = 0
        for i in edit_note.user_notes.split(";0;"):
            if i.split(":")[0] != name_note:
                if counter == int(num_note) - 1:
                    temp = i.split("25:07:..04")
                    if str(new_title_note) != "0":
                        temp[0] = new_title_note
                    if str(message.text) != "0":
                        temp[1] = message.text
                    new_note.append("25:07:..04".join(temp))
                else:
                    new_note.append(i)
                counter += 1
        edit_note.user_notes = str(';0;'.join(new_note))
        sessions.commit()
        keyboard2 = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard2.add("Удалить Запись 🗑")
        keyboard2.add("Изменить Запись ✏️")
        keyboard2.add("Вернуться ↩️")
        bot.send_message(message.chat.id, "Заметка была изменена ✅", reply_markup=keyboard2)
        goToTheNote(message, num_note)


def print_folder(message):
    sessions = db_session.create_session()
    all_notes = sessions.query(notes.Note).all()
    all_folders = sessions.query(folders.Folder).all()
    inline_kb = telebot.types.InlineKeyboardMarkup()
    note_block = None
    count_btn = 1
    keyboard_folder = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard_folder.add("Добавить Запись 📝")
    keyboard_folder.add("Переименовать Папку ✏️")
    keyboard_folder.add("Удалить Папку 🗑")
    keyboard_folder.add("Вернуться ⬅️")
    for i in all_folders:
        if i.in_folder == "now" and i.user_id == message.from_user.id or i.in_folder == "now" and i.user_id == message.chat.id:
            you_folder_id = i.id
    for i in all_notes:
        if int(i.folder_id) == int(you_folder_id):
            note_block = i
    for i in note_block.user_notes.split(";0;"):
          inline_kb.add(telebot.types.InlineKeyboardButton(i.split("25:07:..04")[0].split(';')[-1], callback_data='btn' + str(count_btn)))
          count_btn += 1
    for i in all_folders:
        if i.in_folder == "now" and i.user_id == message.chat.id:
            bot.send_message(message.chat.id, "Вы в папке", reply_markup=keyboard_folder)
            send = bot.send_message(message.chat.id, "*" + i.names_folders + "*", parse_mode="Markdown", reply_markup=inline_kb)
            bot.register_next_step_handler(send, NotesOperations)


def addTitleNote(message):
    if message.text == "Отменить":
        bot.send_message(message.chat.id, "Операция отменена")
        print_folder(message)
    else:
        if type(message.text) is str:
            keyboard_cancler = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard_cancler.add("Текстовая", "Музыкальная")
            keyboard_cancler.add("Альбомная", "Файловая")
            keyboard_cancler.add("Отменить")
            send = bot.send_message(message.chat.id, "Выберите тип записи", reply_markup=keyboard_cancler)
            bot.register_next_step_handler(send, choose_type, message.text)
        else:
            if message.content_type == "audio":
                bot.delete_message(message.chat.id, message.message_id)
            keyboard_cancler = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard_cancler.add("Отменить")
            send = bot.send_message(message.chat.id, "Не корректное название заметки ❌\nВведите название записи",
                                    reply_markup=keyboard_cancler)
            bot.register_next_step_handler(send, addTitleNote)


def addNote(message, title_note):
    if message.text == "Отменить":
        bot.send_message(message.chat.id, "Операция отменена")
        print_folder(message)
    else:
        if type(message.text) is str:
            note = message.text
            sessions = db_session.create_session()
            all_folders = sessions.query(
                folders.Folder).all()  # нужно проверять folder id с id папки в которыю перешёл пользователь, а я спать 23:00 всё таки!
            for i in all_folders:
                if i.in_folder == "now" and i.user_id == message.from_user.id:
                    you_folder_id = i.id
            all_notes = sessions.query(notes.Note).all()
            note_block = None
            for i in all_notes:
                if i.user_id == message.from_user.id and i.folder_id == you_folder_id:
                    note_block = i
            if ";-string-;" + str(title_note) not in note_block.user_notes.split("25:07:..04")\
                    and ";-music-;" + str(title_note) not in note_block.user_notes.split("25:07:..04")\
                    and ";-album-;" + str(title_note) not in note_block.user_notes.split("25:07:..04")\
                    and ";-docs-;" + str(title_note) not in note_block.user_notes.split("25:07:..04"):
                note_block.user_notes = note_block.user_notes + ";-string-;" + str(title_note) + "25:07:..04" + str(note) + ";0;"
                sessions.commit()
                bot.send_message(message.chat.id, "Запись успешно добавлена ✅")
                print_folder(message)
            else:
                bot.send_message(message.chat.id, "Данная запись уже существует в этой папке ❌")
                print_folder(message)
        else:
            if message.content_type == "audio":
                bot.delete_message(message.chat.id, message.message_id)
            keyboard_cancler = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard_cancler.add("Отменить")
            send = bot.send_message(message.chat.id, "Не корректное содержание заметки ❌\nВведите содержание записи",
                                    reply_markup=keyboard_cancler)
            bot.register_next_step_handler(send, addNote, title_note)


@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    sessions = db_session.create_session()
    all_folders = sessions.query(folders.Folder).all()
    for i in all_folders:
        if i.in_folder == "now" and i.user_id == call.from_user.id:
            if call.message.text == i.names_folders:
                goToTheNote(call.message, call.data.split("n")[1])
            else:
                bot.send_message(call.message.chat.id, "😡")
                print_folder(call.message)


#db_session.global_init("/home/tele/SmartNotes/db/database.db")
db_session.global_init("db/database.db")
bot.polling(True)
