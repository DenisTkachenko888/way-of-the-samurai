class Camera:
    def __init__(self, world_width=None, world_height=None):
        self.x = 0
        self.y = 0
        self.world_width = world_width
        self.world_height = world_height

    def apply(self, rect):
        """
        Shift a rect by the camera's (x,y) position.
        Use for all drawing, e.g.:
            screen.blit(sprite.image, camera.apply(sprite.rect))
        """
        return rect.move(-self.x, -self.y)

    def follow_center(self, target_rect, screen_w, screen_h, world_bounds=None):
        """
        Center the camera on the target_rect.
        If world_bounds or world size is set, clamps camera position so you can't scroll beyond the world edge.
        """
        cx = target_rect.centerx - screen_w // 2
        cy = target_rect.centery - screen_h // 2
        # Optionally clamp camera position
        if world_bounds:
            min_x, min_y, max_x, max_y = world_bounds
            cx = max(min_x, min(cx, max_x - screen_w))
            cy = max(min_y, min(cy, max_y - screen_h))
        elif self.world_width and self.world_height:
            cx = max(0, min(cx, self.world_width - screen_w))
            cy = max(0, min(cy, self.world_height - screen_h))
        else:
            cx = max(0, cx)
            cy = max(0, cy)
        self.x = cx
        self.y = cy
