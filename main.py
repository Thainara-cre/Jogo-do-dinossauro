import pygame
from pygame.locals import *
from sys import exit
import os
from random import randrange, choice

# choice recebe uma lista e escolhe um obejto dela aleatoriamente

pygame.init()
pygame.mixer.init()

diretorio_principal = os.path.dirname(__file__)
diretorio_images = os.path.join(diretorio_principal, 'images')
diretorio_audios = os.path.join(diretorio_principal, 'audios')

LARGURA = 640
ALTURA = 480

BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)

tela = pygame.display.set_mode((LARGURA, ALTURA))

pygame.display.set_caption('Dino Game')

sprite_sheet = pygame.image.load(os.path.join(diretorio_images, 'dinoSpritesheet.png')).convert_alpha()
# convert alfa conserva a transaparencia

som_colisao = pygame.mixer.Sound(os.path.join(diretorio_audios, 'sons_death_sound.wav'))
som_colisao.set_volume(1)

som_pontuacao = pygame.mixer.Sound(os.path.join(diretorio_audios, 'sons_score_sound.wav'))
som_pontuacao.set_volume(1)

colidiu = False
escolha_obstaculo = choice([0, 1])
pontos = 0
velocidade_jogo = 10


def exibeMensagem(msg, tamanho, cor):
    fonte = pygame.font.SysFont('comicsansms', tamanho, True, False)
    mensagem = f'{msg}'
    texto_formatado = fonte.render(mensagem, True, cor)
    return texto_formatado

def reiniciar_jogo():
    global pontos, velocidade_jogo, colidiu, escolha_obstaculo
    pontos = 0
    velocidade_jogo = 10
    colidiu = False
    dinoVoador.rect.x = LARGURA
    cacto.rect.x = LARGURA
    escolha_obstaculo = choice([0, 1])
    dino.rect.y = ALTURA - 64 - 96 // 2
    dino.pulo = False

class Dino(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.som_pulo = pygame.mixer.Sound(os.path.join(diretorio_audios, 'sons_jump_sound.wav'))
        # carrega o som do pulo
        self.som_pulo.set_volume(1)
        # aumenta o som do pulo 1 é o maximo e 0 é o minimo
        self.imagens_dinossauro = []
        for i in range(3):
            img = sprite_sheet.subsurface((i * 32, 0), (32, 32))
            # subsurface "recorta" a imagem pro pedaço que eu quero
            img = pygame.transform.scale(img, (32 * 3, 32 * 3))
            # scale almenta a imagem
            self.imagens_dinossauro.append(img)

        self.index_lista = 0
        self.image = self.imagens_dinossauro[self.index_lista]
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        # cria uma mascara ao redor do sprite
        # vai me ajudar na hora da colicao do dinossauro com o cacto
        self.posicao_y_inicial = ALTURA - 64 - 96 // 2
        # 96 e a altura do frame do dinossauro
        self.rect.center = (100, ALTURA - 64)
        # center centro da imagem
        self.pulo = False

    def pular(self):
        self.pulo = True
        self.som_pulo.play()

    def update(self):
        if self.pulo == True:
            if self.rect.y <= 200:
                self.pulo = False
            self.rect.y -= 20
            # y do canto superior esquerdo
        else:
            if self.rect.y < self.posicao_y_inicial:
                self.rect.y += 20
            else:
                self.rect.y = self.posicao_y_inicial

        if self.index_lista > 2:
            self.index_lista = 0
        self.index_lista += 0.25
        self.image = self.imagens_dinossauro[int(self.index_lista)]


class Nuvens(pygame.sprite.Sprite):  # herda funcionalidades do sprite
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = sprite_sheet.subsurface((7 * 32, 0), (32, 32))
        self.image = pygame.transform.scale(self.image, (32 * 3, 32 * 3))
        self.rect = self.image.get_rect()
        self.rect.y = randrange(50, 200, 50)
        # randrange sorteia um numero no intervalo que eu definir
        self.rect.x = LARGURA - randrange(30, 300, 90)

    def update(self):
        if self.rect.topright[0] < 0:
            # topright é o canto superior direito da imagem
            self.rect.x = LARGURA
            self.rect.y = randrange(50, 200, 50)
        self.rect.x -= velocidade_jogo


class Chao(pygame.sprite.Sprite):
    def __init__(self, pos_x):
        pygame.sprite.Sprite.__init__(self)
        self.image = sprite_sheet.subsurface((6 * 32, 0), (32, 32))
        self.image = pygame.transform.scale(self.image, (32 * 2, 32 * 2))
        self.rect = self.image.get_rect()
        self.rect.y = ALTURA - 64
        self.rect.x = pos_x * 64

    def update(self):
        if self.rect.topright[0] < 0:
            self.rect.x = LARGURA
        self.rect.x -= 10


class Cacto(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = sprite_sheet.subsurface((5 * 32, 0), (32, 32))
        self.image = pygame.transform.scale(self.image, (32 * 2, 32 * 2))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.escolha = escolha_obstaculo
        self.rect.center = (LARGURA, ALTURA - 64)
        self.rect.x = LARGURA

    def update(self):
        if self.escolha == 0:
            if self.rect.topright[0] < 0:
                self.rect.x = LARGURA
            self.rect.x -= velocidade_jogo


class DinoVoador(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.imagens_dinossauro = []
        for i in range(3, 5):
            img = sprite_sheet.subsurface((i * 32, 0), (32, 32))
            img = pygame.transform.scale(img, (32 * 3, 32 * 3))
            self.imagens_dinossauro.append(img)

        self.index_lista = 0
        self.image = self.imagens_dinossauro[self.index_lista]
        self.mask = pygame.mask.from_surface(self.image)
        self.escolha = escolha_obstaculo
        self.rect = self.image.get_rect()
        # posiciona o elemento na tela
        # image mask e rect não podem ter outro nome
        self.rect.center = (LARGURA, 300)
        self.rect.x = LARGURA

    def update(self):
        if self.escolha == 1:
            if self.rect.topright[0] < 0:
                self.rect.x = LARGURA
            self.rect.x -= velocidade_jogo

            if self.index_lista > 1:
                self.index_lista = 0
            self.index_lista += 0.25
            self.image = self.imagens_dinossauro[int(self.index_lista)]
            # esse if movimenta o dinossauro voador


todas_as_sprites = pygame.sprite.Group()
dino = Dino()
todas_as_sprites.add(dino)

for i in range(4):
    nuvem = Nuvens()
    todas_as_sprites.add(nuvem)

for i in range(LARGURA * 2 // 64):
    chao = Chao(i)
    todas_as_sprites.add(chao)

cacto = Cacto()
todas_as_sprites.add(cacto)

grupo_obstaculos = pygame.sprite.Group()
grupo_obstaculos.add(cacto)

dinoVoador = DinoVoador()
todas_as_sprites.add(dinoVoador)
grupo_obstaculos.add(dinoVoador)

relogio = pygame.time.Clock()
while True:
    relogio.tick(30)
    tela.fill(BRANCO)
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            exit()
        if event.type == KEYDOWN:
            if event.key == K_SPACE and colidiu == False:
                if dino.rect.y != dino.posicao_y_inicial:
                    pass
                    # pass é não faça nada em python
                else:
                    dino.pular()
            if event.key == K_r and colidiu == True:
                reiniciar_jogo()

    colisoes = pygame.sprite.spritecollide(dino, grupo_obstaculos, False, pygame.sprite.collide_mask)

    todas_as_sprites.draw(tela)
    if cacto.rect.topright[0] <= 0 or dinoVoador.rect.topright[0] <= 0:
        escolha_obstaculo = choice([0, 1])
        cacto.rect.x = LARGURA
        dinoVoador.rect.x = LARGURA
        cacto.escolha = escolha_obstaculo
        dinoVoador.escolha = escolha_obstaculo

    if colisoes and colidiu == False:
        som_colisao.play()
        colidiu = True

    if colidiu == True:
        if pontos % 100 == 0:
            pontos += 1
        game_over = exibeMensagem('GAME OVER', 40, PRETO)
        tela.blit(game_over, (LARGURA//2, ALTURA//2))
        restart = exibeMensagem('Pressione r para reiniciar', 20, PRETO)
        tela.blit(restart, (LARGURA//2, (ALTURA//2) + 60))

    else:
        pontos += 1
        todas_as_sprites.update()
        texto_pontos = exibeMensagem(pontos, 40, PRETO)

    if pontos % 100 == 0:
        som_pontuacao.play()
        if velocidade_jogo <= 23:
            velocidade_jogo += 1

    tela.blit(texto_pontos, (520, 30))

    pygame.display.flip()
