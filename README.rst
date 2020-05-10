CatBot
======

CatBot - это бот для Telegram.

Installing
----------

создание вертуал окруж и актевируйте его, потом выполните:

.. code-block:: text

    pip install -r requirements.txt

Положите картинки с котивами в папку images. Название файлов должно начинаться с cat, а заканчиваться.jpg

Настройки
---------

Создайте файл settings.py и добавте след настройки:

.. code-block:: python

    API_KEY = 'API ключ'

    USER_EMOJI = [':smiley_cat:', ':smiling_imp:', ':panda_face:', ':dog:']

Запуск
------

В активированном верт окружении выполнить:

.. code-block:: text

    python3 bot.py
 