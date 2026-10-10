# Этот файл публично доступен. Модифицируйте его под свои сообственные экраны.

##############################################################################
# Say
#
# Экран отображения ADV-диалога.
# http://www.renpy.org/doc/html/screen_special.html#say
screen say:
    window:
        id "window"

        has vbox:
            style "say_vbox"

        if who:
            text who id "who"

        text what id "what"

    # Если есть изображение, отобразить его над текстом.

    # Использовать быстрое меню.
    use quick_menu


##############################################################################
# Choice
#
# Экран для отображения внутриигровых меню.
# http://www.renpy.org/doc/html/screen_special.html#choice

screen choice:

    window:
        style "menu_window"
        xalign 0.5
        yalign 0.5

        vbox:
            style "menu"
            spacing 2

            for caption, action, chosen in items:

                if action:

                    button:
                        action action
                        style "menu_choice_button"

                        text caption style "menu_choice"

                else:
                    text caption style "menu_caption"

init -2 python:
    config.narrator_menu = True

    style.menu_window.set_parent(style.default)
    style.menu_choice.set_parent(style.button_text)
    style.menu_choice.clear()
    style.menu_choice_button.set_parent(style.button)
    style.menu_choice_button.xminimum = int(config.screen_width * 0.75)
    style.menu_choice_button.xmaximum = int(config.screen_width * 0.75)


##############################################################################
# Input
#
# Экран для отображения renpy.input()
# http://www.renpy.org/doc/html/screen_special.html#input

screen input:

    window style "input_window":
        has vbox

        text prompt style "input_prompt"
        input id "input" style "input_text"

    use quick_menu

##############################################################################
# Nvl
#
# Экран для NVL-диалога и меню.
# http://www.renpy.org/doc/html/screen_special.html#nvl

screen nvl:

    window:
        style "nvl_window"

        has vbox:
            style "nvl_vbox"

        # Отображать диалог.
        for who, what, who_id, what_id, window_id in dialogue:
            window:
                id window_id

                has hbox:
                    spacing 10

                if who is not None:
                    text who id who_id

                text what id what_id

        # Отображать меню, если есть.
        if items:

            vbox:
                id "menu"

                for caption, action, chosen in items:

                    if action:

                        button:
                            style "nvl_menu_choice_button"
                            action action

                            text caption style "nvl_menu_choice"

                    else:

                        text caption style "nvl_dialogue"

    add SideImage() xalign 0.0 yalign 1.0

    use quick_menu

##############################################################################
# Main Menu
#
# Экран для отображения главного меню при запуске Ren'Py.
# http://www.renpy.org/doc/html/screen_special.html#main-menu
init:
    $ renpy.music.register_channel("menu1", mixer='sfx', loop=False)
    $ renpy.music.register_channel("menu2", mixer='sfx', loop=False)
    $ renpy.music.register_channel("menu3", mixer='sfx', loop=False)
    $ renpy.music.register_channel("menu4", mixer='sfx', loop=False)
    $ lines = ImageDissolve('images/dissolves/lines.png', 0.15)



screen main_menu:

    # Это заменяет другие меню.
    tag menu

    imagemap:
        auto "images/gui/menu/menu_%s.jpg"
        hotspot (865,601,191,194) action Quit(confirm=True) 
        hotspot (738,66,489,262) action Start() hovered Play('menu1',"sound/sfx/menu_sfx.ogg",fadein=0.5)
        hotspot (489,382,249,321) action ShowMenu("load") hovered Play('menu2',"sound/sfx/menu_sfx.ogg",fadein=0.5)
        hotspot (1183,382,249,121) action ShowMenu("preferences") hovered Play('menu3',"sound/sfx/menu_sfx.ogg",fadein=0.5)
    

init -2 python:

    # Сделать все кнопки главного меню одноразмерными.
    style.mm_button.size_group = "mm"


##############################################################################
# Navigation
#
# Экран, включаемый в другие экраны для отображения навигации и фона.
# http://www.renpy.org/doc/html/screen_special.html#navigation
screen navigation:

    # Фон игрового меню.
    window:
        style "gm_root"

    # Кнопки.
    frame:
        style_group "gm_nav"
        xalign .98
        yalign .98

        has vbox

        textbutton _("Назад") action Return()
        textbutton _("Настройки") action ShowMenu("preferences")
        textbutton _("Сохранить игру") action ShowMenu("save")
        textbutton _("Загрузить игру") action ShowMenu("load")
        textbutton _("Главное меню") action MainMenu()
        textbutton _("Справка") action Help()
        textbutton _("Выход") action Quit()

init -2 python:
    style.gm_nav_button.size_group = "gm_nav"


##############################################################################
# Save, Load
#
# Экраны для сохранения и загрузки игры.
# http://www.renpy.org/doc/html/screen_special.html#save
# http://www.renpy.org/doc/html/screen_special.html#load

# Ибо сохранение и загрузка очень похожи, мы совмещаем их в один экран,
# file_picker. Потом мы используем его из экранов
# загрузки и сохранения.

screen file_picker:

    frame:
        style "file_picker_frame"

        has vbox

        # Кнопки сверху для выбора страницы.
        hbox:
            style_group "file_picker_nav"

            textbutton _("Пред"):
                action FilePagePrevious()

            textbutton _("Авто"):
                action FilePage("auto")

            textbutton _("Быстро"):
                action FilePage("quick")

            for i in range(1, 9):
                textbutton str(i):
                    action FilePage(i)

            textbutton _("След"):
                action FilePageNext()

        $ columns = 2
        $ rows = 5

        # Отобразить сетку файловых слотов.
        grid columns rows:
            transpose True
            xfill True
            style_group "file_picker"

            # Отобразить 10 слотов, с номерами от 1 до 10.
            for i in range(1, columns * rows + 1):

                # Каждый из них - кнопка.
                button:
                    action FileAction(i)
                    xfill True

                    has hbox

                    # Добавить скриншот.
                    add FileScreenshot(i)

                    $ file_name = FileSlotName(i, columns * rows)
                    $ file_time = FileTime(i, empty=_("Empty Slot."))
                    $ save_name = FileSaveName(i)

                    text "[file_name]. [file_time!t]\n[save_name!t]"

                    key "save_delete" action FileDelete(i)


screen save:

    # Это заменяет другие меню.
    tag menu

    use navigation
    use file_picker

screen load:

    # Это заменяет другие меню.
    tag menu

    use navigation
    use file_picker

init -2 python:
    style.file_picker_frame = Style(style.menu_frame)

    style.file_picker_nav_button = Style(style.small_button)
    style.file_picker_nav_button_text = Style(style.small_button_text)

    style.file_picker_button = Style(style.large_button)
    style.file_picker_text = Style(style.large_button_text)



##############################################################################
# Preferences
#
# Экран, позволяющий пользователю изменять настройки.
# http://www.renpy.org/doc/html/screen_special.html#prefereces

screen preferences:

    tag menu

    # Включить навигацию.
    use navigation

    # Разместить навигационные колонки в сетку шириной 3.
    grid 3 1:
        style_group "prefs"
        xfill True

        # Левая колонка.
        vbox:
            frame:
                style_group "pref"
                has vbox

                label _("Отображение")
                textbutton _("Окно") action Preference("display", "window")
                textbutton _("Полный экран") action Preference("display", "fullscreen")

            frame:
                style_group "pref"
                has vbox

                label _("Переходы")
                textbutton _("Все") action Preference("transitions", "all")
                textbutton _("Никаких") action Preference("transitions", "none")

            frame:
                style_group "pref"
                has vbox

                label _("Скорость текста")
                bar value Preference("text speed")

            frame:
                style_group "pref"
                has vbox

                textbutton _("Джойстик...") action Preference("joystick")


        vbox:
            frame:
                style_group "pref"
                has vbox

                label _("Пропуск")
                textbutton _("Прочтенных сообщений") action Preference("skip", "seen")
                textbutton _("Всех сообщений") action Preference("skip", "all")

            frame:
                style_group "pref"
                has vbox

                textbutton _("Начать пропуск") action Skip()

            frame:
                style_group "pref"
                has vbox

                label _("После выборов")
                textbutton _("Остановить пропуск") action Preference("after choices", "stop")
                textbutton _("Продолжить пропуск") action Preference("after choices", "skip")

            frame:
                style_group "pref"
                has vbox

                label _("Ускорить время")
                bar value Preference("auto-forward time")

                if config.has_voice:
                    textbutton _("Ждать голос") action Preference("wait for voice", "toggle")

        vbox:
            frame:
                style_group "pref"
                has vbox

                label _("Громкость музыки")
                bar value Preference("music volume")

            frame:
                style_group "pref"
                has vbox

                label _("Громкость звука")
                bar value Preference("sound volume")

                if config.sample_sound:
                    textbutton _("Тест"):
                        action Play("sound", config.sample_sound)
                        style "soundtest_button"

            if config.has_voice:
                frame:
                    style_group "pref"
                    has vbox

                    label _("Громкость голоса")
                    bar value Preference("voice volume")

                    textbutton _("Оставлять голос") action Preference("voice sustain", "toggle")
                    if config.sample_voice:
                        textbutton _("Тест"):
                            action Play("voice", config.sample_voice)
                            style "soundtest_button"

init -2 python:
    style.pref_frame.xfill = True
    style.pref_frame.xmargin = 5
    style.pref_frame.top_margin = 5

    style.pref_vbox.xfill = True

    style.pref_button.size_group = "pref"
    style.pref_button.xalign = 1.0

    style.pref_slider.xmaximum = 192
    style.pref_slider.xalign = 1.0

    style.soundtest_button.xalign = 1.0


##############################################################################
# Yes/No Prompt
#
# Экран, спрашивающий у пользователя вопрос да/нет.
# http://www.renpy.org/doc/html/screen_special.html#yesno-prompt
screen yesno_prompt:

    modal True

    imagemap:
        auto "images/gui/yes_no/%s.jpg"
        hotspot (517,689,303,193) action yes_action
        hotspot (1097,689,332,193) action no_action
        
    frame:
        xfill True
        #area(619,205,680,394)
        ypos 205
        yminimum 394
        text _(message)  font "fonts/burlak.ttf" size 50 xcenter 0.5

    key "game_menu" action no_action

init -2 python:
    style.yesno_button.size_group = "yesno"
    style.yesno_label_text.text_align = 0.5
    style.yesno_label_text.layout = "subtitle"
    burlak = "fonts/burlak.ttf"

##############################################################################
# Quick Menu
#
# Экран, входящий в экран save и дающий некоторые полезные функции
screen quick_menu:

    # Быстрое внутриигровое меню.
    hbox:
        style_group "quick"

        xalign 1.0
        yalign 1.0

        textbutton _("Назад") action Rollback()
        textbutton _("Сохранить") action ShowMenu('save')
        textbutton _("Б.Сохр") action QuickSave()
        textbutton _("Б.Загр") action QuickLoad()
        textbutton _("Пропуск") action Skip()
        textbutton _("Б.Пропуск") action Skip(fast=True, confirm=True)
        textbutton _("Авто") action Preference("auto-forward", "toggle")
        textbutton _("Настр") action ShowMenu('preferences')

init -2 python:
    style.quick_button.set_parent('default')
    style.quick_button.background = None
    style.quick_button.xpadding = 5

    style.quick_button_text.set_parent('default')
    style.quick_button_text.size = 12
    style.quick_button_text.idle_color = "#8888"
    style.quick_button_text.hover_color = "#ccc"
    style.quick_button_text.selected_idle_color = "#cc08"
    style.quick_button_text.selected_hover_color = "#cc0"
    style.quick_button_text.insensitive_color = "#4448"
    
    # layout.ARE_YOU_SURE - u"Вы уверены?."
    # layout.DELETE_SAVE - u"Вы действительно хотите удалить сохранение?"
    # layout.OVERWRITE_SAVE - u"Вы действительно хотите перезаписать это сохранение?"
    # layout.LOADING - u"При загрузке весь не сохраненный процесс будет утерян.nВы уверены?"
    # layout.QUIT - u"Вы действительно хотите выйти?"
    # layout.MAIN_MENU - u"Вы действительно хотите выйти в главное меню? Весь не сохраненный прогресс будет утерян."
    # layout.END_REPLAY - u"Вы действительно хотите закончить просмотр реплея?"
