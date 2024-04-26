# Work in Progress Slicer for STL files for 3d-printing preparation

import time
import arcade
import numpy as np
import trimesh

# trimesh.util.attach_to_log()


res = 10
height = 1
maximums = []
minimums = []
positions = []
gcode = []

mesh = trimesh.load_mesh('accelor box v4.stl')
sliced_mesh = mesh.section((0, 0, 1), (0, 0, height))
file = open("mask.txt", "w")


def find_intersection(x1, y1, x2, y2, x3, y3, x4, y4):
    det = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if det == 0:
        return [None, None]

    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / det
    s = ((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / det

    if 1 >= t >= 0 >= s >= -1:
        intersection_x = x1 + t * (x2 - x1)
        intersection_y = y1 + t * (y2 - y1)
        return [intersection_x, intersection_y]
    else:
        return [None, None]


class GameWindow(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title, update_rate=1)

    def on_draw(self):
        global sliced_mesh
        global height
        global positions
        arcade.start_render()
        slicing()
        min_max()
        g_code_generation()
        filling()
        demo_render()
        sliced_mesh = mesh.section((0, 0, 1), (0, 0, height))

        if height >= 10:
            height = 1 / res
        else:
            height += 1 / res


def slicing():
    global positions
    positions = []

    for i in range(len(sliced_mesh.entities)):
        temp_positions = []
        for j in sliced_mesh.entities[i].points:
            x, y, z = sliced_mesh.vertices[j] * res
            temp_positions.append([x, y, z])
        positions.append(temp_positions)


def min_max():
    global maximums
    global minimums
    x = []
    y = []
    for i in positions:
        for j in i:
            x.append(j[0])
            y.append(j[1])
    maximums = [max(x), max(y)]
    minimums = [min(x), min(y)]


def slicing_2_notepad_boogalo():
    line = ""
    total = int(maximums[1]) - int(minimums[1])
    print(total)
    start = time.time()
    for j in range(int(minimums[1]), int(maximums[1])):
        print(int((j - minimums[1]) * 100 / total))

        for i in range(int(minimums[0]), int(maximums[0])):
            if any(np.array_equal([i, j, height * 2], (subarr * res)) for subarr in positions):

                line += "88"
            else:
                line += "__"
        line += "\n"
    print(str(int(time.time() - start)) + "s")
    file.write(line)


def filling():
    global positions
    global minimums
    global maximums
    intersections = []
    x = 2 * minimums[0]
    for entity in positions:
        entity.append(entity[0])
    while x < maximums[0]:
        x2 = x
        for entity in positions:
            for i in range(len(entity) - 1):
                intersect = find_intersection(entity[i][0], entity[i][1], entity[i + 1][0], entity[i + 1][1], x,
                                                     minimums[1], x2, maximums[1])
                #arcade.draw_line(500 + x, 500 + minimums[1], 500 + min(x2, maximums[0]), 500 + maximums[1], color=arcade.color.BLUE)
                if intersect != [None, None]:
                    intersections.append(intersect)
        intersections = sorted(intersections, key=lambda g: g[1])
        while len(intersections) > 0:
            print(intersections)
            gcode.append([intersections[0], intersections[1]])
            intersections.pop(1)
            intersections.pop(0)
        x += 10


def g_code_generation():
    global positions
    global sliced_mesh
    global gcode
    gcode = []
    for i in range(len(sliced_mesh.entities)):
        x = positions[i]
        x.append(x[0])
        for j in range(len(x) - 1):
            gcode.append([[x[j][0], x[j][1]], [x[j + 1][0], x[j + 1][1]]])


def demo_render():
    global gcode
    for i in gcode:
        arcade.draw_line(500 + i[0][0], 500 + i[0][1], 500 + i[1][0], 500 + i[1][1], line_width=5,
                         color=arcade.color.AIR_SUPERIORITY_BLUE)


if __name__ == "__main__":
    Window = GameWindow(1500, 800, "PRINTER")
    arcade.run()
    # slicing_2_electric_boogalo()
