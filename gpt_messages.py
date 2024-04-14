GENERATE_CHAPTERS_LIST = 'Напиши список разделов для {1} "{0}". Пиши только главные разделы, ' \
                         'без подразделов. Каждый раздел с новой строки, без цифр. Напиши хотя бы {2} разделов'
GENERATE_SUBCHAPTERS_LIST = 'Напиши список подразделов для раздела "{0}" {2} "{1}". Пиши только подразделы.' \
                         ' Каждый раздел с новой строки, без цифр'
GENERATE_CHAPTER = 'Напиши раздел "{0}" для {2} "{1}" в формате latex. ' \
                   'Представь, что работа уже написана.'  # Добавь одну или несколько картинок или графиков'
GENERATE_SUBCHAPTER = 'Напиши только подраздел "{0}" раздела "{1}" для {3} "{2}" в формате latex. ' \
                   'Представь, что работа уже написана.'  # Добавь одну или несколько картинок или графиков'
BIBLIOGRAPHY = "Список использованных источников"
ENTER_NAME = "Введите название работы:\n"
BIBLIOGRAPHY_PREFIX = '\\begin{thebibliography}{}\n' \
                      '\\bibitem{ref1}'
GENERATE_BIBLIOGRAPHY = 'Напиши список использованных источников для {1} "{0}" в формате latex.\n'
# 'Представь, что работа уже написана. Используй только русские и английские символы. Придумай имена авторов и названия' \
# 'источников.'
DOLLAR_QUESTION = 'Является ли символ $ в данном контексте обозначением формулы latex?\n{0}\n Ответь да или нет'
SECTIONS_QUESTION = "Есть ли в этом тексте список тем?\n{0}"
SECTIONS_LIST_QUESTION = "Выведи только список тем из этого текста. Выведи каждую тему с новой строки без лишних " \
                         "символов\n{0}"
ADD_SECTIONS = "Дан список глав {2}:\n{0}\nДобавь в него дополнительные главы:\n{1}\nВыведи итоговый" \
               "список глав"
