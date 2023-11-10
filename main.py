from screeninfo import get_monitors
import wx
from random import choice


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
        super(Mywin, self).__init__(parent, title=title, size=(300, 300))
        self.DIMENSION = (300, 300)

        image = wx.Image('hintergrund.jpg', wx.BITMAP_TYPE_ANY).Scale(self.DIMENSION[0], self.DIMENSION[1])
        bitmap = wx.Bitmap(image)
        self.bitmap = wx.StaticBitmap(self, -1, bitmap)
        self.bitmap.Bind(wx.EVT_MOTION, self.OnMove)

        self.btn = wx.Button(self.bitmap, -1, "Klick Mich", size=(70, 20))

        self.Centre()
        self.Show(True)

        self.btn.SetPosition((110, 110))

        self.coordinates = subtract_rectangle(get_screen_coordinates(), self.DIMENSION)
        # self.coordinates = create_map(self.coordinates)

    def OnMove(self, event):
        xmouse, ymouse = wx.GetMousePosition()
        x0, y0 = self.bitmap.ClientToScreen(0, 0)
        xmid, ymid = self.bitmap.ClientToScreen((self.DIMENSION[0] // 2), (self.DIMENSION[1] // 2))
        if abs((xmouse - xmid)) < 110 and abs((ymouse - ymid)) < 110:
            xoffset = xmid - xmouse
            yoffset = ymid - ymouse
            print(xoffset, yoffset)
            new_position = (xoffset, yoffset)
            steps = towards_zero(new_position, 1.5)
            for x_step, y_step in steps:
                new_position = (x0 + x_step, y0 + y_step)
                x0, y0 = new_position
                if (cheked := check_point(self.coordinates, new_position))[0]:
                    self.SetPosition(new_position)
                else:
                    new_position = (x0 + ((self.DIMENSION[0] + 3) * x_step if x_step != 0 else 0),
                                    y0 + ((self.DIMENSION[1] + 3) * y_step if y_step != 0 else 0))
                    if (cheked := check_point(self.coordinates, new_position))[0]:
                        self.SetPosition(new_position)
                    else:
                        self.SetPosition(cheked[1])



app = wx.App()
frm = Mywin(None, 'Window Moving')
app.MainLoop()
