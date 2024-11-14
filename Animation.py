import pygame
import os


def load_trimmed_frames(sheet, frame_count, width, height, scale_factor=2):
    frames = []
    for i in range(frame_count):
        frame = sheet.subsurface(pygame.Rect(i * width, 0, width, height))
        
        bounding_box = frame.get_bounding_rect()
        
        trimmed_frame = frame.subsurface(bounding_box)
        
        scaled_frame = pygame.transform.scale(trimmed_frame, (bounding_box.width * scale_factor, bounding_box.height * scale_factor))
        
        frames.append(scaled_frame)
    return frames

def load_character_animations(character_folders):
    animations = {}
    hitbox = {}
    for folder in character_folders:
        character_name = os.path.basename(folder)
        animations[character_name] = {}
        hitbox[character_name] = {}
        
        for animation in ["idle", "run", "jump", "attack1", "hurt"]:
            sprite_sheet_path = os.path.join(folder, f"{character_name}_{animation}.png")
            if os.path.exists(sprite_sheet_path):
                sprite_sheet = pygame.image.load(sprite_sheet_path).convert_alpha()
                frame_count = sprite_sheet.get_width() // 48
                animations[character_name][animation] = load_trimmed_frames(sprite_sheet, frame_count, 48, 48)

                hitbox[character_name][animation] = animations[character_name][animation][0].get_bounding_rect()
    
    return animations, hitbox