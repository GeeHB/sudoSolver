#!/usr/bin/python3
#
# coding=UTF-8

import pygame
import sys

# --- Couleurs ---
WHITE = (255, 255, 255)
GREY = (200, 200, 200)
LIGHT_GREY = (220, 220, 220)
BLACK = (0, 0, 0)

menu_height = 30

# --- Classes ---

class SubMenu:
    def __init__(self, items, x, y, width=120, height=30):
        self.items = items
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.visible = False

    def draw(self, surface):
        if self.visible:
            for i, item in enumerate(self.items):
                rect = pygame.Rect(self.x, self.y + i * self.height, self.width, self.height)
                pygame.draw.rect(surface, LIGHT_GREY, rect)
                text = font.render(item, True, BLACK)
                textRect = text.get_rect()
                textRect.bottom = rect.bottom - 2
                textRect.left = rect.left + 4
                surface.blit(text, textRect)

    def handle_event(self, event):
        if self.visible and event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            for i, item in enumerate(self.items):
                rect = pygame.Rect(self.x, self.y + i * self.height, self.width, self.height)
                if rect.collidepoint(mx, my):
                    return item
        return None


class MenuItem:
    def __init__(self, label, x, submenu_items):
        self.label = label
        self.rect = pygame.Rect(x, 0, 100, menu_height)
        self.submenu = SubMenu(submenu_items, x, menu_height)
        self.active = False

    def draw(self, surface):
        color = GREY if self.active else LIGHT_GREY
        pygame.draw.rect(surface, color, self.rect)
        text = font.render(self.label, True, BLACK)
        textRect = text.get_rect()
        textRect.bottom = self.rect.bottom - 2
        textRect.left = self.rect.left + 2
        surface.blit(text,textRect)
        self.submenu.draw(surface)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
                self.submenu.visible = self.active
                return None  # Menu clicked but not submenu
        return self.submenu.handle_event(event)


class MenuBar:
    def __init__(self):
        self.items = []
        self.active_item = None

    def add_menu(self, label, submenu_items):
        x = len(self.items) * 100
        item = MenuItem(label, x, submenu_items)
        self.items.append(item)

    def draw(self, surface):
        for item in self.items:
            item.draw(surface)

    def handle_event(self, event):
        for item in self.items:
            result = item.handle_event(event)
            if result:  # Une action a été cliquée
                self.deactivate_all()
                return result

            # Si un menu est activé, désactiver les autres
            if item.active:
                self.active_item = item
                for other in self.items:
                    if other != item:
                        other.active = False
                        other.submenu.visible = False
        return None

    def deactivate_all(self):
        for item in self.items:
            item.active = False
            item.submenu.visible = False
        self.active_item = None


# --- Actions définies ---
def handle_action(item):
    if item == "Quitter":
        pygame.quit()
        sys.exit()
    print(f"Action sélectionnée : {item}")

if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((800, 600), pygame.RESIZABLE)
    pygame.display.set_caption("Menu déroulant OO en Pygame")
    font = pygame.font.Font(None, 24)

    # --- Setup ---
    menu_bar = MenuBar()
    menu_bar.add_menu("Fichier", ["Nouveau", "Ouvrir", "Quitter"])
    menu_bar.add_menu("Édition", ["Copier", "Coller", "Supprimer"])
    menu_bar.add_menu("Aide", ["À propos", "Support"])

    # --- Boucle principale ---
    running = True
    while running:
        screen.fill(WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            action = menu_bar.handle_event(event)
            if action:
                handle_action(action)

        menu_bar.draw(screen)
        pygame.display.flip()

    pygame.quit()
