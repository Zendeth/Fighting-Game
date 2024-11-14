import pygame

# Character dimensions and properties
FRAME_WIDTH = 48
FRAME_HEIGHT = 48
SCALED_WIDTH = FRAME_WIDTH * 2
SCALED_HEIGHT = FRAME_HEIGHT * 2
HITBOX_WIDTH = 30
HITBOX_HEIGHT = 20
GRAVITY = 1
PARRY_DURATION = 0.5  # Parry duration in seconds
PARRY_COOLDOWN = 2  # Parry cooldown in seconds

# Animation settings
ANIMATION_SPEED = 0.2  # Controls speed of animation

# Player class with animations
class Player:
    def __init__(self, x, y, screen, controls, character_hitboxes, character_animations, character = "Biker"):
        self.x = x
        self.y = y
        self.width = character_hitboxes[character]["idle"].width
        self.height = character_hitboxes[character]["idle"].height
        self.health = 100
        self.controls = controls
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = True
        self.facing_right = True
        self.attacking = False
        self.attack_timer = 0
        self.hitbox = pygame.Rect(0, 0, HITBOX_WIDTH, HITBOX_HEIGHT)
        self.character_hitboxes = character_hitboxes
        self.character_animations = character_animations
        self.ground = screen.get_size()[1] - SCALED_HEIGHT
        self.screen = screen

        # Animation states
        self.current_frame = 0
        self.animation_speed = ANIMATION_SPEED
        self.action = "idle"

        # Parry states
        self.parrying = False
        self.parry_timer = 0

        self.character = character  # Default character

        self.parry_cool_down = 0

    def move(self, other_player, dt):
        # Apply horizontal movement
        keys = pygame.key.get_pressed()
        if keys[self.controls["left"]]:
            self.vel_x = -5
            self.facing_right = False
            self.action = "run"
        elif keys[self.controls["right"]]:
            self.vel_x = 5
            self.facing_right = True
            self.action = "run"
        else:
            self.vel_x = 0
            if self.on_ground and not self.attacking:
                self.action = "idle"

        # Jump
        if keys[self.controls["jump"]] and self.on_ground:
            self.vel_y = -15
            self.on_ground = False
            self.action = "jump"

        # Apply gravity
        self.vel_y += GRAVITY

        # Update position
        self.x += self.vel_x
        self.y += self.vel_y

        # Collision with ground
        if self.y >= self.ground:
            self.y = self.ground
            self.vel_y = 0
            self.on_ground = True
            if self.action == "jump":
                self.action = "idle"

        # Keep player within screen boundaries
        self.x = max(0, min(self.x, self.screen.get_size()[0] - self.width))

        # Collision with the other player
        self.handle_collision(other_player)

        # Update attack hitbox position based on direction
        if self.attacking:
            if self.facing_right:
                self.hitbox.x = self.x + self.width
            else:
                self.hitbox.x = self.x - self.hitbox.width
            self.hitbox.y = self.y + self.height // 2 - 10
            self.attack_timer -= 1
            if self.attack_timer <= 0:
                self.attacking = False  # Reset attack

        # Update animation frame
        self.current_frame += self.animation_speed
        if self.action == "run" and self.current_frame >= len(self.character_animations[self.character]["run"]):
            self.current_frame = 0
        elif self.action == "jump" and self.current_frame >= len(self.character_animations[self.character]["jump"]):
            self.current_frame = 0
        elif self.action == "attack" and self.current_frame >= len(self.character_animations[self.character]["attack1"]):
            self.current_frame = 0
        elif self.action == "hurt" and self.current_frame >= len(self.character_animations[self.character]["hurt"]):
            self.current_frame = 0

    def handle_collision(self, other_player):
        if (
            self.x < other_player.x + other_player.width
            and self.x + self.width > other_player.x
            and self.y < other_player.y + other_player.height
            and self.y + self.height > other_player.y
        ):
            # Horizontal collision
            if self.vel_x > 0:  # Moving right
                self.x = other_player.x - self.width
            elif self.vel_x < 0:  # Moving left
                self.x = other_player.x + other_player.width

    def create_outline(self, image, color=(255, 255, 255)):
        mask = pygame.mask.from_surface(image)
        outline = mask.outline()
        outline_image = pygame.Surface((image.get_width(), image.get_height()), pygame.SRCALPHA)
        for point in outline:
            outline_image.set_at(point, color)
        return outline_image

    def draw(self):
        # Choose the correct animation frame
        if self.action == "run":
            frame = self.character_animations[self.character]["run"][int(self.current_frame) % len(self.character_animations[self.character]["run"])]
        elif self.action == "jump":
            frame = self.character_animations[self.character]["jump"][int(self.current_frame) % len(self.character_animations[self.character]["jump"])]
        elif self.action == "attack":
            frame = self.character_animations[self.character]["attack1"][int(self.current_frame) * 2 % len(self.character_animations[self.character]["attack1"]) ]
        elif self.action == "hurt":
            frame = self.character_animations[self.character]["hurt"][int(self.current_frame) // 2 % len(self.character_animations[self.character]["hurt"])]
        else:
            frame = self.character_animations[self.character]["idle"][int(self.current_frame) % len(self.character_animations[self.character]["idle"])]

        # Flip frame based on direction
        if not self.facing_right:
            frame = pygame.transform.flip(frame, True, False)

        # Draw the frame on screen
        self.screen.blit(frame, (self.x, self.y))

        if self.parrying:
            # Add white outline to the frame
            outline_frame = self.create_outline(frame)
            self.screen.blit(outline_frame, (self.x, self.y))

        # Draw health bar
        pygame.draw.rect(self.screen, (255, 0, 0), (self.x, self.y - 10, self.width, 5))
        pygame.draw.rect(self.screen, (0, 0, 255), (self.x, self.y - 10, self.width * (self.health / 100), 5))

        # Draw attack hitbox if attacking
        # if self.attacking:
        #     pygame.draw.rect(screen, GREEN, self.hitbox)

    def attack(self, other_player):
        if not self.attacking:  # Only start an attack if not already attacking
            self.attacking = True
            self.attack_timer = len(self.character_animations[self.character]["attack1"]) / ANIMATION_SPEED // 2
            self.action = "attack"
            self.current_frame = 0  # Reset animation frame

            # Check if the hitbox overlaps with the other player
            if self.hitbox.colliderect(other_player.get_rect()):
                if not other_player.parrying:
                    other_player.action = "hurt"
                    other_player.health -= 10  # Decrease health on hit

    def update(self, dt):
        # Check for parry input
        keys = pygame.key.get_pressed()
        if keys[self.controls["parry"]] and self.parry_cool_down <= 0 and not self.parrying:
                self.start_parry()

        # Update parry state
        if self.parrying:
            self.parry_timer += dt
            if self.parry_timer >= PARRY_DURATION:
                self.end_parry()

    def start_parry(self):
        self.parrying = True
        self.parry_timer = 0
        self.parry_cool_down = PARRY_COOLDOWN


    def end_parry(self):
        self.parry_cool_down = PARRY_COOLDOWN
        self.parrying = False

    def get_rect(self):
        # Return the player's rectangle (for collision detection)
        return pygame.Rect(self.x, self.y, self.width, self.height)
