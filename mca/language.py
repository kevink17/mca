from mca.config import config
import gettext
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
try:
    language = gettext.translation('messages', localedir=dir_path + '/locales',
                                   languages=[config.config.get('language')])
except FileNotFoundError:
    _ = gettext.gettext
else:
    language.install()
    _ = language.gettext

