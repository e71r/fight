import pygame as pg
import random
import pygame_menu

pg.init()

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 550

CHARACTER_WIDTH = 300
CHARACTER_HEIGHT = 375

FPS = 60

font = pg.font.Font(None, 40)


def load_image(file, width, height):
    image = pg.image.load(file).convert_alpha()
    image = pg.transform.scale(image, (width, height))
    return image


def text_render(text):
    return font.render(str(text), True, "black")

class FireBall(pg.sprite.Sprite):
    def __init__(self, coord, side, power):
        super().__init__()

        self.coord = coord
        self.side = side
        self.power = power

        self.image = load_image("images/fire wizard/magicball.png", 200, 150)
        if self.side == "right":
            self.image = pg.transform.flip(self.image, True, False)
        self.rect = self.image.get_rect(center = (self.coord[0], self.coord[1] + 120))
        

    def update(self):

        if self.side == "right":
            self.rect.x += 4
        elif self.side == "left":
            self.rect.x -= 4

        if self.rect.x >= SCREEN_WIDTH or self.rect.x <= 0:
            self.kill()




class Enemy(pg.sprite.Sprite):
    def __init__(self, folder):
        super().__init__()
        
        self.folder = folder
        self.load_animations()
        self.image = self.idle_animation_right[0]
        self.current = 0
        self.animation = self.idle_animation_left

        self.rect = self.image.get_rect()
        self.rect.center = (700, SCREEN_HEIGHT // 2)

        self.timer = pg.time.get_ticks()
        self.interval = 300
        self.side = "left"
        self.animation_mode = True
        self.direction = 0 

        self.hp = 200

        self.charge_power = 0
        self.charge_indicator = pg.Surface((self.charge_power, 10))
        self.charge_indicator.fill("red")

        self.is_moving = False
        self.move_duration = 0
        self.direction = 0
        self.move_timer = pg.time.get_ticks()

        self.attack_percent = 1

        self.charge_mode = False
        self.attack_interval = 1000
        self.move_interval = 1000
        self.magic_balls = pg.sprite.Group()
        self.animation_mode = False
        self.attack_mode = False
        self.attack_timer = pg.time.get_ticks()

        

    def load_animations(self):

        self.idle_animation_right = [load_image(f"images/{self.folder}/idle{i}.png", CHARACTER_WIDTH, CHARACTER_HEIGHT) for i in range(1,4)]
        self.move_animation_right = [load_image(f"images/{self.folder}/move{i}.png", CHARACTER_WIDTH, CHARACTER_HEIGHT) for i in range(1,4)]
        self.move_animation_left = [pg.transform.flip(image, True, False) for image in self.move_animation_right]
        self.idle_animation_left = [pg.transform.flip(image, True, False) for image in self.idle_animation_right]

        self.charge = [load_image(f"images/{self.folder}/charge.png", CHARACTER_WIDTH, CHARACTER_HEIGHT)]
        self.attack = [load_image(f"images/{self.folder}/attack.png", CHARACTER_WIDTH, CHARACTER_HEIGHT)]

        self.charge.append(pg.transform.flip(self.charge[0], True, False))
        self.attack.append(pg.transform.flip(self.attack[0], True, False))

    def update(self, player):
        keys = pg.key.get_pressed()
        self.handle_animation()
        self.handle_movement(player)
        self.handle_attack_mode(player)
        
    

    def handle_attack_mode(self, player):
        rand = random.randint(0,100)

        if len(self.magic_balls.sprites()) == 0:
            if self.charge_mode:
                if self.attack_percent != 50:
                    self.attack_percent += 1
                else:
                    self.attack_percent = 1

            if self.attack_percent > rand and self.charge_mode == False and self.is_moving == False:
                if player.rect.x >= self.rect.x:
                    self.side = "right"
                elif player.rect.x <= self.rect.x:
                    self.side = "left"

                self.animation = self.move_animation_left if self.side == "left" else self.move_animation_left

                self.charge_mode = True
                self.animation_mode = True
                self.is_moving = True
                self.charge_power = random.randint(1,100)
                self.attack_timer = pg.time.get_ticks()
            
        


    def handle_animation(self):
        if self.attack_mode:
            self.animation = self.idle_animation_left if self.side == "left" else self.idle_animation_right
        if self.animation_mode:
            if pg.time.get_ticks() - self.timer > self.interval:
                self.current += 1
                if self.current >= len(self.animation):
                    self.current = 0
                self.image = self.animation[self.current]
                self.timer = pg.time.get_ticks()

        

        if self.attack_mode and not self.is_moving:
            fireball_position = self.rect.topright if self.side == "right" else self.rect.topleft
            self.magic_balls.add(FireBall(fireball_position, self.side, self.charge_power))
            self.charge_power = 0
            self.image = self.attack[self.side != "right"]
            self.animation_mode = True
            self.animation = self.idle_animation_right if self.side == "right" else self.idle_animation_left
            self.timer = pg.time.get_ticks()
            self.attack_mode = False

        if self.charge_mode:
            if pg.time.get_ticks() - self.attack_timer >= self.attack_interval:
                self.charge_mode = False; self.attack_mode = True
                self.is_moving = False; self.animation_mode = False

    


    def handle_movement(self, player):

    
        
        if len(player.fireballs.sprites()) != 0 and not self.is_moving:
            sp = player.fireballs.sprites()[0]

            #if self.rect.x <= 0+self.rect.size[0] or self.rect.x >= SCREEN_WIDTH-self.rect.size[0]:
            #    return

            if sp.side == "right":
                if not self.rect.x <= 0+self.rect.size[0]:
                    self.is_moving = True
                    self.animation_mode = True
                    self.side = sp.side
                    self.animation = self.move_animation_right
                    self.move_timer = pg.time.get_ticks()
            elif sp.side == "left":
                if not self.rect.x >= SCREEN_WIDTH-self.rect.size[0]:
                    self.is_moving = True
                    self.animation_mode = True
                    self.side == sp.side
                    self.animation = self.move_animation_left
                    self.move_timer = pg.time.get_ticks()


            

        if self.is_moving:
            if self.side == "right":
                self.rect.x += 1
            else:
                self.rect.x -= 1

        if self.rect.right >= SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
            self.is_moving = False
        elif self.rect.left <= 0:
            self.rect.left = 0
            self.is_moving = False



class Player(pg.sprite.Sprite):
    def __init__(self, texture = None):
        super().__init__()


        if texture != None:
            if texture == 1:
                self.texture = "lightning wizard"
            elif texture == 2:
                self.texture = "earth monk"
            else:
                self.texture = "fire wizard"
        else:
            self.texture = "fire wizard"

        self.load_animations()
        self.image = self.idle_animation_right[0]
        self.current = 0
        self.animation = self.idle_animation_right

        self.rect = self.image.get_rect()
        self.rect.center = (100, SCREEN_HEIGHT // 2)

        self.timer = pg.time.get_ticks()
        self.interval = 300
        self.side = "right"
        self.animation_mode = True
        self.direction = 0 

        self.hp = 200

        self.charge_power = 0
        self.charge_indicator = pg.Surface((self.charge_power, 10))
        self.charge_indicator.fill("red")

        self.charge_mode = False
        self.attack_mode = False
        self.attack_interval = 500
        self.fireballs = pg.sprite.Group()
        self.down_mode = False

    def load_animations(self):

        self.idle_animation_right = [load_image(f"images/{self.texture}/idle{i}.png", CHARACTER_WIDTH, CHARACTER_HEIGHT) for i in range(1,4)]
        self.move_animation_right = [load_image(f"images/{self.texture}/move{i}.png", CHARACTER_WIDTH, CHARACTER_HEIGHT) for i in range(1,4)]
        self.move_animation_left = [pg.transform.flip(image, True, False) for image in self.move_animation_right]
        self.idle_animation_left = [pg.transform.flip(image, True, False) for image in self.idle_animation_right]

        self.charge = [load_image(f"images/{self.texture}/charge.png", CHARACTER_WIDTH, CHARACTER_HEIGHT)]
        self.attack = [load_image(f"images/{self.texture}/attack.png", CHARACTER_WIDTH, CHARACTER_HEIGHT)]
        self.down = [load_image(f"images/{self.texture}/down.png", CHARACTER_WIDTH, CHARACTER_HEIGHT)]

        self.charge.append(pg.transform.flip(self.charge[0], True, False))
        self.attack.append(pg.transform.flip(self.attack[0], True, False))
        self.down.append(pg.transform.flip(self.down[0], True, False))

    def update(self):

        keys = pg.key.get_pressed()

        self.direction = 0

        if keys[pg.K_a]:
            self.direction = -1
            self.side = "left"
        if keys[pg.K_d]:
            self.direction = 1
            self.side = "right"
        


        self.handle_animation()
        self.handle_movement(self.direction, keys)
        self.handle_attack_mode()
        

    def handle_attack_mode(self):
        if self.attack_mode:
            if pg.time.get_ticks() - self.timer > self.attack_interval:
                self.attack_mode = False
                self.timer = pg.time.get_ticks()

    def handle_animation(self):
        if not self.charge_mode and self.charge_power > 0:
            self.attack_mode = True
        if self.animation_mode and not self.attack_mode:
            if pg.time.get_ticks() - self.timer > self.interval:
                self.current += 1
                if self.current >= len(self.animation):
                    self.current = 0
                self.image = self.animation[self.current]
                self.timer = pg.time.get_ticks()

        if self.charge_mode:
            self.charge_power += 1
            self.charge_indicator = pg.Surface((self.charge_power, 10))
            self.charge_indicator.fill("red")
            if self.charge_power >= 100:
                self.attack_mode = True

        if self.attack_mode and self.charge_power > 0:
            fireball_position = self.rect.topright if self.side == "right" else self.rect.topleft
            self.fireballs.add(FireBall(fireball_position, self.side, self.charge_power))
            self.charge_power = 0
            self.charge_mode = False
            self.image = self.attack[self.side != "right"]
            self.timer = pg.time.get_ticks()



        #else:
            #if self.charge_power != 0:
            #    self.charge_power = 0

    def handle_movement(self, direction, keys):
        if self.attack_mode:
            return
        
        if self.down_mode == True and self.animation != self.down:
            self.down_mode = False
        
        if keys[pg.K_s]:
            self.animation_mode = False
            self.charge_mode = False
            self.down_mode = True
            self.image = self.down[self.side != "right"]
            return
                
        if direction != 0:
            self.animation_mode = True
            self.charge_mode = False
            self.rect.x += direction
            self.animation = self.move_animation_left if direction == -1 else self.move_animation_right
        elif keys[pg.K_SPACE]:
            if len(self.fireballs.sprites()) == 0:
                self.animation_mode = False
                self.image = self.charge[self.side != "right"]
                self.charge_mode = True
        else:
            self.animation_mode = True
            self.charge_mode = False
            self.animation = self.idle_animation_left if self.side == "left" else self.idle_animation_right

        if self.rect.right >= SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        elif self.rect.left <= 0:
            self.rect.left = 0

        

            
class Player2:
    def __init__(self, texture = None):
        super().__init__()

        if texture != None:
            if texture == 1:
                self.texture = "lightning wizard"
            elif texture == 2:
                self.texture = "earth monk"
            else:
                self.texture = "fire wizard"
        else:
            self.texture = "fire wizard"

        self.load_animations()
        self.image = self.idle_animation_right[0]
        self.current = 0
        self.animation = self.idle_animation_left

        self.rect = self.image.get_rect()
        self.rect.center = (700, SCREEN_HEIGHT // 2)

        self.timer = pg.time.get_ticks()
        self.interval = 300
        self.side = "left"
        self.animation_mode = True
        self.direction = 0 

        self.hp = 200

        self.charge_power = 0
        self.charge_indicator = pg.Surface((self.charge_power, 10))
        self.charge_indicator.fill("red")

        self.charge_mode = False
        self.attack_mode = False
        self.attack_interval = 500
        self.fireballs = pg.sprite.Group()
        self.down_mode = False

    def load_animations(self):

        self.idle_animation_right = [load_image(f"images/{self.texture}/idle{i}.png", CHARACTER_WIDTH, CHARACTER_HEIGHT) for i in range(1,4)]
        self.move_animation_right = [load_image(f"images/{self.texture}/move{i}.png", CHARACTER_WIDTH, CHARACTER_HEIGHT) for i in range(1,4)]
        self.move_animation_left = [pg.transform.flip(image, True, False) for image in self.move_animation_right]
        self.idle_animation_left = [pg.transform.flip(image, True, False) for image in self.idle_animation_right]

        self.charge = [load_image(f"images/{self.texture}/charge.png", CHARACTER_WIDTH, CHARACTER_HEIGHT)]
        self.attack = [load_image(f"images/{self.texture}/attack.png", CHARACTER_WIDTH, CHARACTER_HEIGHT)]
        self.down = [load_image(f"images/{self.texture}/down.png", CHARACTER_WIDTH, CHARACTER_HEIGHT)]

        self.charge.append(pg.transform.flip(self.charge[0], True, False))
        self.attack.append(pg.transform.flip(self.attack[0], True, False))
        self.down.append(pg.transform.flip(self.down[0], True, False))

    def update(self):

        keys = pg.key.get_pressed()

        self.direction = 0

        if keys[pg.K_LEFT]:
            self.direction = -1
            self.side = "left"
        if keys[pg.K_RIGHT]:
            self.direction = 1
            self.side = "right"
        


        self.handle_animation()
        self.handle_movement(self.direction, keys)
        self.handle_attack_mode()
        

    def handle_attack_mode(self):
        if self.attack_mode:
            if pg.time.get_ticks() - self.timer > self.attack_interval:
                self.attack_mode = False
                self.timer = pg.time.get_ticks()

    def handle_animation(self):
        if not self.charge_mode and self.charge_power > 0:
            self.attack_mode = True
        if self.animation_mode and not self.attack_mode:
            if pg.time.get_ticks() - self.timer > self.interval:
                self.current += 1
                if self.current >= len(self.animation):
                    self.current = 0
                self.image = self.animation[self.current]
                self.timer = pg.time.get_ticks()

        if self.charge_mode:
            self.charge_power += 1
            self.charge_indicator = pg.Surface((self.charge_power, 10))
            self.charge_indicator.fill("red")
            if self.charge_power >= 100:
                self.attack_mode = True

        if self.attack_mode and self.charge_power > 0:
            fireball_position = self.rect.topright if self.side == "right" else self.rect.topleft
            self.fireballs.add(FireBall(fireball_position, self.side, self.charge_power))
            self.charge_power = 0
            self.charge_mode = False
            self.image = self.attack[self.side != "right"]
            self.timer = pg.time.get_ticks()



        #else:
            #if self.charge_power != 0:
            #    self.charge_power = 0

    def handle_movement(self, direction, keys):
        if self.attack_mode:
            return
        
        if self.down_mode == True and self.animation != self.down:
            self.down_mode = False
        
        if keys[pg.K_DOWN]:
            self.animation_mode = False
            self.charge_mode = False
            self.down_mode = True
            self.image = self.down[self.side != "right"]
            return
                
        if direction != 0:
            self.animation_mode = True
            self.charge_mode = False
            self.rect.x += direction
            self.animation = self.move_animation_left if direction == -1 else self.move_animation_right
        elif keys[pg.K_UP]:
            if len(self.fireballs.sprites()) == 0:
                self.animation_mode = False
                self.image = self.charge[self.side != "right"]
                self.charge_mode = True
        else:
            self.animation_mode = True
            self.charge_mode = False
            self.animation = self.idle_animation_left if self.side == "left" else self.idle_animation_right

        if self.rect.right >= SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        elif self.rect.left <= 0:
            self.rect.left = 0
        


class Game:
    def __init__(self, enemy, oneplayer = False, fp = None, sp = None):

        # Создание окна
        self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pg.display.set_caption("Битва магов")
        
        if enemy != None and oneplayer == False:
            self.player = Player()
            if enemy == 1:
                self.enemy = Enemy("lightning wizard")
            elif enemy == 2:
                self.enemy = Enemy("earth monk")
            else:
                self.enemy = Enemy("lightning wizard" if random.randint(1,2) == 1 else "earth monk")

        else:
            self.player2 = Player2(fp)
            self.player = Player(sp)
            self.enemy = None

        
        self.background = load_image("images/background.png", SCREEN_WIDTH, SCREEN_HEIGHT)

        self.clock = pg.time.Clock()

        self.gesture = None

        self.is_running = True
        

        self.win = None
        self.run()

    def run(self):
        while self.is_running:
            self.event()
            self.update()
            self.draw()
            self.clock.tick(FPS)

    def event(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                Menu()
            if self.win != None:
                if event.type == pg.KEYDOWN:
                    self.is_running = False
                    Menu()

            

    def update(self):
        if self.win is None:
            self.player.update()
            if self.enemy != None:
                self.enemy.update(self.player)
                self.enemy.magic_balls.update()
                hitse = pg.sprite.spritecollide(self.enemy, self.player.fireballs, True, pg.sprite.collide_rect_ratio(0.3))
                for hit in hitse:
                    self.enemy.hp -= hit.power

            else:
                self.player2.update()
                self.player2.fireballs.update()
                hitse = pg.sprite.spritecollide(self.player2, self.player.fireballs, True, pg.sprite.collide_rect_ratio(0.3))
                if not self.player2.down_mode:
                    for hit in hitse:
                        self.player2.hp -= hit.power
            self.player.fireballs.update()

            

            hitsp = pg.sprite.spritecollide(self.player, self.enemy.magic_balls if self.enemy else self.player2.fireballs, True, pg.sprite.collide_rect_ratio(0.3))
            if self.player.down_mode != True:
                for hit in hitsp:
                    self.player.hp -= hit.power

            if self.enemy:
                if self.enemy.hp <= 0:
                    self.win = self.player
                elif self.player.hp <= 0:
                    self.win = self.enemy

            else:
                if self.player2.hp <= 0:
                    self.win = self.player
                elif self.player.hp <= 0:
                    self.win = self.player2



        

    def draw(self):
        # Отрисовка интерфейса
        self.screen.blit(self.background, (0, 0))
        self.screen.blit(self.player.image, self.player.rect)
        if self.enemy:
            self.screen.blit(self.enemy.image, self.enemy.rect)
            pg.draw.rect(self.screen, (0,255,0), (SCREEN_WIDTH-250,20,self.enemy.hp,20))
            self.enemy.magic_balls.draw(self.screen)
            pg.draw.rect(self.screen, (0,0,0), (SCREEN_WIDTH-250,20,200,20), 2)
        else:
            self.screen.blit(self.player2.image, self.player2.rect)
            pg.draw.rect(self.screen, (0,255,0), (SCREEN_WIDTH-250,20,self.player2.hp,20))
            self.player2.fireballs.draw(self.screen)
            pg.draw.rect(self.screen, (0,0,0), (SCREEN_WIDTH-250,20,200,20), 2)

            if self.player2.charge_mode:
                self.screen.blit(self.player2.charge_indicator, (self.player2.rect.x + 120, self.player2.rect.top))    

        pg.draw.rect(self.screen, (0,255,0), (20,20,self.player.hp,20))

        pg.draw.rect(self.screen, (0,0,0), (20,20,200,20), 2)

        if self.player.charge_mode:
            self.screen.blit(self.player.charge_indicator, (self.player.rect.x + 120, self.player.rect.top))
        self.player.fireballs.draw(self.screen)

        if self.win == self.player:
            text = text_render("ПОБЕДА")
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(text, text_rect)
            text2 = text_render("Левый игрок выиграл.")
            text_rect2 = text2.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2-90))
            self.screen.blit(text2, text_rect2)
        
        if self.enemy != None:
            if self.win == self.enemy:
                text = text_render("ПОБЕДА")
                text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                self.screen.blit(text, text_rect)
                text2 = text_render("NPC Выиграл.")
                text_rect2 = text2.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2-90))
                self.screen.blit(text2, text_rect2)
        else:

            if self.win == self.player2:
                text = text_render("ПОБЕДА")
                text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                self.screen.blit(text, text_rect)
                text2 = text_render("Правый игрок выиграл.")
                text_rect2 = text2.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2-90))
                self.screen.blit(text2, text_rect2)


        pg.display.flip()

class Menu:
    def __init__(self):
        self.surface = pg.display.set_mode((900,550))
        self.menu = pygame_menu.Menu(
            height = 550,
            width = 900,
            theme = pygame_menu.themes.THEME_GREEN,
            title = "Меню"
        )
        self.enemy = 1
        self.left_player = 1
        self.right_player = 2
        
        self.menu.add.label("Режим на одного")
        self.menu.add.selector("Противник: ", [("Маг молний", 1), ("Маг земли", 2), ("Случайным образом", 3)], onchange=self.set_enemy)

        self.menu.add.button("Играть", self.start_one_player_game)
        
        self.menu.add.label("---------")

        self.menu.add.label("Режим на двоих")
        self.menu.add.selector("Левый игрок: ", [("Маг земли", 2), ("Маг молний", 1), ("Маг огня", 3)], onchange=self.set_left_player)
        self.menu.add.selector("Правый игрок: ", [("Маг молний", 1), ("Маг земли", 2), ("Маг огня", 3)], onchange=self.set_right_player)
    
        self.menu.add.button("Играть", self.start_two_player_game)
        self.menu.add.button("Выйти", self.exit_game)

        self.run()
    
    def set_enemy(self, selected, value):
        self.enemy = value

    def set_left_player(self, selected, value):
        self.left_player = value
    
    def set_right_player(self, selected, value):
        self.right_player = value

    def start_one_player_game(self):
        Game(self.enemy, False)

    def start_two_player_game(self):
        Game(None, True, self.left_player, self.right_player)

    
    def exit_game(self):
        quit()

    def run(self):
        self.menu.mainloop(self.surface)


if __name__ == "__main__":
    Menu()