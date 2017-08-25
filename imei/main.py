from functools import partial
from os import path

from kivy.app import App
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Rectangle
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.screenmanager import Screen, ScreenManager, FadeTransition
from kivy.network.urlrequest import UrlRequest
from jnius import autoclass, cast

s_m = ScreenManager(transition=FadeTransition())
logo_font = path.abspath(path.join(path.dirname(__file__), 'fonts', 'Pasajero.otf'))
ok_image = path.abspath(path.join(path.dirname(__file__), 'images', 'ok.png'))
failed_image = path.abspath(path.join(path.dirname(__file__), 'images', 'failed.png'))

__author__ = 'Amin Etesamian'
IMEI = None
Build = None


class MainScreen(Screen):
    def __init__(self):
        super(MainScreen, self).__init__()
        with self.canvas.before:
            Color(1, 1, 1, 0.1)
            self.rect = Rectangle(size=(Window.width, Window.height), pos=self.pos)
        self.url = 'http://api.unlockitservice.com/imei/{}'.format(IMEI)
        self.app_name = Label(
            text='IMEI Validator',
            font_name=logo_font,
            font_size=dp(42),
            pos_hint={'center_x': 0.5, 'center_y': 0.8}
        )
        self.info = Label(text='Press Start!', font_name=logo_font)
        self.kivy = Label(
            text='Powered by Kivy!',
            font_name=logo_font,
            font_size=dp(12),
            pos_hint={'center_x': 0.5, 'center_y': 0.75}
        )
        self.ok = Image(
            source=ok_image,
            size_hint=(None, None),
            size=(Window.width / 10, Window.height / 10),
            pos_hint={'center_x': 0.5, 'center_y': 0.6}
        )

        self.failed = Image(
            source=failed_image,
            size_hint=(None, None),
            size=(Window.width / 10, Window.height / 10),
            pos_hint={'center_x': 0.5, 'center_y': 0.6}
        )

        self.contact = Button(
            text='Contact Us!',
            font_name=logo_font,
            pos_hint={'center_x': 0.5, 'center_y': 0.1},
            size_hint=(None, None),
            size=(Window.width / 2.5, Window.height / 10),
            background_normal='',
            background_color=(0.3, 0.6, 0.8, 0.8),
            opacity=0.9
        )
        self.contact.bind(on_release=partial(self.contact_us))

        self.IMEI = Label(font_name=logo_font, font_size=dp(14), pos_hint={'center_x': 0.5, 'center_y': 0.45})
        self.device = Label(font_name=logo_font, font_size=dp(14), pos_hint={'center_x': 0.5, 'center_y': 0.40})
        self.brand = Label(font_name=logo_font, font_size=dp(14), pos_hint={'center_x': 0.5, 'center_y': 0.35})
        self.model = Label(font_name=logo_font, font_size=dp(14), pos_hint={'center_x': 0.5, 'center_y': 0.30})
        self.board = Label(font_name=logo_font, font_size=dp(14), pos_hint={'center_x': 0.5, 'center_y': 0.25})
        self.serial = Label(font_name=logo_font, font_size=dp(14), pos_hint={'center_x': 0.5, 'center_y': 0.20})

        self.add_widget(self.kivy)
        self.add_widget(self.info)
        self.add_widget(self.app_name)

        self.run = Button(
            text='Start',
            font_name=logo_font,
            pos_hint={'center_x': 0.5, 'center_y': 0.2},
            size_hint=(None, None),
            size=(Window.width / 2.5, Window.height / 10),
            background_normal='',
            background_color=(0, 0.9, 0.3, 0.8),
            opacity=0.9
        )
        self.run.bind(on_release=partial(self.on_button_press))
        self.add_widget(self.run)

    def on_button_press(self, *args):
        self.info.text = 'Please Wait ...'
        self.run.text = 'Processing...'
        self.run.background_color = (0.9, 0.0, 0.3, 0.8)
        UrlRequest(
            url=self.url,
            on_success=self.on_request_success,
            on_failure=self.on_request_failure,
            on_error=self.on_request_error
        )

    def on_request_success(self, req, result):
        self.remove_widget(self.run)
        self.add_widget(self.contact)

        if not result or isinstance(result, dict):
            self.add_widget(self.ok)
            self.info.text = "Yes! Your IMEI code is valid!"

            self.IMEI.text = 'IMEI : {}'.format(str(IMEI))
            self.device.text = 'Device: {}'.format(str(Build.DEVICE))
            self.model.text = 'Model: {}'.format(str(Build.MODEL))
            self.board.text = 'Board: {}'.format(str(Build.BOARD))
            self.serial.text = 'Serial: {}'.format(str(Build.SERIAL))
            self.brand.text = 'Brand: {}'.format(str(Build.BRAND))

            self.add_widget(self.IMEI)
            self.add_widget(self.device)
            self.add_widget(self.model)
            self.add_widget(self.board)
            self.add_widget(self.serial)
            self.add_widget(self.brand)

    def on_request_failure(self, req, result):
        self.remove_widget(self.run)
        self.add_widget(self.contact)

        if result == 'Invalid Imei':
            self.add_widget(self.failed)
            self.info.text = 'Ops! Your IMEI code is invalid!'

    def on_request_error(self, req, result):
        self.info.text = 'No Internet Connection!'
        self.run.text = 'Start'
        self.run.background_color = (0, 0.9, 0.3, 0.8)

    def contact_us(self, *args):
        PythonActivity = autoclass('org.renpy.android.PythonActivity')
        Intent = autoclass('android.content.Intent')
        Uri = autoclass('android.net.Uri')
        intent = Intent()
        intent.setAction(Intent.ACTION_VIEW)
        intent.setData(Uri.parse('https://t.me/eteamin'))
        currentActivity = cast('android.app.Activity', PythonActivity.mActivity)
        currentActivity.startActivity(intent)


class CommunityApp(App):
    def on_start(self):
        Service = autoclass('org.kivy.android.PythonActivity')
        Context = autoclass('android.content.Context')
        TelephonyManager = Service.getSystemService(Context.TELEPHONY_SERVICE)

        global Build
        Build = autoclass('android.os.Build')

        global IMEI
        IMEI = TelephonyManager.getDeviceId()
        s_m.add_widget(MainScreen())

    def on_pause(self):
        return True

    def on_stop(self):
        return True

    def on_resume(self):
        pass

    def build(self):
        activity = autoclass('org.kivy.android.PythonActivity').mActivity
        activity.removeLoadingScreen()
        return s_m


if __name__ == '__main__':
    CommunityApp().run()
