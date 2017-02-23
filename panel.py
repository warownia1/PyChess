import pygame


class Panel:

    def __init__(self, rect, surface=None):
        """
        Creates a new panel which represents interacjtive, printable surface.
        :param rect: boundary of the panel relative to its parent panel
        :type rect: pygame.Rect
        :param surface: surface where the graphics is drawn on
        :type surface: pygame.Surface
        """
        self.rect = rect
        if surface is None:
            surface = pygame.Surface((rect.width, rect.height))
        self.surface = surface
        self._child_components = []
    
    def add_component(self, panel):
        """
        Adds component to the panel.
        """
        self._child_components.append(panel)
    
    def paint_after(self, surface):
        """
        Method berforming painting before child components are pained on the
        panel.
        :param surface: current surface you can draw on
        :type surface: pygame.Surface
        """

    # consider using subsurfaces
    def paint(self, surface):
        """
        Method that should be overwritten in order to draw on top of the panel
        :param surface: current surface you can draw on
        :type surface: pygame.Surface
        """
    
    def repaint(self):
        """
        Call paint functions of the panel and all children components.
        Surfaces of each component is then blitted to the panel at their
        location.
        """
        self.paint(self.surface)
        for child in self._child_components:
            child.repaint()
            self.surface.blit(child.surface, child.rect)
        self.paint_after(self.surface)
    
    def clicked(self, x, y):
        """
        Function called when the click event occurs in the area of the panel.
        Executes all own click listeners and calls on click of child components
        if click occured in their boundary. Position is given relative to the
        top left corner of the panel. This method may be overwritten in derived
        classes given that it either call super().on_click() or doesn't need to
        propagate events further.
        """
        self.on_click(x, y)
        for panel in self._child_components:
            if panel.rect.collidepoint(x, y):
                panel.clicked(x - panel.rect.left, y - panel.rect.top)

    def on_click(self, x, y):
        """
        Function triggered when the mouse button is clicked in the boundary of
        the panel. Coordinates are given relative to the top left corner of the
        panel.
        :param x: x coordinate of the click
        :param y: y coordinate of the click
        """
