import pygame
import math
import sys
import random
import json

pygame.init()
pygame.mixer.init()


screen_width, screen_height = 1000, 700
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Snake Adventure - The Ultimate Slither")

clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)
big_font = pygame.font.Font(None, 72)
small_font = pygame.font.Font(None, 24)
medium_font = pygame.font.Font(None, 48)


class GameStats:
    def __init__(self):
        self.score = 0
        self.level = 1
        self.food_eaten = 0
        self.high_score = self.load_high_score()
        self.lives = 3
        self.power_up_timer = 0
        self.invulnerable_timer = 0
        self.base_speed = 0.15  # Starting speed (very slow)
        self.speed_increment = 0.02  # Speed increase per food
        self.max_speed = 0.8  # Maximum speed cap

    def get_current_speed(self):
        """Calculate current speed based on food eaten"""
        current_speed = self.base_speed + (self.food_eaten * self.speed_increment)
        return min(current_speed, self.max_speed)

    def load_high_score(self):
        try:
            with open('high_score.json', 'r') as f:
                return json.load(f).get('high_score', 0)
        except:
            return 0

    def save_high_score(self):
        try:
            with open('high_score.json', 'w') as f:
                json.dump({'high_score': self.high_score}, f)
        except:
            pass


class Food:
    def __init__(self, x=None, y=None, food_type='normal'):
        self.x = x or random.randint(50, screen_width - 50)
        self.y = y or random.randint(50, screen_height - 50)
        self.type = food_type
        self.size = 12 if food_type == 'normal' else 18
        self.points = 10 if food_type == 'normal' else 50
        self.growth = 1 if food_type == 'normal' else 3
        self.pulse = 0
        self.collected = False
        self.sparkle_timer = 0

    def update(self):
        self.pulse += 0.2
        self.sparkle_timer += 1

    def draw(self, surface):
        pulse_size = self.size + math.sin(self.pulse) * 3

        # Enhanced food colors and effects
        if self.type == 'normal':
            # Gradient red apple-like appearance
            color = (220, 50, 50)
            highlight = (255, 100, 100)
        elif self.type == 'super':
            # Golden fruit with shimmer
            color = (255, 215, 0)
            highlight = (255, 255, 150)
        elif self.type == 'power':
            # Purple mystical fruit
            color = (138, 43, 226)
            highlight = (200, 100, 255)

        # Main food body
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), int(pulse_size))

        # Highlight for 3D effect
        highlight_pos = (int(self.x - pulse_size * 0.3), int(self.y - pulse_size * 0.3))
        pygame.draw.circle(surface, highlight, highlight_pos, int(pulse_size * 0.4))

        # Outer glow
        for i in range(3):
            glow_color = (*color, 60 - i * 20)  # Fading alpha
            glow_surface = pygame.Surface((pulse_size * 4, pulse_size * 4), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, glow_color,
                               (pulse_size * 2, pulse_size * 2), int(pulse_size + i * 3))
            surface.blit(glow_surface, (self.x - pulse_size * 2, self.y - pulse_size * 2))

        # Sparkle effect for special foods
        if self.type != 'normal' and self.sparkle_timer % 20 < 10:
            sparkle_positions = [
                (self.x + random.randint(-15, 15), self.y + random.randint(-15, 15))
                for _ in range(3)
            ]
            for pos in sparkle_positions:
                pygame.draw.circle(surface, (255, 255, 255), pos, 2)


class Obstacle:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)

    def draw(self, surface):
        # Enhanced 3D rock appearance
        # Main body
        pygame.draw.rect(surface, (101, 67, 33), self.rect)

        # Top highlight
        highlight_rect = pygame.Rect(self.x, self.y, self.width, 8)
        pygame.draw.rect(surface, (139, 101, 67), highlight_rect)

        # Side shadow
        shadow_rect = pygame.Rect(self.x + self.width - 8, self.y, 8, self.height)
        pygame.draw.rect(surface, (67, 45, 22), shadow_rect)

        # Border
        pygame.draw.rect(surface, (139, 69, 19), self.rect, 3)

        # Texture dots
        for i in range(0, self.width, 20):
            for j in range(0, self.height, 15):
                if random.random() < 0.3:
                    dot_x = self.x + i + random.randint(-5, 5)
                    dot_y = self.y + j + random.randint(-5, 5)
                    if self.rect.collidepoint(dot_x, dot_y):
                        pygame.draw.circle(surface, (89, 59, 31), (dot_x, dot_y), 2)


class Segment:
    def __init__(self, x, y, length, index, total_segments):
        self.x = x
        self.y = y
        self.length = length
        self.angle = 0
        self.index = index
        self.total_segments = total_segments

    def get_thickness(self):
        if self.index == 0:  # Head
            return 32
        else:
            progress = self.index / max(1, self.total_segments - 1)
            return int(26 * (1 - progress * 0.6) + 8)

    def follow(self, tx, ty, wiggle_phase=0, is_moving=True, speed_multiplier=1.0):
        dx = tx - self.x
        dy = ty - self.y
        self.angle = math.atan2(dy, dx)

        wiggle_intensity = (12 if self.index > 0 else 5) * speed_multiplier
        wiggle = math.sin(pygame.time.get_ticks() * 0.02 + wiggle_phase) * wiggle_intensity if is_moving else 0
        offset_x = math.cos(self.angle + math.pi / 2) * wiggle
        offset_y = math.sin(self.angle + math.pi / 2) * wiggle

        target_x = tx - math.cos(self.angle) * self.length + offset_x
        target_y = ty - math.sin(self.angle) * self.length + offset_y

        follow_speed = speed_multiplier
        self.x += (target_x - self.x) * follow_speed
        self.y += (target_y - self.y) * follow_speed

    def get_end(self):
        return (
            self.x + math.cos(self.angle) * self.length,
            self.y + math.sin(self.angle) * self.length
        )

    def get_rect(self):
        thickness = self.get_thickness()
        return pygame.Rect(self.x - thickness // 2, self.y - thickness // 2, thickness, thickness)

    def draw(self, surface, invulnerable=False):
        end_x, end_y = self.get_end()
        thickness = self.get_thickness()

        # Flash if invulnerable
        if invulnerable and pygame.time.get_ticks() % 200 < 100:
            return

        if self.index == 0:  # Enhanced head design
            # Main head circle with gradient
            head_color = (50, 180, 50)
            shadow_color = (30, 120, 30)

            # Shadow/depth
            pygame.draw.circle(surface, shadow_color, (int(self.x + 2), int(self.y + 2)), thickness)
            # Main head
            pygame.draw.circle(surface, head_color, (int(self.x), int(self.y)), thickness)
            # Highlight
            pygame.draw.circle(surface, (80, 220, 80), (int(self.x - 5), int(self.y - 5)), thickness // 3)

            # Enhanced eyes
            eye_offset = 12
            eye_size = 7
            pupil_size = 4

            eye1_x = self.x + math.cos(self.angle - 0.4) * eye_offset
            eye1_y = self.y + math.sin(self.angle - 0.4) * eye_offset
            eye2_x = self.x + math.cos(self.angle + 0.4) * eye_offset
            eye2_y = self.y + math.sin(self.angle + 0.4) * eye_offset

            # Eye whites
            pygame.draw.circle(surface, (255, 255, 255), (int(eye1_x), int(eye1_y)), eye_size)
            pygame.draw.circle(surface, (255, 255, 255), (int(eye2_x), int(eye2_y)), eye_size)

            # Eye pupils
            pygame.draw.circle(surface, (0, 0, 0), (int(eye1_x), int(eye1_y)), pupil_size)
            pygame.draw.circle(surface, (0, 0, 0), (int(eye2_x), int(eye2_y)), pupil_size)

            # Eye shine
            pygame.draw.circle(surface, (255, 255, 255), (int(eye1_x - 1), int(eye1_y - 1)), 2)
            pygame.draw.circle(surface, (255, 255, 255), (int(eye2_x - 1), int(eye2_y - 1)), 2)

            # Enhanced tongue
            if abs(self.x - end_x) > 5 or abs(self.y - end_y) > 5:
                tongue_length = 20
                tongue_x = self.x + math.cos(self.angle) * (thickness + tongue_length)
                tongue_y = self.y + math.sin(self.angle) * (thickness + tongue_length)

                # Forked tongue
                fork_angle1 = self.angle + 0.3
                fork_angle2 = self.angle - 0.3
                fork_length = 8

                fork1_x = tongue_x + math.cos(fork_angle1) * fork_length
                fork1_y = tongue_y + math.sin(fork_angle1) * fork_length
                fork2_x = tongue_x + math.cos(fork_angle2) * fork_length
                fork2_y = tongue_y + math.sin(fork_angle2) * fork_length

                # Main tongue
                pygame.draw.line(surface, (200, 50, 50),
                                 (int(self.x + math.cos(self.angle) * thickness),
                                  int(self.y + math.sin(self.angle) * thickness)),
                                 (int(tongue_x), int(tongue_y)), 4)

                # Fork tips
                pygame.draw.line(surface, (255, 100, 100), (int(tongue_x), int(tongue_y)),
                                 (int(fork1_x), int(fork1_y)), 3)
                pygame.draw.line(surface, (255, 100, 100), (int(tongue_x), int(tongue_y)),
                                 (int(fork2_x), int(fork2_y)), 3)
        else:
            # Enhanced body segments with better gradients
            progress = self.index / self.total_segments
            base_r, base_g, base_b = 50, 180, 50

            # Color variation along body
            r = int(base_r - 20 * progress)
            g = int(base_g - 40 * progress)
            b = int(base_b - 20 * progress)

            shadow_r = max(0, r - 30)
            shadow_g = max(0, g - 30)
            shadow_b = max(0, b - 30)

            if thickness > 4:
                perpendicular_angle = self.angle + math.pi / 2
                half_thickness = thickness / 2

                # Create segment points
                corner1_x = self.x + math.cos(perpendicular_angle) * half_thickness
                corner1_y = self.y + math.sin(perpendicular_angle) * half_thickness
                corner2_x = self.x - math.cos(perpendicular_angle) * half_thickness
                corner2_y = self.y - math.sin(perpendicular_angle) * half_thickness
                corner3_x = end_x - math.cos(perpendicular_angle) * half_thickness
                corner3_y = end_y - math.sin(perpendicular_angle) * half_thickness
                corner4_x = end_x + math.cos(perpendicular_angle) * half_thickness
                corner4_y = end_y + math.sin(perpendicular_angle) * half_thickness

                # Draw shadow first
                shadow_points = [(corner1_x + 2, corner1_y + 2), (corner2_x + 2, corner2_y + 2),
                                 (corner3_x + 2, corner3_y + 2), (corner4_x + 2, corner4_y + 2)]
                pygame.draw.polygon(surface, (shadow_r, shadow_g, shadow_b), shadow_points)

                # Main body
                points = [(corner1_x, corner1_y), (corner2_x, corner2_y),
                          (corner3_x, corner3_y), (corner4_x, corner4_y)]
                pygame.draw.polygon(surface, (r, g, b), points)

                # End caps
                pygame.draw.circle(surface, (r, g, b), (int(self.x), int(self.y)), int(half_thickness))
                pygame.draw.circle(surface, (r, g, b), (int(end_x), int(end_y)), int(half_thickness))

                # Scale pattern
                if self.index % 3 == 0:
                    scale_color = (min(255, r + 40), min(255, g + 40), min(255, b + 20))
                    mid_x = (self.x + end_x) / 2
                    mid_y = (self.y + end_y) / 2
                    scale_size = max(3, thickness // 8)
                    pygame.draw.circle(surface, scale_color, (int(mid_x), int(mid_y)), scale_size)


class Snake:
    def __init__(self):
        self.reset()

    def reset(self):
        self.num_segments = 8
        self.segment_length = 18
        start_x = screen_width // 2
        start_y = screen_height // 2
        self.segments = [Segment(start_x, start_y, self.segment_length, i, self.num_segments)
                         for i in range(self.num_segments)]
        self.target_x, self.target_y = start_x, start_y
        self.moving = False
        self.speed_boost = 1.0

    def add_segment(self, count=1):
        for _ in range(count):
            last_seg = self.segments[-1]
            new_seg = Segment(last_seg.x, last_seg.y, self.segment_length,
                              len(self.segments), len(self.segments) + 1)
            self.segments.append(new_seg)

        # Update indices
        for i, seg in enumerate(self.segments):
            seg.index = i
            seg.total_segments = len(self.segments)

    def update(self, target_x, target_y, base_speed):
        self.target_x, self.target_y = target_x, target_y

        head = self.segments[0]
        dist = math.hypot(target_x - head.x, target_y - head.y)
        self.moving = dist > 15

        # Apply the gradual speed system
        current_speed = base_speed * self.speed_boost

        self.segments[0].follow(target_x, target_y, wiggle_phase=0,
                                is_moving=self.moving, speed_multiplier=current_speed)

        for i in range(1, len(self.segments)):
            self.segments[i].follow(self.segments[i - 1].x, self.segments[i - 1].y,
                                    i * 0.4, is_moving=self.moving, speed_multiplier=current_speed)

    def check_food_collision(self, food_list):
        head = self.segments[0]
        head_rect = pygame.Rect(head.x - 22, head.y - 22, 44, 44)

        for food in food_list[:]:
            food_rect = pygame.Rect(food.x - food.size, food.y - food.size,
                                    food.size * 2, food.size * 2)
            if head_rect.colliderect(food_rect):
                return food
        return None

    def check_obstacle_collision(self, obstacles):
        head = self.segments[0]
        head_rect = pygame.Rect(head.x - 18, head.y - 18, 36, 36)

        for obstacle in obstacles:
            if head_rect.colliderect(obstacle.rect):
                return True
        return False

    def check_wall_collision(self):
        head = self.segments[0]
        margin = 25
        return (head.x < margin or head.x > screen_width - margin or
                head.y < margin or head.y > screen_height - margin)

    def check_self_collision(self):
        if len(self.segments) < 6:
            return False

        head = self.segments[0]
        head_rect = pygame.Rect(head.x - 18, head.y - 18, 36, 36)

        for seg in self.segments[5:]:  # Skip first few segments
            seg_rect = seg.get_rect()
            if head_rect.colliderect(seg_rect):
                return True
        return False

    def draw(self, surface, invulnerable=False):
        for seg in reversed(self.segments):
            seg.draw(surface, invulnerable)


class Game:
    def __init__(self):
        self.state = "menu"  # menu, playing, paused, game_over
        self.stats = GameStats()
        self.snake = Snake()
        self.food_list = []
        self.obstacles = []
        self.particles = []
        self.generate_level()

    def generate_level(self):
        self.food_list.clear()
        self.obstacles.clear()

        # Generate food
        food_count = 6 + self.stats.level
        for _ in range(food_count):
            while True:
                food = Food()
                # Make sure food doesn't spawn in obstacles or too close to snake
                valid = True
                for obstacle in self.obstacles:
                    if obstacle.rect.collidepoint(food.x, food.y):
                        valid = False
                        break
                if valid and len(self.snake.segments) > 0:
                    head = self.snake.segments[0]
                    if math.hypot(food.x - head.x, food.y - head.y) < 120:
                        valid = False
                if valid:
                    break

            # Chance for special food
            if random.random() < 0.18:
                food.type = 'super'
            elif random.random() < 0.08:
                food.type = 'power'

            self.food_list.append(food)

        # Generate obstacles based on level
        obstacle_count = min(self.stats.level - 1, 10)
        for _ in range(obstacle_count):
            width = random.randint(70, 140)
            height = random.randint(40, 90)
            x = random.randint(60, screen_width - width - 60)
            y = random.randint(60, screen_height - height - 60)
            self.obstacles.append(Obstacle(x, y, width, height))

    def handle_food_collection(self, food):
        self.stats.score += food.points
        self.stats.food_eaten += 1

        if food.type == 'power':
            self.stats.power_up_timer = 300  # 5 seconds at 60fps
            self.snake.speed_boost = 2.0

        self.snake.add_segment(food.growth)
        self.food_list.remove(food)

        # Level up check
        if len(self.food_list) == 0:
            self.stats.level += 1
            self.stats.invulnerable_timer = 180  # 3 seconds
            self.generate_level()

    def update_game(self):
        if self.state != "playing":
            return

        # Update timers
        if self.stats.power_up_timer > 0:
            self.stats.power_up_timer -= 1
            if self.stats.power_up_timer == 0:
                self.snake.speed_boost = 1.0

        if self.stats.invulnerable_timer > 0:
            self.stats.invulnerable_timer -= 1

        # Update food
        for food in self.food_list:
            food.update()

        # Check food collision
        collected_food = self.snake.check_food_collision(self.food_list)
        if collected_food:
            self.handle_food_collection(collected_food)

        # Check collisions (only if not invulnerable)
        if self.stats.invulnerable_timer == 0:
            if (self.snake.check_wall_collision() or
                    self.snake.check_obstacle_collision(self.obstacles) or
                    self.snake.check_self_collision()):

                self.stats.lives -= 1
                if self.stats.lives <= 0:
                    self.state = "game_over"
                    if self.stats.score > self.stats.high_score:
                        self.stats.high_score = self.stats.score
                        self.stats.save_high_score()
                else:
                    # Reset snake position
                    self.snake.reset()
                    self.stats.invulnerable_timer = 180

    def draw_speed_meter(self, surface):
        """Draw a visual speed meter"""
        meter_x = screen_width - 200
        meter_y = 50
        meter_width = 150
        meter_height = 20

        # Background
        pygame.draw.rect(surface, (50, 50, 50), (meter_x, meter_y, meter_width, meter_height))
        pygame.draw.rect(surface, (100, 100, 100), (meter_x, meter_y, meter_width, meter_height), 2)

        # Speed fill
        current_speed = self.stats.get_current_speed()
        speed_ratio = (current_speed - self.stats.base_speed) / (self.stats.max_speed - self.stats.base_speed)
        fill_width = int(meter_width * speed_ratio)

        if fill_width > 0:
            # Color gradient based on speed
            if speed_ratio < 0.3:
                color = (0, 255, 0)  # Green
            elif speed_ratio < 0.7:
                color = (255, 255, 0)  # Yellow
            else:
                color = (255, 100, 0)  # Orange-red

            pygame.draw.rect(surface, color, (meter_x, meter_y, fill_width, meter_height))

        # Label
        speed_text = small_font.render("SPEED", True, (255, 255, 255))
        surface.blit(speed_text, (meter_x, meter_y - 25))

    def draw_ui(self, surface):
        # Enhanced UI with better layout and styling
        # Background panel
        ui_panel = pygame.Surface((300, 180), pygame.SRCALPHA)
        ui_panel.fill((0, 0, 0, 120))
        surface.blit(ui_panel, (5, 5))

        # Score and stats with better formatting
        score_text = font.render(f"Score: {self.stats.score:,}", True, (255, 255, 100))
        level_text = font.render(f"Level: {self.stats.level}", True, (100, 255, 100))
        lives_text = font.render(f"Lives: {'♥' * self.stats.lives}", True, (255, 100, 100))
        food_text = small_font.render(f"Food Remaining: {len(self.food_list)}", True, (255, 255, 255))
        length_text = small_font.render(f"Snake Length: {len(self.snake.segments)}", True, (200, 200, 255))

        # Speed info
        current_speed = self.stats.get_current_speed()
        speed_percentage = int((current_speed / self.stats.max_speed) * 100)
        speed_text = small_font.render(f"Speed: {speed_percentage}%", True, (255, 200, 100))

        surface.blit(score_text, (15, 15))
        surface.blit(level_text, (15, 50))
        surface.blit(lives_text, (15, 85))
        surface.blit(food_text, (15, 115))
        surface.blit(length_text, (15, 135))
        surface.blit(speed_text, (15, 155))

        # Power-up indicator with enhanced effects
        if self.stats.power_up_timer > 0:
            power_bg = pygame.Surface((200, 30), pygame.SRCALPHA)
            power_bg.fill((138, 43, 226, 150))
            surface.blit(power_bg, (350, 10))

            power_text = font.render("⚡ SPEED BOOST! ⚡", True, (255, 255, 255))
            surface.blit(power_text, (360, 15))

        # Speed meter
        self.draw_speed_meter(surface)

        # High score with better positioning
        high_score_bg = pygame.Surface((180, 30), pygame.SRCALPHA)
        high_score_bg.fill((0, 0, 0, 120))
        surface.blit(high_score_bg, (screen_width - 185, 80))

        high_score_text = small_font.render(f"High Score: {self.stats.high_score:,}", True, (255, 215, 0))
        surface.blit(high_score_text, (screen_width - 180, 90))

    def draw_menu(self, surface):
        # Enhanced menu with gradient background
        for y in range(screen_height):
            color_ratio = y / screen_height
            r = int(20 + (40 - 20) * color_ratio)
            g = int(40 + (80 - 40) * color_ratio)
            b = int(20 + (40 - 20) * color_ratio)
            pygame.draw.line(surface, (r, g, b), (0, y), (screen_width, y))

        title = big_font.render("🐍 SNAKE ADVENTURE 🐍", True, (50, 255, 50))
        subtitle = font.render("The Ultimate Slither Experience", True, (255, 255, 255))

        instructions = [
            "🎯 Click anywhere to guide your snake",
            "🍎 Red food: Basic growth and points",
            "🟡 Gold food: Bonus points and extra growth",
            "🟣 Purple food: Speed boost power-up",
            "⚠️ Avoid walls, rocks, and yourself",
            "🏆 Clear all food to advance levels",
            "🚀 Snake gets faster as you eat more!",
            "",
            "🎮 Click anywhere to start your adventure!"
        ]

        title_rect = title.get_rect(center=(screen_width // 2, 120))
        subtitle_rect = subtitle.get_rect(center=(screen_width // 2, 170))

        surface.blit(title, title_rect)
        surface.blit(subtitle, subtitle_rect)

        y_offset = 230
        for instruction in instructions:
            if instruction:
                color = (200, 200, 200) if not instruction.startswith("🎮") else (100, 255, 100)
                text = small_font.render(instruction, True, color)
                text_rect = text.get_rect(center=(screen_width // 2, y_offset))
                surface.blit(text, text_rect)
            y_offset += 35

    def draw_game_over(self, surface):
        # Enhanced game over screen
        for y in range(screen_height):
            color_ratio = y / screen_height
            r = int(60 + (20 - 60) * color_ratio)
            g = int(20)
            b = int(20)
            pygame.draw.line(surface, (r, g, b), (0, y), (screen_width, y))

        game_over_text = big_font.render("💀 GAME OVER 💀", True, (255, 100, 100))
        final_score = font.render(f"Final Score: {self.stats.score:,}", True, (255, 255, 255))
        level_reached = font.render(f"Level Reached: {self.stats.level}", True, (255, 255, 255))
        length_reached = font.render(f"Max Length: {len(self.snake.segments)}", True, (200, 200, 255))
        food_eaten = font.render(f"Food Consumed: {self.stats.food_eaten}", True, (100, 255, 100))
        high_score = font.render(f"High Score: {self.stats.high_score:,}", True, (255, 215, 0))

        if self.stats.score == self.stats.high_score and self.stats.score > 0:
            new_record = medium_font.render("🎉 NEW HIGH SCORE! 🎉", True, (255, 215, 0))
        else:
            new_record = None

        restart_text = small_font.render("Press R to restart or ESC for menu", True, (200, 200, 200))

        game_over_rect = game_over_text.get_rect(center=(screen_width // 2, 200))
        final_score_rect = final_score.get_rect(center=(screen_width // 2, 280))
        level_rect = level_reached.get_rect(center=(screen_width // 2, 320))
        length_rect = length_reached.get_rect(center=(screen_width // 2, 360))
        food_rect = food_eaten.get_rect(center=(screen_width // 2, 400))
        high_score_rect = high_score.get_rect(center=(screen_width // 2, 440))
        restart_rect = restart_text.get_rect(center=(screen_width // 2, 520))

        surface.blit(game_over_text, game_over_rect)
        surface.blit(final_score, final_score_rect)
        surface.blit(level_reached, level_rect)
        surface.blit(length_reached, length_rect)
        surface.blit(food_eaten, food_rect)
        surface.blit(high_score, high_score_rect)
        surface.blit(restart_text, restart_rect)

        if new_record:
            new_record_rect = new_record.get_rect(center=(screen_width // 2, 480))
            surface.blit(new_record, new_record_rect)

    def run(self):
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.state == "playing":
                            self.state = "paused" if self.state != "paused" else "playing"
                        else:
                            self.state = "menu"

                    elif event.key == pygame.K_r and self.state == "game_over":
                        self.__init__()  # Reset game
                        self.state = "playing"

                    elif event.key == pygame.K_p and self.state == "playing":
                        self.state = "paused"

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.state == "menu":
                        self.state = "playing"
                    elif self.state == "playing":
                        pass  # Mouse movement handled in main loop
                    elif self.state == "paused":
                        self.state = "playing"

            # Update game logic
            if self.state == "playing":
                mouse_pos = pygame.mouse.get_pos()
                current_speed = self.stats.get_current_speed()
                self.snake.update(mouse_pos[0], mouse_pos[1], current_speed)
                self.update_game()

            # Draw everything
            if self.state == "menu":
                self.draw_menu(screen)
            elif self.state == "game_over":
                self.draw_game_over(screen)
            else:
                # Enhanced game background with animated grass
                base_color = (25, 35, 25)
                screen.fill(base_color)

                # Animated grass pattern
                time_offset = pygame.time.get_ticks() * 0.001
                for i in range(0, screen_width, 40):
                    for j in range(0, screen_height, 40):
                        if (i + j) % 80 == 0:
                            grass_size = 3 + math.sin(time_offset + i * 0.01 + j * 0.01) * 1
                            grass_color = (30 + int(math.sin(time_offset + i * 0.02) * 10),
                                           45 + int(math.cos(time_offset + j * 0.02) * 10),
                                           30)
                            pygame.draw.circle(screen, grass_color, (i, j), int(grass_size))

                # Draw obstacles
                for obstacle in self.obstacles:
                    obstacle.draw(screen)

                # Draw food
                for food in self.food_list:
                    food.draw(screen)

                # Draw snake
                self.snake.draw(screen, self.stats.invulnerable_timer > 0)

                # Draw UI
                self.draw_ui(screen)

                # Paused overlay
                if self.state == "paused":
                    overlay = pygame.Surface((screen_width, screen_height))
                    overlay.set_alpha(180)
                    overlay.fill((0, 0, 0))
                    screen.blit(overlay, (0, 0))

                    paused_text = big_font.render("⏸️ PAUSED ⏸️", True, (255, 255, 255))
                    paused_rect = paused_text.get_rect(center=(screen_width // 2, screen_height // 2))
                    screen.blit(paused_text, paused_rect)

                    resume_text = small_font.render("Click to resume or press ESC for menu", True, (200, 200, 200))
                    resume_rect = resume_text.get_rect(center=(screen_width // 2, screen_height // 2 + 50))
                    screen.blit(resume_text, resume_rect)

            pygame.display.flip()
            clock.tick(60)

        pygame.quit()
        sys.exit()


# Run the game
if __name__ == "__main__":
    game = Game()
    game.run()
