from __future__ import print_function
from sys import exit
import os

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.anchorlayout import AnchorLayout
#from kivy.uix.progressbar import ProgressBar
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from fwupd import FWUpd
from fwget import FWGet


class NineRiFt(App):
    def build(self):
        root_folder = getattr(self, 'user_data_dir')
        cache_folder = os.path.join(root_folder, 'cache')
        fwget = FWGet(cache_folder)
        fwupd = FWUpd()

        sm = ScreenManager()
        def switch_screen(scrn):
            sm.current = scrn
        flashscreen = Screen(name='Flash')
        downloadscreen = Screen(name='Download')


        seladdr_label = Label(text="Addr:", font_size='12sp', height='14sp',
         size_hint_y=1, size_hint_x=.08)
        seladdr_input = TextInput(multiline=False, text='',
        height='12sp', font_size='12sp', size_hint_x=.92, size_hint_y=1)
        seladdr_input.bind(on_text_validate=lambda x: fwupd.setaddr(seladdr_input.text))
        selfile_label = Label(text="FW file:", font_size='12sp', size_hint_x=1, height='12sp')
        ifaceselspin = Spinner(text='TCP', values=('TCP', 'Serial', 'BLE')
        , font_size='12sp',height='14sp', sync_height=True)
        ifaceselspin.bind(text=lambda x, y: fwupd.setiface(ifaceselspin.text))
        devselspin = Spinner(text='ESC', values=('BLE', 'ESC', 'BMS', 'ExtBMS'),
         sync_height=True, font_size='12sp', height='14sp')
        devselspin.bind(text=lambda x, y: fwupd.setdev(devselspin.text))
        # ble_button = Button(text="BLE", font_size='12sp', height='15sp',
        #  on_press=lambda x:fwupd.setdev('ble'))
        #
        # esc_button = Button(text="ESC", font_size='12sp', height='15sp',
        #  on_press=lambda x:fwupd.setdev('esc'))
        #
        # bms_button = Button(text="BMS", font_size='12sp', height='15sp',
        #  on_press=lambda x:fwupd.setdev('bms'))
        #
        # ebms_button = Button(text="EBMS", font_size='12sp', height='15sp',
        #  on_press=lambda x:fwupd.setdev('extbms'))
        selfile = FileChooserListView(path=cache_folder)
        flash_button = Button(text="Flash It!", font_size='12sp', height='14sp',
         on_press=lambda x: fwupd.Flash(selfile.selection[0]))

        switcherlayout = BoxLayout(orientation='horizontal', size_hint_y=.08)
        toplayout = GridLayout(rows=2, size_hint_y=.2)
        addrlayout = BoxLayout(orientation='horizontal', size_hint_y=.3)
        addrlayout.add_widget(seladdr_label)
        addrlayout.add_widget(seladdr_input)
        topbtnlayout = BoxLayout(orientation='horizontal', size_hint_y=.7)
        # topbtnlayout.add_widget(ble_button)
        # topbtnlayout.add_widget(esc_button)
        # topbtnlayout.add_widget(bms_button)
        # topbtnlayout.add_widget(ebms_button)
        topbtnlayout.add_widget(ifaceselspin)
        topbtnlayout.add_widget(devselspin)
        toplayout.add_widget(addrlayout)
        toplayout.add_widget(topbtnlayout)
        midlayout = BoxLayout(orientation='vertical', size_hint_y=.70)
        midlabelbox = AnchorLayout(anchor_y='top', size_hint_y=.1)
        midlabelbox.add_widget(selfile_label)
        midlayout.add_widget(midlabelbox)
        midlayout.add_widget(selfile)
        botlayout = BoxLayout(orientation='vertical', size_hint_y=.15)
        botlayout.add_widget(flash_button)
        #botlayout.add_widget(pb)

        flashlayout = GridLayout(cols=1, rows=3)
        flashlayout.add_widget(toplayout)
        flashlayout.add_widget(midlayout)
        flashlayout.add_widget(botlayout)

        downloadlayout = GridLayout(cols=1, rows=3)
        fwget.setRepo("https://files.scooterhacking.org/esx/fw/repo.json")
        download_button = Button(text="Download It!", font_size='12sp', height='14sp',
         on_press=lambda x: fwget.Gimme('BMS','136'))
        downloadlayout.add_widget(download_button)

        fwupd_screen_btn = Button(text="Flash", font_size='12sp', height='12sp',
         on_press=lambda x: switch_screen('Flash'))
        fwget_screen_btn = Button(text="Download", font_size='12sp', height='14sp',
         on_press=lambda x: switch_screen('Download'))

        switcherlayout.add_widget(fwupd_screen_btn)
        switcherlayout.add_widget(fwget_screen_btn)

        mainlayout = GridLayout(cols=1, rows=2)
        mainlayout.add_widget(switcherlayout)

        flashscreen.add_widget(flashlayout)
        downloadscreen.add_widget(downloadlayout)
        sm.add_widget(flashscreen)
        sm.add_widget(downloadscreen)

        mainlayout.add_widget(sm)
        return mainlayout

if __name__ == "__main__":
    NineRiFt().run()
