import pygame
import random
import math
import numpy as np
from pygame import gfxdraw
from collections import deque
from enum import Enum
import unittest

# Inicialização do Pygame
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

# Constantes do jogo
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Cores Futuristas
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)
ELECTRIC_BLUE = (0, 170, 255)
NEON_GREEN = (57, 255, 20)
HOT_PINK = (255, 0, 128)
PURPLE = (180, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
RED = (255, 50, 50)
DARK_BLUE = (0, 0, 40)
GOLD = (255, 215, 0)

# Tipos de armas
class WeaponType(Enum):
    BASIC = 1
    SPREAD = 2
    RAPID = 3
    LASER_BEAM = 4
    HOMING = 5

class SoundManager:
    """Gerenciador de efeitos sonoros"""
    def __init__(self):
        self.sounds = {}
        self.load_sounds()
    
    def load_sounds(self):
        try:
            self.create_laser_sound()
            self.create_explosion_sound()
            self.create_powerup_sound()
        except:
            pass
    
    def create_laser_sound(self):
        sample_rate = 22050
        duration = 0.2
        frequency = 440
        
        frames = int(duration * sample_rate)
        arr = np.zeros((frames, 2))
        
        for i in range(frames):
            t = float(i) / sample_rate
            wave = np.sin(2 * np.pi * frequency * t) * np.exp(-t * 10)
            wave += np.sin(2 * np.pi * frequency * 2 * t) * 0.3 * np.exp(-t * 15)
            
            arr[i] = [wave, wave]
        
        arr = (arr * 32767).astype(np.int16)
        self.sounds['laser'] = pygame.sndarray.make_sound(arr)
    
    def create_explosion_sound(self):
        sample_rate = 22050
        duration = 0.5
        
        frames = int(duration * sample_rate)
        arr = np.zeros((frames, 2))
        
        for i in range(frames):
            t = float(i) / sample_rate
            noise = np.random.normal(0, 0.1)
            freq = 200 * (1 - t/duration)
            wave = np.sin(2 * np.pi * freq * t) * (1 - t/duration)
            
            arr[i] = [(noise + wave) * 32767 * (1 - t/duration), 
                     (noise + wave) * 32767 * (1 - t/duration)]
        
        arr = np.clip(arr, -32767, 32767).astype(np.int16)
        self.sounds['explosion'] = pygame.sndarray.make_sound(arr)
    
    def create_powerup_sound(self):
        sample_rate = 22050
        duration = 0.3
        
        frames = int(duration * sample_rate)
        arr = np.zeros((frames, 2))
        
        for i in range(frames):
            t = float(i) / sample_rate
            # Som ascendente de power-up
            freq = 400 + t * 800
            wave = np.sin(2 * np.pi * freq * t) * (1 - t)
            arr[i] = [wave * 32767, wave * 32767]
        
        self.sounds['powerup'] = pygame.sndarray.make_sound(arr.astype(np.int16))
    
    def play(self, sound_name):
        if sound_name in self.sounds:
            self.sounds[sound_name].play()

class Particle:
    """Partícula individual otimizada"""
    __slots__ = ['x', 'y', 'vx', 'vy', 'size', 'color', 'life', 'max_life']
    
    def __init__(self, x, y, vx, vy, size, color, life):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.size = size
        self.color = color
        self.life = life
        self.max_life = life
    
    def update(self, dt):
        self.x += self.vx * dt * 60
        self.y += self.vy * dt * 60
        self.life -= dt
        return self.life > 0
    
    def draw(self, surface):
        alpha = int(255 * (self.life / self.max_life))
        color = (*self.color[:3], alpha)
        gfxdraw.filled_circle(surface, int(self.x), int(self.y), int(self.size), color)

class ParticleSystem:
    """Sistema de partículas otimizado"""
    def __init__(self, max_particles=500):
        self.max_particles = max_particles
        self.particles = []
        
    def emit(self, x, y, color, count=30, speed_range=(1, 5), size_range=(1, 4)):
        for _ in range(min(count, self.max_particles - len(self.particles))):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(*speed_range)
            size = random.uniform(*size_range)
            
            particle = Particle(
                x, y,
                math.cos(angle) * speed,
                math.sin(angle) * speed,
                size, color, random.uniform(0.5, 1.5)
            )
            self.particles.append(particle)
    
    def update(self, dt):
        for particle in self.particles[:]:
            if not particle.update(dt):
                self.particles.remove(particle)
    
    def draw(self, surface):
        for particle in self.particles:
            particle.draw(surface)

class Trail:
    """Classe para gerenciar o rastro da nave"""
    def __init__(self, max_length=20):
        self.points = deque(maxlen=max_length)
        self.max_length = max_length
        
    def add_point(self, x, y):
        self.points.append((x, y))
    
    def update(self):
        pass
    
    def draw(self, surface):
        if len(self.points) > 1:
            for i in range(1, len(self.points)):
                alpha = int(255 * (i / len(self.points)) * 0.7)
                color = (*ELECTRIC_BLUE, alpha)
                
                start_pos = self.points[i-1]
                end_pos = self.points[i]
                
                trail_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                pygame.draw.line(trail_surf, color, start_pos, end_pos, 3)
                surface.blit(trail_surf, (0, 0), special_flags=pygame.BLEND_ADD)

class Bullet:
    """Classe base para projéteis"""
    def __init__(self, x, y, weapon_type=WeaponType.BASIC):
        self.x = x
        self.y = y
        self.weapon_type = weapon_type
        self.active = True
        self.speed = 15
        self.damage = 1
        self.size = 4
        
        if weapon_type == WeaponType.BASIC:
            self.color = CYAN
            self.speed = 15
        elif weapon_type == WeaponType.SPREAD:
            self.color = YELLOW
            self.speed = 12
        elif weapon_type == WeaponType.RAPID:
            self.color = NEON_GREEN
            self.speed = 20
        elif weapon_type == WeaponType.LASER_BEAM:
            self.color = PURPLE
            self.speed = 25
        elif weapon_type == WeaponType.HOMING:
            self.color = HOT_PINK
            self.speed = 10
            self.target = None
    
    def update(self, asteroids):
        if self.weapon_type == WeaponType.HOMING and asteroids:
            # Encontrar o asteroide mais próximo
            if not self.target or self.target not in asteroids:
                min_dist = float('inf')
                for asteroid in asteroids:
                    dist = math.sqrt((asteroid.rect.centerx - self.x)**2 + 
                                   (asteroid.rect.centery - self.y)**2)
                    if dist < min_dist:
                        min_dist = dist
                        self.target = asteroid
            
            # Mover em direção ao alvo
            if self.target:
                dx = self.target.rect.centerx - self.x
                dy = self.target.rect.centery - self.y
                dist = math.sqrt(dx**2 + dy**2)
                if dist > 0:
                    self.x += (dx / dist) * self.speed
                    self.y += (dy / dist) * self.speed
        else:
            # Movimento padrão
            self.y -= self.speed
        
        # Verificar se saiu da tela
        if self.y < -10 or self.x < -10 or self.x > SCREEN_WIDTH + 10:
            self.active = False
    
    def draw(self, surface):
        if self.weapon_type == WeaponType.BASIC:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.size)
            pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), self.size, 1)
        elif self.weapon_type == WeaponType.SPREAD:
            pygame.draw.rect(surface, self.color, (int(self.x-3), int(self.y-6), 6, 12))
            pygame.draw.rect(surface, WHITE, (int(self.x-3), int(self.y-6), 6, 12), 1)
        elif self.weapon_type == WeaponType.RAPID:
            pygame.draw.ellipse(surface, self.color, (int(self.x-2), int(self.y-8), 4, 16))
        elif self.weapon_type == WeaponType.LASER_BEAM:
            pygame.draw.line(surface, self.color, (int(self.x), int(self.y)), 
                          (int(self.x), int(self.y-20)), 3)
            # Brilho
            for i in range(2):
                alpha = 100 - i * 40
                glow_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                pygame.draw.line(glow_surf, (*self.color, alpha), 
                               (int(self.x), int(self.y)), 
                               (int(self.x), int(self.y-20)), 5-i*2)
                surface.blit(glow_surf, (0, 0), special_flags=pygame.BLEND_ADD)
        elif self.weapon_type == WeaponType.HOMING:
            # Desenhar míssil
            points = [(int(self.x), int(self.y-8)), 
                     (int(self.x-4), int(self.y+4)), 
                     (int(self.x+4), int(self.y+4))]
            pygame.draw.polygon(surface, self.color, points)
            pygame.draw.polygon(surface, WHITE, points, 1)
    
    def get_rect(self):
        return pygame.Rect(self.x - self.size, self.y - self.size, 
                         self.size * 2, self.size * 2)

class PowerUp(pygame.sprite.Sprite):
    """Power-ups que mudam a arma"""
    def __init__(self, x, y, weapon_type):
        super().__init__()
        self.weapon_type = weapon_type
        
        # Inicializar cores antes de desenhar
        self.colors = {
            WeaponType.BASIC: CYAN,
            WeaponType.SPREAD: YELLOW,
            WeaponType.RAPID: NEON_GREEN,
            WeaponType.LASER_BEAM: PURPLE,
            WeaponType.HOMING: HOT_PINK
        }
        
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        self.draw_powerup()
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.speed_y = 2
        self.pulse = 0
    
    def draw_powerup(self):
        color = self.colors[self.weapon_type]
        center = (20, 20)
        
        # Desenhar ícone baseado no tipo de arma
        if self.weapon_type == WeaponType.BASIC:
            # Círculo com ponto no centro
            pygame.draw.circle(self.image, color, center, 15)
            pygame.draw.circle(self.image, WHITE, center, 15, 2)
            pygame.draw.circle(self.image, WHITE, center, 5)
        elif self.weapon_type == WeaponType.SPREAD:
            # Três pontos em formação de triângulo
            for i in range(3):
                angle = i * 2 * math.pi / 3
                x = center[0] + 10 * math.cos(angle)
                y = center[1] + 10 * math.sin(angle)
                pygame.draw.circle(self.image, color, (int(x), int(y)), 6)
        elif self.weapon_type == WeaponType.RAPID:
            # Linhas rápidas
            for i in range(4):
                y = center[1] - 12 + i * 8
                pygame.draw.line(self.image, color, (center[0]-8, y), (center[0]+8, y), 3)
        elif self.weapon_type == WeaponType.LASER_BEAM:
            # Linha vertical com brilho
            pygame.draw.line(self.image, color, (center[0], center[1]-15), 
                           (center[0], center[1]+15), 4)
            for i in range(2):
                alpha = 100 - i * 40
                glow_surf = pygame.Surface((40, 40), pygame.SRCALPHA)
                pygame.draw.line(glow_surf, (*color, alpha), 
                               (center[0], center[1]-15), 
                               (center[0], center[1]+15), 6-i*2)
                self.image.blit(glow_surf, (0, 0), special_flags=pygame.BLEND_ADD)
        elif self.weapon_type == WeaponType.HOMING:
            # Forma de míssil
            points = [(center[0], center[1]-10), 
                     (center[0]-8, center[1]+10), 
                     (center[0]+8, center[1]+10)]
            pygame.draw.polygon(self.image, color, points)
            pygame.draw.polygon(self.image, WHITE, points, 2)
    
    def update(self, dt):
        self.rect.y += self.speed_y
        self.pulse += dt * 5
        
        # Remover se sair da tela
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()
    
    def draw(self, surface):
        # Efeito de pulsação
        pulse_scale = 1 + math.sin(self.pulse) * 0.1
        scaled_image = pygame.transform.scale(self.image, 
                                           (int(self.rect.width * pulse_scale), 
                                            int(self.rect.height * pulse_scale)))
        scaled_rect = scaled_image.get_rect(center=self.rect.center)
        surface.blit(scaled_image, scaled_rect)

class Player(pygame.sprite.Sprite):
    """Nave do jogador"""
    __slots__ = ['image', 'rect', 'speed_x', 'lives', 'shoot_cooldown', 'invulnerable', 
                 'angle', 'trail', 'shield_active', 'shield_timer', 'weapon_type', 
                 'weapon_timer']
    
    def __init__(self):
        super().__init__()
        
        # Inicializar todos os atributos antes de desenhar a nave
        self.speed_x = 0
        self.lives = 3
        self.shoot_cooldown = 0
        self.invulnerable = 0
        self.angle = -math.pi/2
        self.trail = Trail()
        self.shield_active = False
        self.shield_timer = 0
        self.weapon_type = WeaponType.BASIC  # Inicializar antes de desenhar
        self.weapon_timer = 0
        
        # Agora podemos desenhar a nave
        self.image = pygame.Surface((60, 50), pygame.SRCALPHA)
        self.draw_spaceship()
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 30
        
    def draw_spaceship(self):
        # Desenha uma nave futurista
        points = [
            (30, 0),   # Topo
            (15, 30),  # Meio esquerdo
            (5, 45),   # Base esquerda
            (55, 45),  # Base direita
            (45, 30)   # Meio direito
        ]
        pygame.draw.polygon(self.image, ELECTRIC_BLUE, points)
        pygame.draw.polygon(self.image, CYAN, points, 2)
        
        # Cabine
        pygame.draw.circle(self.image, NEON_GREEN, (30, 20), 10)
        pygame.draw.circle(self.image, WHITE, (30, 20), 10, 2)
        
        # Motores
        for x, y in [(18, 40), (42, 40)]:
            pygame.draw.circle(self.image, HOT_PINK, (x, y), 6)
            pygame.draw.circle(self.image, YELLOW, (x, y), 3)
        
        # Asas
        pygame.draw.polygon(self.image, PURPLE, [(0, 30), (15, 25), (15, 40)])
        pygame.draw.polygon(self.image, PURPLE, [(60, 30), (45, 25), (45, 40)])
        
        # Mudar cor baseado na arma
        weapon_colors = {
            WeaponType.BASIC: CYAN,
            WeaponType.SPREAD: YELLOW,
            WeaponType.RAPID: NEON_GREEN,
            WeaponType.LASER_BEAM: PURPLE,
            WeaponType.HOMING: HOT_PINK
        }
        
        # Destacar a arma atual
        weapon_color = weapon_colors.get(self.weapon_type, CYAN)
        pygame.draw.circle(self.image, weapon_color, (30, 5), 8, 3)
        
    def update(self, dt):
        # Atualizar timer da arma
        if self.weapon_timer > 0:
            self.weapon_timer -= dt
            if self.weapon_timer <= 0:
                self.weapon_type = WeaponType.BASIC
                self.draw_spaceship()
        
        # Adicionar ponto ao rastro
        self.trail.add_point(self.rect.centerx, self.rect.centery)
        
        # Movimento - AUMENTADO A VELOCIDADE DE 8 PARA 12
        self.speed_x = 0
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.speed_x = -12  # AUMENTADO DE 8 PARA 12
            self.angle = -math.pi/2 - 0.3
        elif keys[pygame.K_RIGHT]:
            self.speed_x = 12   # AUMENTADO DE 8 PARA 12
            self.angle = -math.pi/2 + 0.3
        else:
            self.angle = -math.pi/2
            
        self.rect.x += self.speed_x * dt * 60
        
        # Limitar à tela
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
            
        # Recarregar tiro baseado na arma
        cooldowns = {
            WeaponType.BASIC: 10,
            WeaponType.SPREAD: 15,
            WeaponType.RAPID: 3,
            WeaponType.LASER_BEAM: 8,
            WeaponType.HOMING: 20
        }
        
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= dt * 60
            
        # Invulnerabilidade após hit
        if self.invulnerable > 0:
            self.invulnerable -= dt
            self.shield_active = True
            self.shield_timer = self.invulnerable
        else:
            self.shield_active = False
            
    def shoot(self, sound_manager, bullets):
        if self.shoot_cooldown <= 0:
            cooldowns = {
                WeaponType.BASIC: 10,
                WeaponType.SPREAD: 15,
                WeaponType.RAPID: 3,
                WeaponType.LASER_BEAM: 8,
                WeaponType.HOMING: 20
            }
            
            self.shoot_cooldown = cooldowns[self.weapon_type]
            sound_manager.play('laser')
            
            # Criar balas baseado no tipo de arma
            if self.weapon_type == WeaponType.BASIC:
                bullets.append(Bullet(self.rect.centerx, self.rect.top, self.weapon_type))
            elif self.weapon_type == WeaponType.SPREAD:
                # Três balas em formação de leque
                for angle in [-0.3, 0, 0.3]:
                    bullet = Bullet(self.rect.centerx, self.rect.top, self.weapon_type)
                    bullet.vx = math.sin(angle) * 5
                    bullet.vy = -math.cos(angle) * 15
                    bullets.append(bullet)
            elif self.weapon_type == WeaponType.RAPID:
                # Uma bala rápida
                bullets.append(Bullet(self.rect.centerx, self.rect.top, self.weapon_type))
            elif self.weapon_type == WeaponType.LASER_BEAM:
                # Laser contínuo
                bullets.append(Bullet(self.rect.centerx, self.rect.top, self.weapon_type))
            elif self.weapon_type == WeaponType.HOMING:
                # Míssil teleguiado
                bullets.append(Bullet(self.rect.centerx, self.rect.top, self.weapon_type))
    
    def change_weapon(self, weapon_type):
        self.weapon_type = weapon_type
        self.weapon_timer = 10.0  # 10 segundos de power-up
        self.draw_spaceship()
    
    def draw_shield(self, surface):
        if self.shield_active:
            pulse = math.sin(self.shield_timer * 10) * 0.2 + 0.8
            radius = int(40 * pulse)
            alpha = int(100 * pulse)
            
            shield_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            pygame.draw.circle(shield_surf, (*CYAN, alpha), self.rect.center, radius, 3)
            surface.blit(shield_surf, (0, 0), special_flags=pygame.BLEND_ADD)

class Asteroid(pygame.sprite.Sprite):
    """Asteroide com movimento contínuo"""
    __slots__ = ['image', 'rect', 'size', 'speed_y', 'speed_x', 'rotation', 'rotation_speed', 
                 'health', 'max_health', 'id', 'cracks', 'energy_core', 'original_image', 'size_category']
    
    def __init__(self, size_category=1):
        super().__init__()
        # Tamanho baseado na categoria (1=pequeno, 2=médio, 3=grande)
        self.size_category = size_category
        if size_category == 1:
            self.size = random.randint(20, 40)
            self.health = 1
        elif size_category == 2:
            self.size = random.randint(40, 60)
            self.health = 2
        else:
            self.size = random.randint(60, 80)
            self.health = 3
            
        self.rect = pygame.Rect(0, 0, self.size*2, self.size*2)
        
        # Inicializar todos os atributos
        self.speed_y = random.uniform(1, 2 + size_category)
        self.speed_x = random.uniform(-1, 1)
        self.rotation = 0
        self.rotation_speed = random.uniform(-2, 2)
        self.max_health = self.health
        self.id = id(self)
        self.cracks = []
        self.energy_core = random.choice([True, False])
        
        # Criar imagem original
        self.original_image = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
        self.draw_asteroid()
        self.image = self.original_image.copy()
        
        # Posicionar o asteroide
        self.rect.x = random.randint(0, SCREEN_WIDTH - self.size)
        self.rect.y = random.randint(-100, -40)
        
    def draw_asteroid(self):
        center = (self.size, self.size)
        
        # Base do asteroide
        points = []
        num_points = 12
        for i in range(num_points):
            angle = (2 * math.pi * i) / num_points
            radius = self.size * random.uniform(0.8, 1.0)
            x = center[0] + radius * math.cos(angle)
            y = center[1] + radius * math.sin(angle)
            points.append((x, y))
            
        pygame.draw.polygon(self.original_image, (80, 80, 90), points)
        pygame.draw.polygon(self.original_image, ELECTRIC_BLUE, points, 2)
        
        # Adiciona textura com cristais
        for _ in range(int(self.size/8)):
            crystal_x = random.randint(int(self.size*0.3), int(self.size*1.7))
            crystal_y = random.randint(int(self.size*0.3), int(self.size*1.7))
            crystal_size = random.randint(3, int(self.size/6))
            color = random.choice([CYAN, NEON_GREEN, HOT_PINK])
            pygame.draw.circle(self.original_image, color, (crystal_x, crystal_y), crystal_size)
        
        # Núcleo de energia para alguns asteroides
        if self.energy_core:
            pygame.draw.circle(self.original_image, YELLOW, center, int(self.size*0.3))
            pygame.draw.circle(self.original_image, WHITE, center, int(self.size*0.3), 2)
            
    def add_crack(self):
        if len(self.cracks) < 5:
            start_x = random.randint(int(self.size*0.3), int(self.size*1.7))
            start_y = random.randint(int(self.size*0.3), int(self.size*1.7))
            length = random.randint(int(self.size*0.2), int(self.size*0.5))
            angle = random.uniform(0, 2 * math.pi)
            
            end_x = start_x + length * math.cos(angle)
            end_y = start_y + length * math.sin(angle)
            
            self.cracks.append(((start_x, start_y), (end_x, end_y)))
            
            # Redesenhar asteroide com rachaduras
            self.image = self.original_image.copy()
            for crack in self.cracks:
                pygame.draw.line(self.image, RED, crack[0], crack[1], 2)
            
    def update(self, dt):
        # Atualizar posição
        self.rect.y += self.speed_y * dt * 60
        self.rect.x += self.speed_x * dt * 60
        self.rotation += self.rotation_speed * dt * 60
        
        # Girar o asteroide
        rotated_image = pygame.transform.rotate(self.original_image, self.rotation)
        self.rect = rotated_image.get_rect(center=self.rect.center)
        self.image = rotated_image.copy()
        
        # Redesenhar rachaduras se houver
        if self.cracks:
            for crack in self.cracks:
                pygame.draw.line(self.image, RED, crack[0], crack[1], 2)
        
        # Remover se sair da tela
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()
            
    def hit(self, damage=1):
        self.health -= damage
        self.add_crack()
        if self.health <= 0:
            return True
        return False

class WaveManager:
    """Gerenciador de waves de asteroides"""
    def __init__(self):
        self.current_wave = 1
        self.asteroids_in_wave = 3  # REDUZIDO para começar com menos asteroides
        self.asteroids_spawned = 0
        self.wave_complete = False
        self.time_between_waves = 5.0  # AUMENTADO para dar mais tempo entre waves
        self.wave_timer = 0
        self.spawn_timer = 0  # Timer para controlar o spawn individual de asteroides
        self.spawn_delay = 0.5  # Tempo entre cada spawn de asteroide - REDUZIDO
        
    def start_new_wave(self):
        self.current_wave += 1
        self.asteroids_in_wave = 3 + self.current_wave  # Aumento mais gradual
        self.asteroids_spawned = 0
        self.wave_complete = False
        self.wave_timer = 0
        self.spawn_timer = 0
        
    def should_spawn_asteroid(self, dt):
        if self.wave_complete:
            self.wave_timer += dt
            if self.wave_timer >= self.time_between_waves:
                self.start_new_wave()
                return True
            return False
            
        # Controlar o spawn de asteroides individualmente
        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_delay and self.asteroids_spawned < self.asteroids_in_wave:
            self.spawn_timer = 0
            self.asteroids_spawned += 1
            if self.asteroids_spawned >= self.asteroids_in_wave:
                self.wave_complete = True
            return True
        return False
    
    def get_asteroid_size(self):
        # Determinar o tamanho do asteroide baseado na wave
        if self.current_wave <= 3:
            return 1  # Apenas pequenos
        elif self.current_wave <= 6:
            return random.choice([1, 2])  # Pequenos e médios
        else:
            return random.choice([1, 2, 3])  # Todos os tamanhos

class StarField:
    """Campo de estrelas"""
    def __init__(self):
        self.stars = []
        for _ in range(150):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            size = random.uniform(0.5, 2)
            speed = random.uniform(0.5, 2)
            brightness = random.randint(100, 255)
            color = random.choice([WHITE, CYAN, NEON_GREEN, HOT_PINK])
            self.stars.append([x, y, size, speed, brightness, color])
            
    def update(self):
        for star in self.stars:
            star[1] += star[3]
            if star[1] > SCREEN_HEIGHT:
                star[1] = 0
                star[0] = random.randint(0, SCREEN_WIDTH)
                    
    def draw(self, surface):
        for star in self.stars:
            color = (*star[5][:3], star[4])
            gfxdraw.filled_circle(surface, int(star[0]), int(star[1]), int(star[2]), color)

class HUD:
    """Interface HUD"""
    def __init__(self):
        self.font_small = pygame.font.Font(None, 24)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_large = pygame.font.Font(None, 48)
        
    def draw_health_bar(self, surface, x, y, width, height, health, max_health):
        # Fundo
        pygame.draw.rect(surface, DARK_BLUE, (x, y, width, height))
        pygame.draw.rect(surface, CYAN, (x, y, width, height), 2)
        
        # Saúde
        health_width = int(width * (health / max_health))
        health_color = NEON_GREEN if health > max_health * 0.5 else YELLOW if health > max_health * 0.25 else RED
        pygame.draw.rect(surface, health_color, (x, y, health_width, height))
        
        # Efeito de brilho
        glow_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(glow_surf, (*health_color, 50), (x-2, y-2, width+4, height+4), 2)
        surface.blit(glow_surf, (0, 0), special_flags=pygame.BLEND_ADD)
    
    def draw_text_with_glow(self, surface, text, font, x, y, color, center=False):
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        
        if center:
            text_rect.center = (x, y)
        else:
            text_rect.topleft = (x, y)
            
        # Desenha brilho
        glow_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        for i in range(3):
            glow_text = font.render(text, True, (*color, 50 - i*15))
            glow_rect = glow_text.get_rect(center=text_rect.center)
            glow_surf.blit(glow_text, glow_rect)
        surface.blit(glow_surf, (0, 0), special_flags=pygame.BLEND_ADD)
        
        # Desenha texto principal
        surface.blit(text_surface, text_rect)
    
    def draw(self, surface, score, lives, player_health=100, wave=1, weapon_type=WeaponType.BASIC, weapon_timer=0):
        # Pontuação
        self.draw_text_with_glow(surface, f"SCORE: {score}", self.font_medium, 60, 20, NEON_GREEN)
        
        # Wave
        self.draw_text_with_glow(surface, f"WAVE: {wave}", self.font_medium, SCREEN_WIDTH//2, 20, YELLOW)
        
        # Arma atual
        weapon_names = {
            WeaponType.BASIC: "BASIC",
            WeaponType.SPREAD: "SPREAD",
            WeaponType.RAPID: "RAPID",
            WeaponType.LASER_BEAM: "LASER",
            WeaponType.HOMING: "HOMING"
        }
        weapon_text = f"WEAPON: {weapon_names[weapon_type]}"
        if weapon_timer > 0:
            weapon_text += f" ({int(weapon_timer)}s)"
        self.draw_text_with_glow(surface, weapon_text, self.font_small, SCREEN_WIDTH - 150, 20, PURPLE)
        
        # Vidas
        for i in range(lives):
            x = SCREEN_WIDTH - 100 + i * 30
            y = 60
            pygame.draw.polygon(surface, ELECTRIC_BLUE, [(x, y), (x-10, y+20), (x+10, y+20)])
            pygame.draw.polygon(surface, CYAN, [(x, y), (x-10, y+20), (x+10, y+20)], 2)
        
        # Barra de saúde
        self.draw_health_bar(surface, 20, SCREEN_HEIGHT - 40, 200, 20, player_health, 100)
        self.draw_text_with_glow(surface, "SHIELD", self.font_small, 230, SCREEN_HEIGHT - 30, CYAN)

class Button:
    """Botão interativo"""
    def __init__(self, x, y, width, height, text, color, text_color=WHITE):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.hover_color = tuple(min(255, c + 50) for c in color)
        self.current_color = color
        self.font = pygame.font.Font(None, 36)
        self.hovered = False
        
    def update(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)
        self.current_color = self.hover_color if self.hovered else self.color
        
    def draw(self, surface):
        # Desenha o botão
        pygame.draw.rect(surface, self.current_color, self.rect)
        pygame.draw.rect(surface, WHITE, self.rect, 3)
        
        # Desenha o texto
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
        
        # Efeito de brilho quando hover
        if self.hovered:
            glow_surf = pygame.Surface((self.rect.width + 10, self.rect.height + 10), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (*WHITE, 50), (0, 0, self.rect.width + 10, self.rect.height + 10), 3)
            surface.blit(glow_surf, (self.rect.x - 5, self.rect.y - 5), special_flags=pygame.BLEND_ADD)
    
    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.hovered

def show_start_screen(screen, clock):
    """Tela inicial do jogo"""
    screen.fill(BLACK)
    
    # Título
    title_font = pygame.font.Font(None, 72)
    title_text = title_font.render("SPACE DEFENDER", True, CYAN)
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 150))
    screen.blit(title_text, title_rect)
    
    # Subtítulo
    subtitle_font = pygame.font.Font(None, 36)
    subtitle_text = subtitle_font.render("FUTURISTIC EDITION", True, ELECTRIC_BLUE)
    subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH//2, 220))
    screen.blit(subtitle_text, subtitle_rect)
    
    # Controles
    controls_font = pygame.font.Font(None, 28)
    controls = [
        "CONTROLES:",
        "← → : Mover a nave",
        "ESPAÇO : Atirar",
        "ENTER : Começar o jogo"
    ]
    
    y = 320
    for control in controls:
        control_text = controls_font.render(control, True, WHITE)
        control_rect = control_text.get_rect(center=(SCREEN_WIDTH//2, y))
        screen.blit(control_text, control_rect)
        y += 40
    
    # Instrução adicional
    instruction_font = pygame.font.Font(None, 24)
    instruction_text = instruction_font.render("Colete power-ups para mudar sua arma!", True, NEON_GREEN)
    instruction_rect = instruction_text.get_rect(center=(SCREEN_WIDTH//2, 500))
    screen.blit(instruction_text, instruction_rect)
    
    pygame.display.flip()
    
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_RETURN:
                    waiting = False
    return True

def show_game_over_screen(screen, clock, score, wave):
    """Tela de game over moderna"""
    screen.fill(BLACK)
    
    # Fundo com efeito de grade
    for x in range(0, SCREEN_WIDTH, 40):
        pygame.draw.line(screen, (20, 20, 30), (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, 40):
        pygame.draw.line(screen, (20, 20, 30), (0, y), (SCREEN_WIDTH, y))
    
    # Título Game Over
    title_font = pygame.font.Font(None, 72)
    title_text = title_font.render("GAME OVER", True, RED)
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 150))
    
    # Efeito de brilho
    glow_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    for i in range(5):
        glow_text = title_font.render("GAME OVER", True, (*RED, 50 - i*10))
        glow_rect = glow_text.get_rect(center=title_rect.center)
        glow_surf.blit(glow_text, glow_rect)
    screen.blit(glow_surf, (0, 0), special_flags=pygame.BLEND_ADD)
    screen.blit(title_text, title_rect)
    
    # Estatísticas
    stats_font = pygame.font.Font(None, 48)
    score_text = stats_font.render(f"SCORE: {score}", True, YELLOW)
    score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, 250))
    screen.blit(score_text, score_rect)
    
    wave_text = stats_font.render(f"WAVE: {wave}", True, CYAN)
    wave_rect = wave_text.get_rect(center=(SCREEN_WIDTH//2, 310))
    screen.blit(wave_text, wave_rect)
    
    # Botão de jogar novamente
    play_button = Button(SCREEN_WIDTH//2 - 150, 400, 300, 60, "PLAY AGAIN", NEON_GREEN)
    
    # Mensagem adicional
    msg_font = pygame.font.Font(None, 24)
    msg_text = msg_font.render("Clique no botão ou pressione ENTER", True, WHITE)
    msg_rect = msg_text.get_rect(center=(SCREEN_WIDTH//2, 500))
    screen.blit(msg_text, msg_rect)
    
    pygame.display.flip()
    
    waiting = True
    while waiting:
        clock.tick(FPS)
        mouse_pos = pygame.mouse.get_pos()
        play_button.update(mouse_pos)
        play_button.draw(screen)
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_RETURN:
                    waiting = False
            if play_button.is_clicked(event):
                waiting = False
                
    return True

# Testes unitários
class TestSpaceDefender(unittest.TestCase):
    def test_bullet_creation(self):
        """Testa se as balas são criadas corretamente"""
        bullet = Bullet(100, 100, WeaponType.BASIC)
        self.assertEqual(bullet.x, 100)
        self.assertEqual(bullet.y, 100)
        self.assertEqual(bullet.weapon_type, WeaponType.BASIC)
        self.assertTrue(bullet.active)
    
    def test_player_shoot_basic(self):
        """Testa se o jogador atira corretamente com a arma básica"""
        player = Player()
        bullets = []
        sound_manager = SoundManager()
        
        player.shoot(sound_manager, bullets)
        self.assertEqual(len(bullets), 1)
        self.assertEqual(bullets[0].weapon_type, WeaponType.BASIC)
    
    def test_player_shoot_spread(self):
        """Testa se o jogador atira corretamente com a arma spread"""
        player = Player()
        player.weapon_type = WeaponType.SPREAD
        bullets = []
        sound_manager = SoundManager()
        
        player.shoot(sound_manager, bullets)
        self.assertEqual(len(bullets), 3)  # Spread dispara 3 balas
        for bullet in bullets:
            self.assertEqual(bullet.weapon_type, WeaponType.SPREAD)
    
    def test_wave_manager(self):
        """Testa o gerenciador de waves"""
        wave_manager = WaveManager()
        
        # Testa a primeira wave
        self.assertEqual(wave_manager.current_wave, 1)
        self.assertEqual(wave_manager.asteroids_in_wave, 3)
        
        # Testa o spawn de asteroides com dt maior que o delay
        dt = 0.6  # Maior que o spawn_delay de 0.5
        should_spawn = wave_manager.should_spawn_asteroid(dt)
        self.assertTrue(should_spawn)
        
        # Testa se completa a wave
        for _ in range(3):
            wave_manager.should_spawn_asteroid(dt)
        
        # Após completar, não deve spawnar mais asteroides imediatamente
        should_spawn = wave_manager.should_spawn_asteroid(dt)
        self.assertFalse(should_spawn)
    
    def test_asteroid_health(self):
        """Testa a saúde dos asteroides"""
        asteroid = Asteroid(1)  # Asteroide pequeno
        self.assertEqual(asteroid.health, 1)
        self.assertEqual(asteroid.max_health, 1)
        
        # Testa dano
        destroyed = asteroid.hit(1)
        self.assertTrue(destroyed)
        
        # Testa asteroide médio
        asteroid = Asteroid(2)
        self.assertEqual(asteroid.health, 2)
        
        destroyed = asteroid.hit(1)
        self.assertFalse(destroyed)
        self.assertEqual(asteroid.health, 1)

def main():
    # Configuração da tela
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Space Defender - Futuristic Edition")
    clock = pygame.time.Clock()
    
    # Gerenciador de som
    sound_manager = SoundManager()
    
    # Efeitos visuais
    starfield = StarField()
    particle_system = ParticleSystem(500)
    hud = HUD()
    
    # Grupos de sprites
    all_sprites = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    powerups = pygame.sprite.Group()
    
    # Lista de balas - MOVIDA PARA FORA DO LOOP
    bullets = []
    
    # Variáveis do jogo
    running = True
    game_over = False
    score = 0
    player_health = 100
    
    # Mostrar tela inicial
    if not show_start_screen(screen, clock):
        return
    
    # Criar jogador
    player = Player()
    all_sprites.add(player)
    
    # Gerenciador de waves
    wave_manager = WaveManager()
    
    # Variáveis de spawn
    powerup_spawn_timer = 0
    
    # Loop principal do jogo
    while running:
        # Delta time
        dt = clock.tick(FPS) / 1000.0
        
        # Processar eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.shoot(sound_manager, bullets)
        
        # Spawn de asteroides baseado em waves
        if wave_manager.should_spawn_asteroid(dt):
            size = wave_manager.get_asteroid_size()
            asteroid = Asteroid(size)
            all_sprites.add(asteroid)
            asteroids.add(asteroid)
        
        # Spawn de power-ups
        powerup_spawn_timer += dt
        if powerup_spawn_timer > 15.0:  # AUMENTADO para 15 segundos
            powerup_spawn_timer = 0
            weapon_type = random.choice(list(WeaponType))
            powerup = PowerUp(random.randint(50, SCREEN_WIDTH-50), -40, weapon_type)
            all_sprites.add(powerup)
            powerups.add(powerup)
        
        # Atualizar
        all_sprites.update(dt)
        starfield.update()
        particle_system.update(dt)
        player.trail.update()
        
        # Atualizar balas
        for bullet in bullets[:]:
            bullet.update(asteroids)
            if not bullet.active:
                bullets.remove(bullet)
        
        # Verificar colisões - balas com asteroides
        for bullet in bullets[:]:
            bullet_rect = bullet.get_rect()
            for asteroid in asteroids:
                if bullet_rect.colliderect(asteroid.rect):
                    if asteroid.hit(bullet.damage):
                        score += 20 if asteroid.energy_core else 10
                        sound_manager.play('explosion')
                        
                        # Explosão
                        particle_system.emit(
                            asteroid.rect.centerx, 
                            asteroid.rect.centery, 
                            YELLOW if asteroid.energy_core else ORANGE, 
                            count=40 if asteroid.energy_core else 30
                        )
                        asteroid.kill()
                    else:
                        particle_system.emit(
                            asteroid.rect.centerx, 
                            asteroid.rect.centery, 
                            CYAN, 
                            count=15
                        )
                    if bullet in bullets:
                        bullets.remove(bullet)
                    break
        
        # Verificar colisões - jogador com asteroides
        if player.invulnerable <= 0:
            hits = pygame.sprite.spritecollide(player, asteroids, True, pygame.sprite.collide_circle_ratio(0.7))
            for hit in hits:
                player.lives -= 1
                player.invulnerable = 2.0
                player_health = max(0, player_health - 25)
                
                particle_system.emit(
                    player.rect.centerx, 
                    player.rect.centery, 
                    RED, 
                    count=40
                )
                
                if player.lives <= 0 or player_health <= 0:
                    game_over = True
        else:
            # Recuperar saúde lentamente
            player_health = min(100, player_health + dt * 5)
        
        # Verificar colisões - jogador com power-ups
        powerup_hits = pygame.sprite.spritecollide(player, powerups, True)
        for powerup in powerup_hits:
            player.change_weapon(powerup.weapon_type)
            sound_manager.play('powerup')
            particle_system.emit(
                powerup.rect.centerx,
                powerup.rect.centery,
                powerup.colors[powerup.weapon_type],
                count=30
            )
        
        # Desenhar
        screen.fill(BLACK)
        starfield.draw(screen)
        
        # Desenhar rastro da nave
        player.trail.draw(screen)
        
        # Desenhar sprites
        all_sprites.draw(screen)
        
        # Desenhar balas
        for bullet in bullets:
            bullet.draw(screen)
        
        # Desenhar partículas
        particle_system.draw(screen)
        
        # Desenhar escudo
        player.draw_shield(screen)
        
        # Desenhar HUD
        hud.draw(screen, score, player.lives, player_health, 
                wave_manager.current_wave, player.weapon_type, player.weapon_timer)
        
        # Efeito de piscar quando invulnerável
        if player.invulnerable > 0 and int(player.invulnerable * 10) % 2:
            player.image.set_alpha(128)
        else:
            player.image.set_alpha(255)
        
        pygame.display.flip()
        
        # Verificar game over
        if game_over:
            if not show_game_over_screen(screen, clock, score, wave_manager.current_wave):
                running = False
            game_over = False
            score = 0
            player_health = 100
            
            # Resetar jogo
            all_sprites.empty()
            asteroids.empty()
            powerups.empty()
            particle_system.particles.clear()
            bullets.clear()  # Limpar a lista de balas
            
            player = Player()
            all_sprites.add(player)
            wave_manager = WaveManager()
            powerup_spawn_timer = 0

    pygame.quit()

# Executar testes se o arquivo for executado diretamente
if __name__ == "__main__":
    # Executar testes
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
    
    # Executar jogo
    main()