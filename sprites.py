import pygame
import random
import math
import time
# Player 1 and 2 classes should probably just subclass a main
# player class

# class for player 1
class Player(pygame.sprite.Sprite):
    def __init__(self, settings, canon_colour, left_side):
        super(Player, self).__init__()
        self.sprite_dim_x = 13
        self.sprite_dim_y = 7
        self.surf = pygame.Surface((self.sprite_dim_x,
                                    self.sprite_dim_y))
        self.surf.fill((200, 200, 200))
        self.rect = self.surf.get_rect()
        self.canon = pygame.Surface((3,3))
        self.canon.fill(canon_colour)
        if left_side:
            self.x = random.randint(settings['XPlayDomain'][0],
                                    int(settings['XPlayDomain'][1]/3)-self.sprite_dim_x)
            self.y = random.randint(settings['YPlayDomain'][0]+30,
                                    settings['YPlayDomain'][1]-self.sprite_dim_y)
            self.rect.topleft = (self.x, self.y)
            #30 offset prevents player sprites overlapping with input UI
            self.canon_x = self.x+8 
            self.canon_y = self.y+2
            self.angle_text = '000.0000'
            self.velocity_text = '5.0000'
            self.angle = 0.0
            self.velocity = 5.0
            self.name = settings['Player1Name']
        else:
            self.x = random.randint(int((settings['XPlayDomain'][1]/3)*2),
                                settings['XPlayDomain'][1]-self.sprite_dim_x)
            self.y = random.randint(settings['YPlayDomain'][0]+30,
                                    settings['YPlayDomain'][1]-self.sprite_dim_y)
            self.rect.topleft = (self.x, self.y)
            self.canon_x = self.x+2
            self.canon_y = self.y+2
            self.angle_text = '180.0000'
            self.velocity_text = '5.0000'
            self.angle = 180.0
            self.velocity = 5.0
            self.name = settings['Player2Name']

# class for planets
class Planet(pygame.sprite.Sprite):
    def __init__(self, settings):
        super(Planet, self).__init__()
        self.density = math.floor((random.random() * 3) + 2) / 3
        # planet type
        # 1. Small rocky 1/8
        # 2. Rocky/earth-like 3/8
        # 3. Gas Giant 1/8
        # 4. Gas giant with ring 1/8
        # 5. Neptune like 1/8
        # 6. Neptune like with ring 1/8
        # 7. Black hole 1/24
        planet_types = (1, 2, 3, 4, 5, 6)
        self.planet_type = random.choices(planet_types,
                                          (1/8, 3/8, 1/8, 1/8,
                                           1/8, 1/8), k=1)[0]
        if settings['Blackholes']:
            planet_types = (1, 2, 3, 4, 5, 6, 7)
            self.planet_type = random.choices(planet_types,
                                          (3/24, 9/24, 3/24, 3/24,
                                           2/24, 3/24, 1/24), k=1)[0]
        
        self.planet_colour = (200, 200, 200)
        
        # 15 to 85
        self.radius = random.randint(0, 3) + 10
        if self.planet_type == 2:
            self.density = math.floor((random.random() * 3) + 2) / 4
            self.planet_colour = random.choice(((225, 115, 60),(130, 225, 125),(125, 180, 220)))
            self.radius = random.randint(13, 23)
        if self.planet_type == 3:
            self.density = math.floor((random.random() * 3) + 2) / 6
            self.planet_colour = (225, 180, 70)
            self.radius = random.randint(31, 43)
        if self.planet_type == 4:
            self.density = math.floor((random.random() * 3) + 2) / 6
            self.planet_colour = (225, 180, 70)
            self.radius = random.randint(31, 43)
        if self.planet_type == 5:
            self.density = math.floor((random.random() * 3) + 2) / 5
            self.planet_colour = random.choice(((155, 190, 155),(155,155,190)))
            self.radius = random.randint(23, 30)
        if self.planet_type == 6:
            self.density = math.floor((random.random() * 3) + 2) / 5
            self.planet_colour = random.choice(((155, 190, 155),(155,155,190)))
            self.radius = random.randint(23, 30)
        if self.planet_type == 7:
            self.density = math.floor((random.random() * 3) + 2) / 2
            self.planet_colour = (0,0,0)
            self.radius = random.randint(11, 43)
        
        self.mass = settings['G'] * 2 * math.pi * self.radius**2 * self.density
        self.x = random.randint(settings['XPlayDomain'][0]+self.radius,
                                settings['XPlayDomain'][1]-self.radius)
        self.y = random.randint(settings['YPlayDomain'][0]+self.radius,
                                settings['YPlayDomain'][1]-self.radius)
        self.image = pygame.Surface((self.radius*2+1, self.radius*2+1), pygame.SRCALPHA)
        pygame.gfxdraw.circle(self.image,
                                self.radius,
                                self.radius,
                                self.radius, self.planet_colour)
        pygame.gfxdraw.filled_circle(self.image,
                                     self.radius,
                                     self.radius,
                                     self.radius, self.planet_colour)
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.x, self.y)
        
# class for Missiles
class Missile(pygame.sprite.Sprite):
    def __init__(self, player, trail_colour, MISSILE_PUTTERING,
                 BLACKHOLE_STRIKE, PLANET_STRIKE, MISSILE_FADE):
        super(Missile, self).__init__() #
        # missile should start at the centre of the canon
        self.audio_ctl = True
        self.MISSILE_PUTTERING = MISSILE_PUTTERING
        self.BLACKHOLE_STRIKE = BLACKHOLE_STRIKE
        self.PLANET_STRIKE = PLANET_STRIKE
        self.MISSILE_FADE = MISSILE_FADE
        self.x = player.canon_x+2
        self.y = player.canon_y+1
        self.ar = math.pi * (90 - player.angle) / 180
        self.velocity_y = math.cos(self.ar) * -player.velocity / 5
        self.velocity_x = math.sin(self.ar) * player.velocity / 5
        self.surf = pygame.Surface((1, 1))
        self.surf.fill(trail_colour)
        self.rect = self.surf.get_rect()
        self.time_step = 1
        self.missile_start_time = None
        self.message = ''

    def set_starting_location(self, player):
        overlap = True
        while True:
            self.x += self.velocity_x
            self.y += self.velocity_y
            if self.x < player.rect.topleft[0]-3 or self.x > player.rect.topright[0]+3:
                overlap = False
            if self.y < player.rect.topleft[1]-3 or self.y > player.rect.bottomright[1]+3:
                overlap = False
            if not overlap:
                break

    def __distance(self, x, y):
        return math.sqrt(x**2 + y**2)
 
    def __calculateForces(self, planets):
        forces = {'x': 0,
                  'y': 0,
                  'l': 0}
        for planet in planets:
            #first get the distance from my missile and this planet
            dx = self.x - planet.x-planet.radius
            dy = self.y - planet.y-planet.radius
            phys_dist = self.__distance(dx,dy)
            k = 1/((phys_dist**2) * phys_dist)
            forces['x'] = forces['x'] - planet.mass * dx * k 
            forces['y'] = forces['y'] - planet.mass * dy * k
            forces['l'] = self.__distance(forces['x'], forces['y'])  
        return forces

    def check_bounds(self, settings):
        if self.x < settings['XSolarSystemDomain'][0]:
            return False
        if self.x > settings['XSolarSystemDomain'][1]:
            return False
        if self.y < settings['YSolarSystemDomain'][0]:
            return False
        if self.y > settings['YSolarSystemDomain'][1]:
            return False
        return True

    def update_location(self, planets):
        self.x += self.velocity_x * self.time_step
        self.y += self.velocity_y * self.time_step
        forces = self.__calculateForces(planets)
        self.velocity_x += forces['x'] * self.time_step
        self.velocity_y += forces['y'] * self.time_step
        self.x += self.velocity_x
        self.y += self.velocity_y * self.time_step
        self.rect.x = self.x
        self.rect.y = self.y
        # position_history['x'].append(missile['x'])
        # position_history['y'].append(missile['y'])

    def fire_missile(self, screen, physics_planets, collision_planets, settings, player):
        self.update_location(physics_planets)
        screen.blit(self.surf, self.rect)
        pygame.display.update()
        missile_done = False
        collisions = pygame.sprite.spritecollide(self, collision_planets, 
                                                 False, pygame.sprite.collide_circle)
        if collisions:
            sprite_type = "planet"
            if collisions[0].planet_type == 7:
                #if we strike a black hole we add to its mass, as a function of
                # the missile velocity
                collisions[0].mass = collisions[0].mass+(player.velocity*4)
                if collisions[0].mass > settings['MaxMass']:
                    collisions[0].mass = settings['MaxMass']
                sprite_type = "black hole"
                if self.audio_ctl:
                    pygame.event.post(pygame.event.Event(self.BLACKHOLE_STRIKE))
                    self.audio_ctl = False
            else:
                if self.audio_ctl:
                    pygame.event.post(pygame.event.Event(self.PLANET_STRIKE))
                    self.audio_ctl = False 
            self.message = f"{player.name}'s missile hit a {sprite_type}"
            missile_done = True

        flight_time = time.time() - self.missile_start_time
        if flight_time*1000 >= (settings['MissileMaxFlightTime']*1000)-1500:
            if self.audio_ctl:
                pygame.event.post(pygame.event.Event(self.MISSILE_PUTTERING))
                self.audio_ctl = False
        if flight_time > settings['MissileMaxFlightTime']:
            self.message = f"{player.name}'s missile ran out of fuel"
            missile_done = True
        if not self.check_bounds(settings):
            if self.audio_ctl:
                pygame.event.post(pygame.event.Event(self.MISSILE_FADE))
                self.audio_ctl = False 
            self.message = f"{player.name}'s missile left solar system"
            missile_done = True
        return missile_done
