from screeninfo import get_monitors
import wx
from random import choice
import win32gui
import win32con
import os
import subprocess
from pynput.keyboard import Key, Controller


def get_screen_coordinates():
    monitors = get_monitors()
    coordinates = []
    for m in monitors:
        # Die Koordinaten des Monitors werden als Bereich dargestellt
        x_range = range(m.x, m.x + m.width + 1)
        y_range = range(m.y, m.y + m.height + 1)
        coordinates.append((x_range, y_range))
    return coordinates


def subtract_rectangle(coordinates, rectangle):
    rx, ry = rectangle
    new_coordinates = []
    for xr, yr in coordinates:
        if not (xr.stop - rx) < xr.start or (yr.stop - ry) < yr.start:
            new_coordinates.append((range(xr.start, xr.stop - rx), range(yr.start, yr.stop - ry)))
    return new_coordinates


def check_point(coordinates, point):
    x, y = point
    for xr, yr in coordinates:  # gets tuple with range for x,y
        if x in xr and y in yr:
            return True, (x, y)
    closest_points = [(min(max(x, xr.start), xr.stop), min(max(y, yr.start), yr.stop)) for xr, yr in coordinates]
    distances = [abs(x - xp) + abs(y - yp) for xp, yp in closest_points]
    return False, closest_points[distances.index(min(distances))]


# def towards_zero(xy_goal: tuple[int, int]):
#     x, y = xy_goal
#     # Bestimmen Sie die Schrittrichtung basierend auf den Vorzeichen von x und y
#     x_step = -1 if x > 0 else 1 if x < 0 else 0
#     x_step_neg = x_step * -1
#     y_step = -1 if y > 0 else 1 if y < 0 else 0
#     y_step_neg = y_step * -1
#
#     result = []
#     while x != 0 or y != 0:
#         result.append((x_step_neg if x != 0 else 0, y_step_neg if y != 0 else 0))
#         x += x_step if x != 0 else 0
#         y += y_step if y != 0 else 0
#     return result


def create_map(ranges):
    print(ranges)
    points = set()
    for xr, yr in ranges:
        for x in xr:
            for y in yr:
                points.add((x, y))
    return points


def search_map(coord_map, point):
    if point in coord_map:
        return True, point
    else:
        # Berechnen Sie die Distanz zu allen Punkten und finden Sie den nächsten
        closest_point = min(coord_map, key=lambda x: (x[0]-point[0])**2 + (x[1]-point[1])**2)
        return False, closest_point


def towards_zero(xy: tuple[int, int], step_multiplicator: float = 1, zero_random: bool = True) -> list[tuple[int, int]]:
    x, y = xy
    length = max(abs(x), abs(y))
    x_step = -1 if x > 0 else 1 if x < 0 else 0
    x_step = choice([1, -1]) if x_step == 0 and zero_random else x_step
    x_step *= step_multiplicator
    y_step = -1 if y > 0 else 1 if y < 0 else 0
    y_step = choice([1, -1]) if y_step == 0 and zero_random else y_step
    y_step *= step_multiplicator
    x_multiplier = abs(x) / length
    x_multiplier *= step_multiplicator
    y_multiplier = abs(y) / length
    y_multiplier *= step_multiplicator
    result = []
    x_sum, y_sum = 0, 0
    for _ in range(length):
        x_sum += x_multiplier
        y_sum += y_multiplier
        result.append((int(round(x_sum) * x_step * -1), int(round(y_sum) * y_step * -1)))
        x_sum -= round(x_sum)
        y_sum -= round(y_sum)
    return result


class Mywin(wx.Frame):
    def __init__(self, parent, title):
        super(Mywin, self).__init__(parent, title=title, size=(300, 300), style=wx.BORDER_NONE)
        self.DIMENSION = (300, 300)
        self.clicked = False
        print(os.getcwd())
        image = wx.Image('hintergrund.jpg', wx.BITMAP_TYPE_ANY).Scale(self.DIMENSION[0], self.DIMENSION[1])
        bitmap = wx.Bitmap(image)
        self.bitmap = wx.StaticBitmap(self, -1, bitmap)
        self.bitmap.Bind(wx.EVT_MOTION, self.OnMove)

        self.btn = wx.Button(self.bitmap, -1, "Klick Mich", size=(70, 20))
        self.btn.Bind(wx.EVT_BUTTON, self.OnClick)

        self.Centre()
        self.Show(True)

        self.btn.SetPosition((115, 135))

        self.coordinates = subtract_rectangle(get_screen_coordinates(), self.DIMENSION)

        self.Iconize(False)
        self.Raise()

        hwnd = win32gui.FindWindow(None, 'Window Moving')
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 1000, 400, 300, 300, 0)


    def OnMove(self, event):
        if not self.clicked:
            xmouse, ymouse = wx.GetMousePosition()
            x0, y0 = self.bitmap.ClientToScreen(0, 0)
            xmid, ymid = self.bitmap.ClientToScreen((self.DIMENSION[0] // 2), (self.DIMENSION[1] // 2))
            if abs((xmouse - xmid)) < 85 and abs((ymouse - ymid)) < 80:
                keyboard.press(Key.media_volume_up)
                keyboard.release(Key.media_volume_up)
                subprocess.Popen("python soundplayer.py", creationflags=subprocess.CREATE_NO_WINDOW)
                xoffset = xmid - xmouse
                yoffset = ymid - ymouse
                new_position = (xoffset, yoffset)
                steps = towards_zero(new_position, 1.5)
                for x_step, y_step in steps:
                    self.SetFocus()
                    new_position = (x0 + x_step, y0 + y_step)
                    x0, y0 = new_position
                    if check_point(self.coordinates, new_position)[0]:
                        self.SetPosition(new_position)
                    else:
                        new_position = (x0 + ((self.DIMENSION[0] + 3) * x_step if x_step != 0 else 0),
                                        y0 + ((self.DIMENSION[1] + 3) * y_step if y_step != 0 else 0))
                        if (cheked := check_point(self.coordinates, new_position))[0]:
                            self.SetPosition(new_position)
                        else:
                            self.SetPosition(cheked[1])
                    self.bitmap.Refresh()
                    self.Update()
                    self.Refresh()
        else:
            self.clicked = False
            points = []
            for _ in range(3001):
                choosen_point_x = choice(choice(self.coordinates)[0])
                choosen_point_y = choice(choice(self.coordinates)[1])
                points.append((choosen_point_x, choosen_point_y))
            for i, point in enumerate(points):
                self.SetFocus()
                self.SetPosition(point)
                self.bitmap.Refresh()
                self.Update()
                self.Refresh()
                if i % 40 == 0:
                    keyboard.press(Key.media_volume_up)
                    keyboard.release(Key.media_volume_up)
                    subprocess.Popen("python soundplayer.py", creationflags=subprocess.CREATE_NO_WINDOW)
                wx.MilliSleep(20)

    def OnClick(self, event):
        self.clicked = True


keyboard = Controller()
app = wx.App()
frm = Mywin(None, 'Window Moving')
app.MainLoop()
