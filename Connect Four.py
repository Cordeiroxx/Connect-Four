import numpy as np
import random
import pygame
import sys
import math

BLUE = (0,0,255)
BLACK = (0,0,0)
RED = (255,0,0)
YELLOW = (255,255,0)

conta_linha = 6
conta_coluna = 7

JOGADOR = 0
IA = 1

VAZIO = 0
PECA_JOGADOR = 1
PECA_IA = 2

tamanho_janela = 4

def criando_tabela():
	tabela = np.zeros((conta_linha,conta_coluna))
	pygame.display.set_caption('Connect 4')
	return tabela

def soltar_peca(tabela, linha, coluna, peca):
	tabela[linha][coluna] = peca

def e_localizacao_valida(tabela, coluna):
	return tabela[conta_linha-1][coluna] == 0

def obter_proxima_linha_aberta(tabela, coluna):
	for r in range(conta_linha):
		if tabela[r][coluna] == 0:
			return r

def imprimir_tabela(tabela):
	print (np.flip(tabela, 0))

def movimento_vencedor(tabela, peca):

	# Checa a horizontal
	for c in range(conta_coluna-3):
		for r in range(conta_linha):
			if tabela[r][c] == peca and tabela[r][c+1] == peca and tabela[r][c+2] == peca and tabela[r][c+3] == peca:
				return True
	# Checa a vertical
	for c in range(conta_coluna):
		for r in range(conta_linha-3):
			if tabela[r][c] == peca and tabela[r+1][c] == peca and tabela[r+2][c] == peca and tabela[r+3][c] == peca:
				return True
	# Checa as diagonais positivamente inclinadas
	for c in range(conta_coluna-3):
		for r in range(conta_linha-3):
			if tabela[r][c] == peca and tabela[r+1][c+1] == peca and tabela[r+2][c+2] == peca and tabela[r+3][c+3] == peca:
				return True
	# Checa as diagonais negativamente inclinadas
	for c in range(conta_coluna-3):
		for r in range(conta_linha):
			if tabela[r][c] == peca and tabela[r-1][c+1] == peca and tabela[r-2][c+2] == peca and tabela[r-3][c+3] == peca:
				return True

def avaliar_janela(janela, peca):
	Pontuacao = 0
	peca_oposta = PECA_JOGADOR
	if peca == PECA_JOGADOR:
		peca_oposta = PECA_IA

	if janela.count(peca) == 4:
		Pontuacao += 100
	elif janela.count(peca) == 3 and janela.count(VAZIO) == 1:
		Pontuacao += 5
	elif janela.count(peca) == 2 and janela.count(VAZIO) == 2:
		Pontuacao += 2

	if janela.count(peca_oposta) == 3 and janela.count(VAZIO) == 1:
		Pontuacao -= 4

	return Pontuacao

def posicao_pontuacao(tabela, peca):
	Pontuacao = 0

	## Pontuacao Coluna Central
	array_centro = [int(i) for i in list(tabela[:,conta_coluna//2])]
	contador_centro = array_centro.count(peca)
	Pontuacao += contador_centro * 3

	## Pontuacao Horizontal
	for r in range(conta_linha):
		linha_array = [int(i) for i in list(tabela[r,:])]
		for c in range(conta_coluna-3):
			janela = linha_array[c:c+tamanho_janela]
			Pontuacao += avaliar_janela(janela, peca)
		
	## Pontuacao Vertical
	for c in range(conta_coluna):
		coluna_array = [int(i) for i in list(tabela[:,c])]
		for r in range(conta_linha-3):
			janela = coluna_array[r:r+tamanho_janela]
			Pontuacao += avaliar_janela(janela, peca)
			

	## Pontuacao positiva inclinada diagonal
	for r in range(conta_linha-3):
		for c in range(conta_coluna-3):
			janela = [tabela[r+i][c+i] for i in range(tamanho_janela)]
			Pontuacao += avaliar_janela(janela, peca)

	for r in range(conta_linha-3):
		for c in range(conta_coluna-3):
			janela = [tabela[r+3-i][c+3] for i in range(tamanho_janela)]
			Pontuacao += avaliar_janela(janela, peca)

		return Pontuacao

def o_terminal_node(tabela):
	return movimento_vencedor(tabela, PECA_JOGADOR) or movimento_vencedor(tabela, PECA_IA) or len(pegue_locais_validos(tabela)) == 0

def Minimax(tabela, depth, alpha, beta, maximizingPlayer):
	locais_validos = pegue_locais_validos(tabela)
	o_terminal = o_terminal_node(tabela)
	if depth == 0 or o_terminal:
		if o_terminal:
			if movimento_vencedor(tabela, PECA_IA):
				return (None, 100000000000000)
			elif movimento_vencedor(tabela, PECA_JOGADOR):
				return (None, -100000000000000)
			else: # Fim de jogo, não tem mais movimentos válidos
				return (None, 0)
		else: # Depth é zero
			return (None, posicao_pontuacao(tabela, PECA_IA))
	if maximizingPlayer: 
		valor = -math.inf
		col = random.choice(locais_validos)
		for coluna in locais_validos:
			linha = obter_proxima_linha_aberta(tabela, coluna)
			t_copia = tabela.copy()
			soltar_peca(t_copia, linha, coluna, PECA_IA)
			nova_pontuacao = Minimax(t_copia, depth-1, alpha, beta, False)[1]
			if nova_pontuacao > valor:
				valor = nova_pontuacao
				col = coluna
				alpha = max(alpha, valor)
				if alpha >= beta:
					break
		return col, valor

	else: # Minimizing Player
		valor = math.inf
		col = random.choice(locais_validos)
		for coluna in locais_validos:
			linha = obter_proxima_linha_aberta(tabela, coluna)
			t_copia = tabela.copy()
			soltar_peca(t_copia, linha, coluna, PECA_JOGADOR)
			nova_pontuacao = Minimax(t_copia, depth-1, alpha, beta, True)[1]
			if nova_pontuacao < valor:
				valor = nova_pontuacao
				col = coluna
				beta = min(beta, valor)
				if alpha >= beta:
					break
		return col, valor

def pegue_locais_validos(tabela):
	locais_validos = []
	for coluna in range(conta_coluna):
		if e_localizacao_valida(tabela, coluna):
			locais_validos.append(coluna)
	return locais_validos

def escolha_melhor_movimento(tabela, peca):

	locais_validos = pegue_locais_validos(tabela)
	melhor_pontuacao = -10000
	melhor_coluna = random.choice(locais_validos)
	for coluna in locais_validos:
		linha = obter_proxima_linha_aberta(tabela, coluna)
		temp_tabela = tabela.copy()
		soltar_peca(temp_tabela, linha, coluna, peca)
		Pontuacao = posicao_pontuacao(temp_tabela, peca)
		if Pontuacao > melhor_pontuacao:
			melhor_pontuacao = Pontuacao
			melhor_coluna = coluna

	return melhor_coluna
  
def desenhar_tabela(tabela):
	for c in range(conta_coluna):
		for r in range(conta_linha):
			pygame.draw.rect(tela, BLUE, (c*TAMANHOQUADRADO, r*TAMANHOQUADRADO+TAMANHOQUADRADO, TAMANHOQUADRADO, TAMANHOQUADRADO))
			pygame.draw.circle(tela, BLACK, (int(c*TAMANHOQUADRADO+TAMANHOQUADRADO/2), int(r*TAMANHOQUADRADO+TAMANHOQUADRADO+TAMANHOQUADRADO/2)), raio)

	for c in range(conta_coluna):
		for r in range(conta_linha):
			if tabela[r][c] == PECA_JOGADOR:
				pygame.draw.circle(tela, RED, (int(c*TAMANHOQUADRADO+TAMANHOQUADRADO/2), altura-int(r*TAMANHOQUADRADO+TAMANHOQUADRADO/2)), raio)
			elif tabela[r][c] == PECA_IA:
				pygame.draw.circle(tela, YELLOW, (int(c*TAMANHOQUADRADO+TAMANHOQUADRADO/2), altura-int(r*TAMANHOQUADRADO+TAMANHOQUADRADO/2)), raio)
	pygame.display.update()


tabela = criando_tabela()
imprimir_tabela(tabela)
fim_de_jogo = False

pygame.init()

TAMANHOQUADRADO = 90

largura = conta_coluna * TAMANHOQUADRADO
altura = (conta_linha+1) * TAMANHOQUADRADO

tamanho = (largura, altura)
raio = int(TAMANHOQUADRADO/2 - 5)

tela = pygame.display.set_mode(tamanho)
desenhar_tabela(tabela)
pygame.display.update()

myfont = pygame.font.SysFont("monospace", 50)

turno = random.randint(JOGADOR, IA)

while not fim_de_jogo:

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			sys.exit()

		if event.type == pygame.MOUSEMOTION:
			pygame.draw.rect(tela, BLACK, (0,0, largura, TAMANHOQUADRADO))
			Xposicao = event.pos[0]
			if turno == JOGADOR:
				pygame.draw.circle(tela, RED, (Xposicao, int(TAMANHOQUADRADO/2)), raio)

			pygame.display.update()

		if event.type == pygame.MOUSEBUTTONDOWN:
			pygame.draw.rect(tela, BLACK, (0,0, largura, TAMANHOQUADRADO))

			# --- Chama Jogador 1 ---#
			
			if turno == JOGADOR:
				Xposicao = event.pos[0]
				coluna = int(math.floor(Xposicao/TAMANHOQUADRADO))

				if e_localizacao_valida(tabela, coluna):
					linha = obter_proxima_linha_aberta(tabela, coluna)
					soltar_peca(tabela, linha, coluna, PECA_JOGADOR)

					if movimento_vencedor(tabela, PECA_JOGADOR):
						label = myfont.render("Jogador 1 venceu!!", 1, RED)
						tela.blit(label, (40,10))
						fim_de_jogo = True

					turno += 1
					turno = turno % 2

					imprimir_tabela(tabela)
					desenhar_tabela(tabela)

			#--- Chama Jogador 2 ---#

	if turno == IA and not fim_de_jogo:
		
		coluna, minimax_pontuacao = Minimax(tabela, 5, -math.inf, math.inf, True)

		if e_localizacao_valida(tabela, coluna):
			linha = obter_proxima_linha_aberta(tabela, coluna)
			soltar_peca(tabela, linha, coluna, PECA_IA)

			if movimento_vencedor(tabela, PECA_IA):
				label = myfont.render("Jogador 2 venceu!!", 1, YELLOW)
				tela.blit(label, (40,10))
				fim_de_jogo = True


			imprimir_tabela(tabela)
			desenhar_tabela(tabela)

			turno += 1
			turno = turno % 2

	if fim_de_jogo:
		pygame.time.wait(3000)