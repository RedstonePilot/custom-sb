import pygame
import random
import math
import os
from prettytable import PrettyTable
pygame.init()
font = pygame.font.Font(None, 25)


class Bot:
    def __init__(self):
        self.planes = []
        self.landing_order = []
        self.s_width, self.s_height = 800, 800
        self.screen = pygame.display.set_mode((self.s_width, self.s_height))
        self.runway_pos = (0, self.s_height//2)

    def draw(self):
        self.screen.fill((0, 0, 0))
        pygame.draw.circle(self.screen, (255, 255, 255), self.runway_pos, 5)
        pygame.draw.line(self.screen, (255, 255, 255),
                         self.runway_pos, (self.s_width, self.s_height//2), 1)
        for i in range(2, self.s_width, 100):  # 50 pixels = 1 nm
            pygame.draw.line(self.screen, (255, 255, 255), (i,
                             self.s_height // 2 - 10), (i, self.s_height // 2 + 10), 1)

        pygame.draw.line(self.screen, (255, 255, 255),
                         (550, 0), (550, self.s_height), 1)
        self.update_landing_order()
        self.vector()
        for plane in self.planes:
            plane.move()
            pygame.draw.circle(self.screen, (255, 0, 0), (plane.x, plane.y), 5)

            id_surface = font.render(str(plane.cs), True, (255, 255, 255))
            self.screen.blit(id_surface, (plane.x, plane.y - 20))

        self.display_landing_order()
        os.system("cls" if os.name == "nt" else "clear")
        table = PrettyTable(["Plane", "NM to TD", "State"])
        table.clear_rows()
        for plane in self.landing_order:
            dist = round(self.get_distance_to_td(plane)/50, 2)
            if plane.ils:
                state = "ILS"
            elif plane.base:
                state = "Base"
            else:
                state = int(plane.h)
            table.add_row([plane.cs, dist, state])
        print(str(table), end="")

        pygame.display.update()

    def update_landing_order(self):
        for plane in self.planes:
            if plane not in self.landing_order:
                new_dist = self.get_distance_to_td(plane)
                for i in range(len(self.landing_order) - 1):
                    plane1_distance = self.get_distance_to_td(
                        self.landing_order[i])
                    plane2_distance = self.get_distance_to_td(
                        self.landing_order[i + 1])

                    if plane2_distance - plane1_distance > 8 * 50:  # 8 nm gap
                        if plane1_distance < new_dist < plane2_distance:
                            self.landing_order.insert(i + 1, plane)
                            return True
                else:  # at the back lol
                    self.landing_order.append(plane)
                    return False

    def draw_dist(self, plane_a, plane_b):
        pygame.draw.line(self.screen, (0, 200, 200),
                         (plane_a.x, plane_a.y), (plane_b.x, plane_b.y), 1)

    def display_landing_order(self):
        for i, p in enumerate(self.landing_order):
            if i != 0:
                self.draw_dist(self.landing_order[i-1], p)

    def get_distance_to_td(self, plane):

        if plane.base and not plane.ils:
            return (abs(self.runway_pos[1] - plane.y) + 550)
        if plane.ils:
            return plane.x

        rad = math.radians(plane.h - 90)
        dx = 550 - plane.x
        dy = dx * math.tan(rad)
        turn_y = plane.y + dy

        dx = 550 - plane.x
        dy = turn_y - plane.y
        distance_to_base = (dx**2 + dy**2) ** 0.5

        distance_on_base = abs(self.runway_pos[1] - turn_y)

        distance_down_ILS = 550

        return distance_to_base + distance_on_base + distance_down_ILS

    def find_itx_heading(self, plane):

        order = self.landing_order.index(plane)
        if self.landing_order[order-1].ils:
            print("Plane on the ILS, maintaining heading")
            return plane.h
        preceeding_dist = self.get_distance_to_td(self.landing_order[order-1])
        current_distance = self.get_distance_to_td(plane)
        diff = 5*50 - (current_distance - preceeding_dist)

        rad = math.radians(plane.h - 90)
        dx = 550 - plane.x
        dy = dx * math.tan(rad)
        planned_itx = plane.y + dy
        if plane.y < self.runway_pos[1]:
            diff = - diff

        itx_point = planned_itx + diff

        dx = 500 - plane.x
        dy = itx_point - plane.y
        heading = (math.degrees(math.atan2(dy, dx)) + 90) % 360

        return heading

    def vector(self):
        for i, plane in enumerate(self.landing_order):
            if i != 0:
                plane.h = self.find_itx_heading(plane)

    def test_planes(self, mx, my):
        id = len(self.planes) + 1
        plane = Plane(id, mx, my)

        total_distance = self.get_distance_to_td(plane)
        print(f"Total distance: {total_distance/50} nm")  # 1 nm is 50px
        plane.d = total_distance

        self.planes.append(plane)


class Plane:
    def __init__(self, cs, x, y, d=-1):
        self.cs = cs
        self.x = x
        self.y = y
        self.d = d
        self.h = 90 if x < 550 else 270
        self.s = 180
        self.base = False
        self.ils = False
        self.landed = False

    def move(self):
        if 548 < self.x < 552:
            self.base = True
            if 398 < self.y < 402:
                self.h = 270
                self.ils = True
            else:
                self.h = 180 if self.y < 400 else 0

        if self.x < 2 and 398 < self.y < 402:
            self.landed = True
        rad = math.radians(self.h - 90)
        dx = (self.s/50 / 20) * math.cos(rad)
        dy = (self.s/50 / 20) * math.sin(rad)
        self.x += dx
        self.y += dy


if __name__ == "__main__":
    bot = Bot()
    running = True
    while running:
        bot.draw()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                bot.test_planes(mx, my)

    pygame.quit()
