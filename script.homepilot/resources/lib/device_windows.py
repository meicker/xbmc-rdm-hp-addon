#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import time
import math
import xbmc
import xbmcgui
import xbmcaddon
import threading
import os
import xbmcaddon
__addon__ = xbmcaddon.Addon(id='script.homepilot')
__addon_path__        = __addon__.getAddonInfo('path').decode("utf-8")
_images = os.path.join(__addon_path__, 'resources', 'skins', 'Default', 'media', 'devices')
_control_images = os.path.join(__addon_path__, 'resources', 'skins', 'Default', 'media')

class BaseWindow(xbmcgui.WindowXMLDialog):

    BACKSPACE = 61448


    def add_error_control(self):
        label = unicode("<Probleme bei der Kommunikation \nmit dem HomePilot>", "utf-8")
        self.errorcontrol = xbmcgui.ControlLabel(280, 250, 350, 75, label, alignment=0x00000002)
        self.addControl(self.errorcontrol)

class MeterWindow(BaseWindow):

    def __init__( self, *args, **kwargs ):
        xbmcgui.WindowXMLDialog.__init__( self )
        client = kwargs["client"]
        did = kwargs["did"]
        self.parent_window = kwargs["parent"]
        try:
            self.meter = client.get_meter_by_id(did)
        except Exception, e:
            xbmc.log(str(e), level=xbmc.LOGWARNING)
            self.meter = None

    def onInit(self):
        controls = []
        if self.meter is not None:
            icon = self.meter.get_icon()
            icon_img = os.path.join(_images, icon)
            image_control = xbmcgui.ControlImage (260, 50, 40,40, icon_img)
            controls.append(image_control)
            title = self.meter.get_name()
            data = self.meter.get_data()
            title_control = xbmcgui.ControlLabel(310, 50, 600, 75, title, font="font16", textColor="white")
            controls.append(title_control)

            aktuell_control = xbmcgui.ControlLabel(300, 110, 600, 75, "Aktuelle Daten", font="font12", textColor="white")
            controls.append(aktuell_control)

            y = 150
            for data_dict in data:
                for d in data_dict:
                    label = d + ": " + data_dict[d]
                    data_control = xbmcgui.ControlLabel(300, y, 600, 75, label, font="font12", textColor="white")
                    y += 35
                    controls.append(data_control)
            self.addControls(controls)
        else:
            self.add_error_control()


    def onAction(self, action):
        xbmc.log("action window: " + str(action.getButtonCode()), level=xbmc.LOGNOTICE)
        if action == 92:
            xbmc.log(" ------- device window close ----", xbmc.LOGNOTICE)
            self.close()
        if action == 10:
            xbmc.log(" ------- device window close ----", xbmc.LOGNOTICE)
            self.parent_window.shutdown()
            xbmc.log("Stop thread", level=xbmc.LOGNOTICE)

            self.close()



sliderbarImg = os.path.join(_control_images, 'slider.png')
sliderNibImg = os.path.join(_control_images, 'osd_slider_nib.png')
sliderNibImgNF = os.path.join(_control_images, 'osd_slider_nibNF.png')
PERCENT_TYPE = "PERCENT"
DEGREE_TYPE = "DEGREE"


class SliderUpdater (threading.Thread):

    def __init__(self, client, device, type):
        threading.Thread.__init__(self)
        self.position = -1
        self.update_time = 0
        self.client = client
        self.device = device
        self.status = "NOTHING"
        self.type = type

    def update_slider (self, new_value):
        if self.position != new_value:
            #xbmc.log(str(self.position), xbmc.LOGNOTICE)
            #xbmc.log(str(new_value), xbmc.LOGNOTICE)
            self.update_time = time.time()
            self.position = new_value
            self.status = "UPDATE"

    def set_is_running (self, is_running):
        self.is_running = is_running

    def get_status(self):
        return self.status

    def run(self):
        self.is_running = 'True'
        while self.is_running:
            xbmc.log(" ------- device window running ----" + str(self.device.get_device_id()), xbmc.LOGNOTICE)
            #xbmc.log("-- update -- no status update awaiting", xbmc.LOGNOTICE)
            if self.update_time > 0 and time.time() - self.update_time > 0.4:
                if self.status == "UPDATE":
                    #xbmc.log("-- send move --" + str(self.position), xbmc.LOGNOTICE)
                    if self.type == PERCENT_TYPE:
                        self.client.move_to_position(self.device.get_device_id(), self.position)
                    else:
                        self.client.move_to_degree(self.device.get_device_id(), self.position)
                    self.status = "UPDATE_SENT"
            time.sleep(0.3)


class DeviceWindow(BaseWindow):

    def __init__( self, *args, **kwargs ):
        xbmcgui.WindowXMLDialog.__init__( self )
        self.x = 250
        self.y = 40

    def get_base_device_controls(self, device):
        control_dict = {}
        title = self.device.get_name()
        title_control = xbmcgui.ControlLabel(310, 50, 600, 75, title, font="font16", textColor="white")
        control_dict["title"] = title_control
        icon = self.device.get_icon()
        icon_img = os.path.join(_images, icon)
        image_control = xbmcgui.ControlImage ( self.x + 80, self.y + 60, 50, 50, icon_img)
        control_dict["icon"] = image_control
        #favoriten_radio_control = xbmcgui.ControlRadioButton(380, 250, 200, 50, "Favoriten")
        #control_dict["favoriten"] = favoriten_radio_control
        return control_dict

    def get_slider (self):
        if xbmc.skinHasImage ('settings/slider_back.png'):
            statusSlider = xbmcgui.ControlSlider(self.x + 80, self.y + 130, 280, 15, textureback = 'settings/slider_back.png', texture = 'settings/orb_nofo.png', texturefocus = 'settings/orb_fo.png')
            return statusSlider
        elif xbmc.skinHasImage ('slider.png'):
            statusSlider = xbmcgui.ControlSlider(self.x + 80, self.y + 130, 250, 20, textureback = 'slider.png', texture = 'osd_slider_nibNF.png', texturefocus = 'osd_slider_nib.png')
            return statusSlider
        else:
            statusSlider = xbmcgui.ControlSlider(self.x + 80, self.y + 130, 250, 20, textureback = sliderbarImg, texture = sliderNibImgNF, texturefocus = sliderNibImg)
            return statusSlider

class PercentageWindow(DeviceWindow):

    def __init__( self, *args, **kwargs ):
        DeviceWindow.__init__( self )
        self.client = kwargs["client"]
        self.device = kwargs["device"]
        self.parent_window = kwargs["parent"]
        self.updater = SliderUpdater(self.client, self.device, PERCENT_TYPE)
        self.updater.start()
        self.has_error = False

    def onInit(self):
        base_device_controls = self.get_base_device_controls(self.device)
        percent_controls = self.__get_percent_controls()
        self.controls = base_device_controls
        self.controls.update(percent_controls)
        button_group = self.getControl(114)
        button_group.setPosition(330,200)
        self.addControls([self.controls["slider"], self.controls["status"], self.controls["title"], self.controls["icon"]])
        slider = self.controls["slider"]
        slider.setPercent(self.device.get_position())
        self.__set_focus_and_navigation_handling()

    def __get_percent_controls (self):
        controls = {}
        x = self.x
        y = self.y
        status = self.device.get_display_value()
        status_control = xbmcgui.ControlLabel(self.x+ 180, self.y + 60, 600, 75, status, font="font16", textColor="white")
        controls["status"] = status_control
        slider = self.get_slider()
        controls["slider"] = slider
        slider.setPercent(self.device.get_position())
        down_button = self.getControl(112)
        up_button = self.getControl(113)
        controls["down"] = down_button
        controls["up"] = up_button
        return controls

    def update(self):
        if self.getFocusId() == 0:
            self.setFocus(self.controls["slider"])
        if self.updater.get_status() != "UPDATE":
            #xbmc.log("-- update -- no status update awaiting", xbmc.LOGNOTICE)
            try:
                new_device = self.client.get_device_by_id(self.device.get_device_id())
                if new_device.get_sync() != self.device.get_sync():#device has changed
                    self.__update_position(new_device)
                    self.__update_name(new_device)
                    self.device = new_device
            except Exception, e:
                xbmc.log(str(e), level=xbmc.LOGWARNING)
                self.has_error = True
        else:
            #xbmc.log("--update -- wait for status update", xbmc.LOGNOTICE)
            new_device = self.client.get_device_by_id(self.device.get_device_id())
            if new_device.get_sync() != self.device.get_sync():#device has changed
                self.__update_icon(new_device)
                self.__update_name(new_device)

        if self.has_error:
            self.add_error_control()


    def __update_icon(self, new_device):
        icon = self.controls["icon"]
        image = new_device.get_icon()
        icon_img = os.path.join(_images, image)
        icon.setImage(icon_img)

    def __update_position (self, new_device):
        self.__update_icon(new_device)
        if new_device.get_position() != self.device.get_position():
            statusSlider = self.controls["slider"]
            #xbmc.log("set slider to position: " + str(new_device.get_position()), xbmc.LOGNOTICE)
            statusSlider.setPercent(new_device.get_position())
            self.device = new_device
            statusLabel = self.controls["status"]
            statusLabel.setLabel(new_device.get_display_value())



    def __update_name(self, new_device):
        if new_device.get_name() != self.device.get_name():
            title_label = self.controls["title"]
            title_label.setLabel(new_device.get_name())


    def __set_focus_and_navigation_handling(self):
        statusSlider = self.controls["slider"]
        downButton = self.controls["down"]
        upButton = self.controls["up"]

        self.setFocus(statusSlider)
        statusSlider.controlDown(downButton)
        downButton.controlDown(upButton)
        downButton.controlRight(upButton)
        downButton.controlUp(statusSlider)
        downButton.controlLeft(statusSlider)
        upButton.controlUp(downButton)
        upButton.controlLeft(downButton)


    def onClick (self, controlId):
        statusSlider = self.controls["slider"]
        downButton = self.controls["down"]
        upButton = self.controls["up"]
        #favoriten_radio_control = self.controls["favoriten"]
        status = self.device.get_status()
        #handle up-down-buttons
        if self.device.get_devicegroup() == 4:#dimmer
            if controlId == downButton.getId():
                self.client.move_up(self.device.get_device_id())
            elif controlId == upButton.getId():
                self.client.move_down(self.device.get_device_id())
        elif self.device.get_devicegroup() == 2:#rollo
            if controlId == downButton.getId():
                 self.client.move_down(self.device.get_device_id())
            elif controlId == upButton.getId():
                 self.client.move_up(self.device.get_device_id())
        else:
            if controlId == downButton.getId():
                if status <= 95:
                    self.client.move_to_position(self.device.get_device_id(), status + 5)
            elif controlId == upButton.getId():
                if status >= 5:
                    self.client.move_to_position(self.device.get_device_id(), status - 5)
        #handle slider
        if controlId == statusSlider.getId():
            current_slider_value = statusSlider.getPercent()
            #xbmc.log("current slider:" + str(current_slider_value), xbmc.LOGNOTICE)
            #xbmc.log("current status:" + str(status), xbmc.LOGNOTICE)
            if current_slider_value > status:
                new_position = current_slider_value
                if self.device.get_devicegroup() == 2 and new_position > 99:#rollo
                    new_position = 99
                elif self.device.get_devicegroup() == 2 and new_position == 6:#rollo
                    new_position = 5
                self.updater.update_slider(new_position)
            elif current_slider_value < status:
                new_position = current_slider_value
                if self.device.get_devicegroup() == 2 and new_position < 1:#rollo
                    new_position = 1
                elif self.device.get_devicegroup() == 2 and new_position == 94:#rollo
                    new_position = 95
                self.updater.update_slider(new_position)


    def onAction(self, action):
        xbmc.log("action window: " + str(action.getButtonCode()), level=xbmc.LOGNOTICE)
        if action == 92:
            xbmc.log(" ------- device window close ----", xbmc.LOGNOTICE)
            self.updater.set_is_running = False
            self.close()
        if action == 10:
            self.updater.set_is_running = False
            xbmc.log(" ------- device window close ----", xbmc.LOGNOTICE)
            self.parent_window.shutdown()
            xbmc.log("Stop thread", level=xbmc.LOGNOTICE)

            self.close()



class SwitchWindow(DeviceWindow):

    def __init__( self, *args, **kwargs ):
        DeviceWindow.__init__( self )
        self.client = kwargs["client"]
        self.device = kwargs["device"]
        self.parent_window = kwargs["parent"]
        self.wait_for_response = False
        self.updater = SliderUpdater(self.client, self.device, DEGREE_TYPE)

    def onInit(self):
        base_device_controls = self.get_base_device_controls(self.device)
        switch_controls = self.__get_switch_controls()
        self.addControls(base_device_controls.values())
        self.controls = base_device_controls
        self.controls.update(switch_controls)

        self.__set_focus_and_navigation_handling()


    def __get_switch_controls(self):
        controls = {}
        group_control = self.getControl(118)
        group_control.setPosition(350, 100)

        radio = self.getControl(116)
        on = self.getControl(115)
        off = self.getControl(117)
        if self.device.get_position() > 50:
            radio.setSelected(True)
            on.setEnabled(True)
            off.setEnabled(False)
        else:
            radio.setSelected(False)
            on.setEnabled(False)
            off.setEnabled(True)
        controls["group"] = group_control
        controls["radio"] = radio
        controls["on"] = on
        controls["off"] = off
        return controls

    def update (self):
        if self.getFocusId() == 0:
            self.setFocusId(116)
        if not self.wait_for_response:
            new_device = self.client.get_device_by_id(self.device.get_device_id())
            if new_device.get_sync() != self.device.get_sync():
                if new_device.get_position() != self.device.get_position():
                    radio = self.getControl(116)
                    on = self.getControl(115)
                    off = self.getControl(117)
                    icon = self.controls["icon"]
                    if new_device.get_position() > 50:
                        radio.setSelected(True)
                        on.setEnabled(True)
                        off.setEnabled(False)
                    else:
                        radio.setSelected(False)
                        on.setEnabled(False)
                        off.setEnabled(True)
                    image = new_device.get_icon()
                    icon_img = os.path.join(_images, image)
                    icon.setImage(icon_img)
                if new_device.get_name() != self.device.get_name():
                    title_label = self.controls["title"]
                    title_label.setLabel(new_device.get_name())
                self.device = new_device


    def __set_focus_and_navigation_handling(self):
        button = self.controls["radio"]
        self.setFocus(button)

    def onClick (self, controlId):
        self.wait_for_response = True
        button = self.controls["radio"]
        xbmc.log("click -on: " + str(button.isSelected()), level=xbmc.LOGNOTICE)
        if controlId == button.getId():
            if button.isSelected():
                self.client.switch_on(self.device.get_device_id())
            else:
                self.client.switch_off(self.device.get_device_id())
        self.wait_for_response = False


    def onAction(self, action):
        xbmc.log("action window: " + str(action.getButtonCode()), level=xbmc.LOGNOTICE)
        if action == 92:
            xbmc.log(" ------- device window close ----", xbmc.LOGNOTICE)
            self.close()
        if action == 10:
            xbmc.log(" ------- device window close ----", xbmc.LOGNOTICE)
            self.parent_window.shutdown()
            xbmc.log("Stop thread", level=xbmc.LOGNOTICE)

            self.close()

class DegreeWindow(DeviceWindow):

    def __init__( self, *args, **kwargs ):
        DeviceWindow.__init__( self )
        self.client = kwargs["client"]
        self.device = kwargs["device"]
        self.parent_window = kwargs["parent"]
        self.updater = SliderUpdater(self.client, self.device, DEGREE_TYPE)
        self.updater.start()

    def onInit(self):
        base_device_controls = self.get_base_device_controls(self.device)
        degree_controls = self.__get_degree_controls()
        self.controls = base_device_controls
        self.controls.update(degree_controls)
        button_group = self.getControl(114)
        button_group.setPosition(330,200)
        self.addControls([self.controls["slider"], self.controls["status"], self.controls["title"], self.controls["icon"]])
        slider = self.controls["slider"]
        slider_position = self.__get_slider_percent_from_position(self.device)
        slider.setPercent(slider_position)
        self.__set_focus_and_navigation_handling()

    def __get_degree_controls (self):
        controls = {}
        x = self.x
        y = self.y
        status = self.device.get_display_value()
        status_control = xbmcgui.ControlLabel(self.x+ 180, self.y + 60, 600, 75, status, font="font16", textColor="white")
        controls["status"] = status_control
        controls["slider"] = self.get_slider()
        controls["down"] = self.getControl(112)
        controls["up"] = self.getControl(113)
        return controls

    def __get_slider_percent_from_position (self, device):
        position = device.get_position()
        return (float(position)/10 - 3) * 4


    def __set_focus_and_navigation_handling(self):
        statusSlider = self.controls["slider"]
        downButton = self.controls["down"]
        upButton = self.controls["up"]

        self.setFocus(statusSlider)
        statusSlider.controlDown(downButton)
        downButton.controlDown(upButton)
        downButton.controlRight(upButton)
        downButton.controlUp(statusSlider)
        downButton.controlLeft(statusSlider)
        upButton.controlUp(downButton)
        upButton.controlLeft(downButton)

    def update(self):
        if self.getFocusId() == 0:
            self.setFocus(self.controls["slider"])
        if self.updater.get_status() != "UPDATE":
            new_device = self.client.get_device_by_id(self.device.get_device_id())
            if new_device.get_sync() != self.device.get_sync():
                self.__update_position(new_device)
                self.__update_name(new_device)
                self.device = new_device
        else:
            new_device = self.client.get_device_by_id(self.device.get_device_id())
            if new_device.get_sync() != self.device.get_sync():
                self.__update_name(new_device)
                self.__update_icon(new_device)

    def __update_icon(self, new_device):
        icon = self.controls["icon"]
        image = new_device.get_icon()
        icon_img = os.path.join(_images, image)
        icon.setImage(icon_img)


    def __update_position(self, new_device):
        if new_device.get_position() != self.device.get_position():
            statusSlider = self.controls["slider"]
            new_position = self.__get_slider_percent_from_position(new_device)
            statusSlider.setPercent(new_position)
            self.device = new_device
            statusLabel = self.controls["status"]
            statusLabel.setLabel(new_device.get_display_value())
            self.__update_icon(new_device)

    def __update_name (self, new_device):
        if new_device.get_name() != self.device.get_name():
            title_label = self.controls["title"]
            title_label.setLabel(new_device.get_name())

    def onClick (self, controlId):
        statusSlider = self.controls["slider"]
        downButton = self.controls["down"]
        upButton = self.controls["up"]
        #favoriten_radio_control = self.controls["favoriten"]
        current_device_position = self.device.get_position()
        current_device_position_in_percent = self.__get_slider_percent_from_position(self.device)
        current_slider_position = statusSlider.getPercent()
        if controlId == downButton.getId():
            if current_slider_position >= 5:
                self.client.move_to_degree(self.device.get_device_id(), current_device_position - 5)
        elif controlId == upButton.getId():
            if current_slider_position <= 95:
                self.client.move_to_degree(self.device.get_device_id(), current_device_position + 5)
        elif controlId == statusSlider.getId():
            if current_slider_position != current_device_position_in_percent:
                diff = current_slider_position - current_device_position_in_percent
                # thermostats can only be shifted in 0.5 degree steps over a range from 3°-28°
                # this results in 50 possible value, as the slider has 100 possible values
                # this requires some mappings/hacks
                if diff == 1:
                    new_position = (float(current_slider_position + 1) * 5 + 60) / 2
                    if new_position % 5 == 0:
                        self.updater.update_slider(int(new_position))
                elif diff == -1:
                    new_position = (float(current_slider_position - 1) * 5 + 60) / 2
                    if new_position % 5 == 0:
                        self.updater.update_slider(int(new_position))
                else:
                    new_position = (float(current_slider_position) * 5 + 60) / 2
                    if new_position % 5 == 0:
                        self.updater.update_slider(int(new_position))


    def onAction(self, action):
        xbmc.log("action window: " + str(action.getButtonCode()), level=xbmc.LOGNOTICE)
        if action == 92:
            xbmc.log(" ------- device window close ----", xbmc.LOGNOTICE)
            self.updater.set_is_running = False
            self.close()
        if action == 10:
            self.updater.set_is_running = False
            xbmc.log(" ------- device window close ----", xbmc.LOGNOTICE)
            self.parent_window.shutdown()
            xbmc.log("Stop thread", level=xbmc.LOGNOTICE)

            self.close()
