import telebot
from data import db_session, folders, notes, users, music

TOKEN = "1363841624:AAEsC-fHePzz1dPaLAZS6ntWLky_wf9mg-I"
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
                and ";-music-;" + str(title_note) not in note_block.user_notes.split("25:07:..04"):
            note_block.user_notes = note_block.user_notes + ";-music-;" + str(title_note) + "25:07:..04;0;"
            sessions.commit()
            bot.send_message(message.chat.id, "Запись успешно добавлена ✅")
            print_folder(message)
        else:
            bot.send_message(message.chat.id, "Данная запись уже существует в этой папке ❌")
            print_folder(message)
    else:
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
            message.text == "Добавить Аудиозапись 🔊" or message.text == "Удалить Аудиозапись 🔇":
        pass
    else:
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
    if right_note is not None:
        keyboard2 = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        if right_note.split(";")[1] == "-music-":
            keyboard2.add("Добавить Аудиозапись 🔊")
            keyboard2.add("Удалить Аудиозапись 🔇")
        keyboard2.add("Удалить Запись 🗑")
        if right_note.split(";")[1] == "-music-":
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
                for i in new_l:
                    send = bot.send_audio(message.chat.id, audio=i)
            except Exception:
                pass
        else:
            send = bot.send_message(message.chat.id, "*" +
                                    right_note.split("25:07:..04")[0].split(";")[-1] + "*\n" +
                                    right_note.split("25:07:..04")[1], parse_mode="Markdown",
                                    reply_markup=keyboard2)
        bot.register_next_step_handler(send, inNote, right_note.split("25:07:..04")[0], num_note)
    else:
        keyboard_folder = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard_folder.add("Добавить Запись 📝")
        keyboard_folder.add("Переименовать Папку ✏️")
        keyboard_folder.add("Удалить Папку 🗑")
        keyboard_folder.add("Вернуться ⬅️")
        send = bot.send_message(message.chat.id, "Данной записи не существует",
                                reply_markup=keyboard_folder)
        bot.register_next_step_handler(send, NotesOperations)


def inNote(message, name_note, num_note):
    if message.text == "Вернуться ↩️":
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
        new_note = []
        for i in del_note.user_notes.split(";0;"):
            if i.split("25:07:..04")[0] != name_note:
                new_note.append(i)
        del_note.user_notes = str(';0;'.join(new_note))
        sessions.commit()
        bot.send_message(message.chat.id, "Запись удалена ✅")
        print_folder(message)
    elif message.text == "Изменить Запись ✏️":
        keyboard_cancler = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard_cancler.add("Отменить")
        send = bot.send_message(message.chat.id, "Введите новое название записи (0 - неизменять)", reply_markup=keyboard_cancler)
        bot.register_next_step_handler(send, editNoteTitle, name_note, num_note, "str")
    elif message.text == "Переименовать Запись ✏️":
        keyboard_cancler = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard_cancler.add("Отменить")
        send = bot.send_message(message.chat.id, "Введите новое название записи (0 - неизменять)",
                                reply_markup=keyboard_cancler)
        bot.register_next_step_handler(send, editNoteTitle, name_note, num_note, "other")
    elif message.text == "Добавить Аудиозапись 🔊":
        keyboard_cancler = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard_cancler.add("Отменить")
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
        bot.send_message(message.chat.id, "*" + name_note.split(";")[-1] + "*" + "\n" +
                         "\n".join(list_music),
                         parse_mode="Markdown")
        keyboard_cancler.add("Отменить")
        send = bot.send_message(message.chat.id, "Введите номера аудиозаписей, которые хотите удалить (1) (1, 2, 3)",
                                reply_markup=keyboard_cancler)
        bot.register_next_step_handler(send, deleteAudio, name_note, num_note)
    else:
        keyboard2 = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard2.add("Удалить Запись 🗑")
        keyboard2.add("Изменить Запись ✏️")
        keyboard2.add("Вернуться ↩️")
        bot.send_message(message.chat.id, "Вы что-то не то ввели",
                         reply_markup=keyboard2)
        goToTheNote(message, num_note)


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
            keyboard2 = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard2.add("Добавить Аудиозапись 🔊")
            keyboard2.add("Удалить Аудиозапись 🔇")
            keyboard2.add("Удалить Запись 🗑")
            keyboard2.add("Переименовать Запись ✏️")
            keyboard2.add("Вернуться ↩️")
            bot.send_message(message.chat.id, "Запись успешно добавлена ✅", reply_markup=keyboard2)

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
            for i in edit_note.user_notes.split(";0;"):
                if i.split(":")[0] != name_note:
                    if counter == int(num_note) - 1:
                        temp = i.split("25:07:..04")
                        new_list = temp[1].split("_-_")
                        while "" in new_list:
                            new_list.remove("")
                        if len(message.text) == 1:
                            new_list.remove(new_list[int(message.text) - 1])
                        else:
                            counter = 1
                            for i in message.text.split(", "):
                                new_list.remove(new_list[int(i) - counter])
                                counter += 1
                        new_note.append("_-_".join(new_list))
                    else:
                        new_note.append(i)
                    counter += 1
            edit_note.user_notes = temp[0] + "25:07:..04_-_" + str(';0;'.join(new_note))
            sessions.commit()
            keyboard2 = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard2.add("Удалить Запись 🗑")
            keyboard2.add("Изменить Запись ✏️")
            keyboard2.add("Вернуться ↩️")
            goToTheNote(message, num_note)

        except Exception:
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
                            temp[0] = ";-music-;" + new_title_note
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
            bot.send_message(message.chat.id, "Заметка была переименована ✅", reply_markup=keyboard2)
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
            keyboard_cancler.add("Отменить")
            send = bot.send_message(message.chat.id, "Выберите тип записи", reply_markup=keyboard_cancler)
            bot.register_next_step_handler(send, choose_type, message.text)
        else:
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
                    and ";-music-;" + str(title_note) not in note_block.user_notes.split("25:07:..04"):
                note_block.user_notes = note_block.user_notes + ";-string-;" + str(title_note) + "25:07:..04" + str(note) + ";0;"
                sessions.commit()
                bot.send_message(message.chat.id, "Запись успешно добавлена ✅")
                print_folder(message)
            else:
                bot.send_message(message.chat.id, "Данная запись уже существует в этой папке ❌")
                print_folder(message)
        else:
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


db_session.global_init("/home/tele/db/database.db")
#db_session.global_init("db/database.db")
bot.polling()
