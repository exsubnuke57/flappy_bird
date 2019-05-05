import pygame as pg, random, sys, os 
from pygame.locals import *

#Globals
FPS = 30
ANIMATION_SPEED = 0.18
SCREEN_WIDTH = 284 * 3
SCREEN_HEIGHT = 512
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
PURPLE = (255, 0, 255)

pg.init()
pg.mixer.init()
clock = pg.time.Clock()
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pg.display.set_caption("Flappy Bird")
game_dir = os.path.dirname(__file__)
resource_dir = os.path.join(game_dir, 'resources_flappy')
font_dir = os.path.join(resource_dir, 'fonts')
image_dir = os.path.join(resource_dir, 'images')
sound_dir = os.path.join(resource_dir, 'sounds')
font_type = pg.font.match_font("comicsansms")
hit_pipe = pg.mixer.Sound(os.path.join(sound_dir,"hit_pipe.wav"))
pg.mixer.music.load(os.path.join(sound_dir,"clearday.ogg"))

class Bird(pg.sprite.Sprite):
	def __init__(self, resource_dict):
		pg.sprite.Sprite.__init__(self)
		self.images = [resource_dict["bird_wing_up"],resource_dict["bird_wing_down"]]
		self.image = self.images[0]
		self.image.set_colorkey(BLACK)
		self.rect = self.image.get_rect()
		self.rect.x = 20
		self.rect.y = SCREEN_HEIGHT / 2
		self.velx = 0
		self.vely = 15
		self.last_update = pg.time.get_ticks()
		self.climb_trigger = False
		self.climb_update = pg.time.get_ticks()
		self.climb_duration = 120
		self.bird_anim = 0

	def update(self):
		if pg.time.get_ticks() - self.last_update > 40:
			self.last_update = pg.time.get_ticks()
			self.rect.x += self.velx
			if self.rect.top < 0:
				self.rect.top = 0
			if self.rect.left < 20:
				self.rect.left = 20
			if self.rect.right > SCREEN_WIDTH // 2:
				self.rect.right = SCREEN_WIDTH // 2
			self.rect.y += self.vely
			if self.rect.bottom > SCREEN_HEIGHT:
				hit_pipe.play()
				self.kill()
			if self.climb_trigger:
				self.climb_trigger = False
				self.climb_update = pg.time.get_ticks()
			if pg.time.get_ticks() - self.climb_update > self.climb_duration:
				self.vely = 12
			else:
				temp = self.rect.center
				self.bird_anim = (self.bird_anim + 1) % 2
				self.image = self.images[self.bird_anim]
				self.image.set_colorkey(BLACK)
				self.rect = self.image.get_rect()
				self.rect.center = temp

class Pipe(pg.sprite.Sprite):
	def __init__(self,screen, resource_dict, total_pipe_bodies, pipe_velocity):
		pg.sprite.Sprite.__init__(self)
		self.screen = screen
		self.resource_dict = resource_dict
		self.pipe_size_upper = random.randint(1,total_pipe_bodies)
		self.pipe_size_lower = total_pipe_bodies - self.pipe_size_upper
		self.pipe_x = SCREEN_WIDTH
		self.pipe_end_upper = 0
		self.pipe_end_lower = 0
		self.pass_pipe = False
		self.add_score = False
		self.vel = pipe_velocity 
		self.last_update = pg.time.get_ticks()
		
	def draw_pipe(self,screen,resource_dict):	
		self.pipe_body_image = resource_dict["pipe_body"]
		self.pipe_end_image = resource_dict["pipe_end"]
		self.image = self.pipe_body_image	
		self.rect = self.image.get_rect()
		self.pipe_body_height = self.rect.height
		self.rect.x = self.pipe_x
		self.rect.y = SCREEN_HEIGHT
		for pipe_body_piece in range(self.pipe_size_upper):
			screen.blit(self.image,(self.rect.x, self.pipe_body_height * (pipe_body_piece)))
		for pipe_body_piece in range(self.pipe_size_lower):
			screen.blit(self.image,(self.rect.x, self.rect.y - self.pipe_body_height * (pipe_body_piece + 1)))
		self.image = resource_dict["pipe_end"]
		self.rect = self.image.get_rect()
		self.rect.x = self.pipe_x
		self.rect.y = SCREEN_HEIGHT
		self.pipe_end_height = self.rect.height
		screen.blit(self.image,(self.rect.x,self.rect.y-self.pipe_end_height*self.pipe_size_lower-self.pipe_end_height))
		screen.blit(self.image,(self.rect.x,self.pipe_end_height*self.pipe_size_upper))
		self.pipe_end_upper = self.pipe_end_height*(self.pipe_size_upper + 1)
		self.pipe_end_lower = self.rect.y-self.pipe_end_height*self.pipe_size_lower-self.pipe_end_height

	def update(self):
		self.pipe_x -= self.vel
		self.draw_pipe(self.screen,self.resource_dict)

def load_resources():
	resources = {"background" : pg.image.load(os.path.join(image_dir, "background.png")).convert(),
				 "bird_wing_down" : pg.image.load(os.path.join(image_dir, "bird_wing_down.png")).convert(),
				 "bird_wing_up" : pg.image.load(os.path.join(image_dir, "bird_wing_up.png")).convert(),
				 "pipe_body" : pg.image.load(os.path.join(image_dir, "pipe_body.png")),
				 "pipe_end" : pg.image.load(os.path.join(image_dir, "pipe_end.png")).convert()
				}
	return resources

def get_pipe_dimensions(resource_dict):			#Returns pipe piece dimensions: body width, body height, end width, end height
	pipe_dim = []
	pipe_body_rect = resource_dict["pipe_body"].get_rect()
	pipe_end_rect = resource_dict["pipe_end"].get_rect()
	pipe_dim.append(pipe_body_rect.width)
	pipe_dim.append(pipe_body_rect.height)
	pipe_dim.append(pipe_end_rect.width)
	pipe_dim.append(pipe_end_rect.height)
	return pipe_dim

def drawText(msg,size,color,x,y,center=True):	#If x==-1, text is centered. font_type must be defined prior to this function
	font = pg.font.Font(font_type, size)
	text_surf = font.render(msg,True,color)
	if not center:
		screen.blit(text_surf,(x,y))
	if center:
		rect = text_surf.get_rect()
		text_len = rect.width
		center = SCREEN_WIDTH // 2 - text_len // 2
		screen.blit(text_surf,(center,y))

def splash_start():								#Game entry splash screen
	title_timer = pg.time.get_ticks()
	blue_intensity = 255
	blue_increment = -5       
	pause = True
	while pause:
		for event in pg.event.get():
			if event.type == pg.QUIT:
				pause = False
				pg.quit()
			if event.type == pg.KEYDOWN:
				if event.key == pg.K_SPACE:
					pause = False
				if event.key == pg.K_ESCAPE or event.key == pg.K_q:
					pause = False
					pg.quit()
		if pg.time.get_ticks() - title_timer > 20:
			title_timer = pg.time.get_ticks()
			blue_intensity += blue_increment
			if blue_intensity <= 5 or blue_intensity >= 255:
				blue_increment *= -1
			screen.fill(BLACK)
			drawText("Flappy Bird",70,(0,0,blue_intensity) ,-1,SCREEN_HEIGHT/2-40)
			drawText("Guide your bird through the pipes --- do not hit them!",30,WHITE,-1,SCREEN_HEIGHT/2+60)
			drawText("Space to flap, Left/Right arrows to move bird",30,WHITE,-1,SCREEN_HEIGHT/2+100)
			drawText("Press Space to continue, Q to quit",30,WHITE,-1,480)
			pg.display.update()
			pg.mixer.music.play(-1)

def splash_gameover(high_score_flag, high_score, resource_dict):	#Game Over screen
	screen.blit(resource_dict["background"],(0,0))
	screen.blit(resource_dict["background"],(SCREEN_WIDTH / 3 , 0))
	screen.blit(resource_dict["background"],(SCREEN_WIDTH / 3 * 2 , 0))
	hs_text = ""
	hs_color = PURPLE
	drawText("GAME OVER",70,BLUE ,-1,SCREEN_HEIGHT/2)
	if high_score_flag:
		hs_text = "Congratulations!  You got a new "
		hs_color = BLUE
	drawText(hs_text+"High Score: "+str(high_score),30,hs_color,-1,SCREEN_HEIGHT/2+60)
	drawText("Press space to play again, q to quit",30,BLUE,-1,480)
	pg.display.update()
	pause = True
	while pause:
		for event in pg.event.get():
			if event.type == pg.QUIT:
				pause = False
				pg.quit()
			if event.type == pg.KEYDOWN:
				if event.key == pg.K_SPACE:
					pause = False
				if event.key == pg.K_ESCAPE or event.key == pg.K_q:
					pause = False
					pg.quit()	

def main():
	resource_dict = load_resources()
	pipe_dimensions = get_pipe_dimensions(resource_dict)
	pipe_gap = 8
	total_pipe_bodies = SCREEN_HEIGHT // (pipe_dimensions[1]) - pipe_gap #Total pieces - 2 pipe ends - 'gap'
	pipe_timer = pg.time.get_ticks()
	pipe_velocity = 2
	all_sprites = pg.sprite.Group()
	birds = pg.sprite.Group()
	pipes = pg.sprite.Group()
	bird = Bird(resource_dict)
	pipe = Pipe(screen, resource_dict, total_pipe_bodies, pipe_velocity)
	all_sprites.add(bird)
	all_sprites.add(pipe)
	birds.add(bird)
	pipes.add(pipe)
	score = 0
	high_score = 0
	high_score_flag = False
	level = 1
	pause = False

	running = True
	game_over = False

	while running:
		if game_over:
			pg.mixer.music.stop()
			game_over = False
			splash_gameover(high_score_flag, high_score, resource_dict)
			score = 0
			level = 1
			pipe_gap = 8
			pipe_velocity = 2
			high_score_flag = False
			all_sprites.empty()
			birds.empty()
			pipes.empty()
			bird = Bird(resource_dict)
			all_sprites.add(bird)
			birds.add(bird)
			pg.mixer.music.play(-1)
			
		for event in pg.event.get():
			if event.type == pg.QUIT:
				running = False
			if event.type == pg.KEYDOWN:
				if event.key == pg.K_ESCAPE:
					running = False
				if event.key == pg.K_SPACE:
					bird.vely = -8
					bird.climb_trigger = True
				if event.key == pg.K_RIGHT:
					bird.velx = 8
				if event.key == pg.K_LEFT:
					bird.velx = -8
				if event.key == pg.K_p:
					if pause == True:
						pause = False
						pg,mixer.music.play(-1)
					else:
						pause = True
						pg.mixer.music.stop()
		if not pause:
			screen.blit(resource_dict["background"],(0,0))
			screen.blit(resource_dict["background"],(SCREEN_WIDTH / 3 , 0))
			screen.blit(resource_dict["background"],(SCREEN_WIDTH / 3 * 2 , 0))
			if len(birds) == 0:
				game_over = True
			if pg.time.get_ticks() - pipe_timer > random.randint(2000,70000):
				pipe_timer = pg.time.get_ticks()
				pipe = Pipe(screen, resource_dict, total_pipe_bodies, pipe_velocity)
				all_sprites.add(pipe)
				pipes.add(pipe)
			all_sprites.update()
			all_sprites.draw(screen)
			drawText("Score: "+str(score),30,(0,0,0),10,10,False)
			drawText("Flappy Bird!",40,(0,0,255),320,10,False)
			drawText("Level: "+str(level),30,(0,0,0),740,10,False)
			pg.display.update() 
			for ix,pipe in enumerate(pipes):
				if bird.rect.right >= pipe.rect.left and bird.rect.left <= pipe.rect.right and (bird.rect.top <= pipe.pipe_end_upper or bird.rect.bottom >= pipe.pipe_end_lower):
					hit_pipe.play()
					game_over = True
				if bird.rect.left >= pipe.rect.right:
					pipe.pass_pipe = True
				if pipe.pass_pipe and not pipe.add_score:
					pipe.pass_pipe = False
					pipe.add_score = True
					score += 10
					if score > high_score:
						high_score = score
						high_score_flag = True
					if score % 100 == 0:
						level += 1
						difficulty = (score // 100) % 2
						print(difficulty)
						if difficulty:			#If odd, increase pipe speed
							pipe_velocity += 1
							if pipe_velocity >= 6:
								pipe_velocity = 6
							for ix,pipe in enumerate(pipes):  	
								pipe.vel = pipe_velocity
						else:					#If even, decrease pipe gap
							pipe_gap -= 1
							if pipe_gap <= 3:
								pipe_gap = 3
							total_pipe_bodies = SCREEN_HEIGHT // (pipe_dimensions[1]) - pipe_gap  
				if pipe.rect.right < 0:
					pipe.kill()

splash_start()
main()
pg.quit()