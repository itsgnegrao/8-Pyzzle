# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# UNIVERSIDADE TECNOLÓGICA FEDERAL DO PARANÁ - UTFPR-CM
# Gabriel Negrão Silva - 1602012 - 25/10/2017
# Inteligencia Artificial - Ciência Da Computação
#
# Algoritmo soluciona 8-Puzzle recebido escrito em python utilizando:
# - A* com Hamming+movie
# ou
# - A* com Manhattan
# ou
# - A* com Pecas Fora do lugar
#
# 8-Pyzzle.py
# -----------------------------------------------------------------------------
from heapq import *
from random import *
import time, math, sys

class FilaPrioridade:
  def __init__(self):
    self.fp = []

  def add(self, item):
    heappush(self.fp, item)

  def poll(self):
    return heappop(self.fp)

  def peek(self):
    return self.fp[0]

  def remove(self, item):
    valor = self.fp.remove(item)
    heapify(self.fp)
    return valor is not None

  def __len__(self):
    return len(self.fp)


class Estado:
  def __init__(self, valores, movimentos=0, vizinhos=None):
    self.valores = valores
    self.movimentos = movimentos
    self.vizinhos = vizinhos
    self.objetivo = range(1, 9)

  #funcao que define os movimentos_possiveis
  def movimentos_possiveis(self, movimentos, heuristica):
    i = self.valores.index(0)
    res = [] #recebe o valor da distancia de cada possibilidade
    estados = [] #rescebe os respectivos estados possiveis

    #verifica movimentos
    #movimento Up
    if i in [3, 4, 5, 6, 7, 8]:
      novo_quadro = self.valores[:]
      novo_quadro[i], novo_quadro[i - 3] = novo_quadro[i - 3], novo_quadro[i]
      novo_estado = Estado(novo_quadro, movimentos, self)

      if heuristica == '--MANHATTAN':
          res.append(novo_estado.manhattan_distance())
      elif heuristica == '--PECAS_FORA':
          res.append(novo_estado._h())

      estados.append(novo_estado)
      print 'Up\n',novo_estado,'\n'

    #movimento Left
    if i in [1, 2, 4, 5, 7, 8]:
      novo_quadro = self.valores[:]
      novo_quadro[i], novo_quadro[i - 1] = novo_quadro[i - 1], novo_quadro[i]
      novo_estado = Estado(novo_quadro, movimentos, self)

      if heuristica == '--MANHATTAN':
          res.append(novo_estado.manhattan_distance())
      elif heuristica == '--PECAS_FORA':
          res.append(novo_estado._h())

      estados.append(novo_estado)
      print 'Left\n',novo_estado,'\n'

    #movimento Right
    if i in [0, 1, 3, 4, 6, 7]:
      novo_quadro = self.valores[:]
      novo_quadro[i], novo_quadro[i + 1] = novo_quadro[i + 1], novo_quadro[i]
      novo_estado = Estado(novo_quadro, movimentos, self)

      if heuristica == '--MANHATTAN':
          res.append(novo_estado.manhattan_distance())
      elif heuristica == '--PECAS_FORA':
          res.append(novo_estado._h())

      estados.append(novo_estado)
      print 'Right\n',novo_estado,'\n'

    #movimento Down
    if i in [0, 1, 2, 3, 4, 5]:
      novo_quadro = self.valores[:]
      novo_quadro[i], novo_quadro[i + 3] = novo_quadro[i + 3], novo_quadro[i]
      novo_estado = Estado(novo_quadro, movimentos, self)

      if heuristica == '--MANHATTAN':
          res.append(novo_estado.manhattan_distance())
      elif heuristica == '--PECAS_FORA':
          res.append(novo_estado._h())

      estados.append(novo_estado)
      print 'Down\n',novo_estado,'\n'


    #builda os estados
    if heuristica == '--EXPAND_ALL': #somente expande os estados
        #consome todos estados
        for estado in estados:
            yield estado

    elif heuristica in ['--MANHATTAN' , '--PECAS_FORA']: #expande sempre os menores
        #consome sempre o menor das distancias
        for i in range(len(res)):
            estado = estados[res.index(min(res))]
            yield estado
            res.remove(min(res))
            estados.remove(estado)

    else:
        print 'Função de calculo de distancia / kernel nao implementada!'
        print 'Utilize:\n--EXPAND_ALL\n--MANHATTAN\n--PECAS_FORA\n'
        exit(1)

  #funcao de calculo da distancia manhattan_distance
  def manhattan_distance(self):
    distance = 0
    kalan = 0
    bolum = 0

    for i in range(len(self.objetivo)):
        position_difference = abs(self.objetivo[i] - self.valores[i])
        if i is not 0:
            kalan = position_difference % 3
            bolum = position_difference / 3
            distance += kalan + int(math.floor(bolum))
            if abs(self.objetivo[i] % 3 - self.valores[i] % 3) == 2 and position_difference % 3 == 1:
                distance += 2
            #print "i: " + str(i) + " goal-index: " + str(self.objetivo.index(i)) + " current-index: " + str(self.valores.index(i)) + " bolum: " + str(bolum) + ": kalan: " + str(kalan) + ": distance: " + str(distance)
    return distance

  #funcao score define pecas fora + movimentos
  def score(self):
    return self._h() + self._g()

  #funcao calculo pecas fora do lugar
  def _h(self):
    return sum([1 if self.valores[i] != self.objetivo[i] else 0 for i in xrange(8)])

  def _g(self):
    return self.movimentos

  def __cmp__(self, outro_estado):
    return self.valores == outro_estado.valores

  def __eq__(self, outro_estado):
    return self.__cmp__(outro_estado)

  def __hash__(self):
    return hash(str(self.valores))

  def __lt__(self, outro_estado):
    return self.score() < outro_estado.score()

  def __str__(self):
    return '\n'.join([str(self.valores[:3]),
        str(self.valores[3:6]),
        str(self.valores[6:9])]).replace(',', '').replace('0', 'x')



class Solucionador:
  def __init__(self, estado_inicial=None):
    self.estado_inicial = Estado(estado_inicial)
    self.objetivo = range(1, 9)

  #funcao executada somente quando encontra o objetivo, atribuindo os respectivoss vizinhos formando o caminho
  def _rebuildPath(self, fim):
    resolucao = [fim]
    estado = fim.vizinhos
    while estado.vizinhos:
      resolucao.append(estado)
      estado = estado.vizinhos
    return resolucao

  #funcao que resolve tudo implementa A*
  def resolver(self, heuristica):
    fila_prioridade = FilaPrioridade()
    fila_prioridade.add(self.estado_inicial)
    closed = set()
    movimentos = 0

    print("Estado inicial do puzzle:")
    print(self.estado_inicial)
    print
    print('Tentando encontrar a resolução do puzzle..')

    start_time = time.time()
    while fila_prioridade:
      estado_atual = fila_prioridade.poll()

      #Caso encontre um solução
      if estado_atual.valores[:-1] == self.objetivo: #caso os valores atuais sejam identicos ao do objetivo
        print ('Achei a solução do puzzle!')
        print estado_atual
        print
        resolucao = self._rebuildPath(estado_atual) #adiciona a si mesmo como solução final
        end_time = time.time() #pega o tempo de finalização

        #print dos estados da solução reversed(resolucao) == inverte a lista para print
        print 'Resolucao do 8-Puzzle:'
        for estado, i in zip(reversed(resolucao),range(len(resolucao))):
          print 'Movimento nº:',i+1, '- Pecas fora do lugar:',estado._h()
          print(estado)
          print

        print('Solucao encontrada a partir do algoritmo: %s' %heuristica)
        print('Solução encontrada utilizando: %d movimentos' % len(resolucao))
        print('Solução encontrada em: %s segundos' % (end_time - start_time))
        print('Solução utilizou de: %d expansões' %movimentos)
        break


      movimentos += 1 #Incrementa o numero de expansoes


      print 'Possiveis movimentos da expansao n',movimentos
      print 'Estado atual\n', estado_atual
      print '\nExpansoes:'

      #Executa A* com a heuristica selecionada, onde toda magia acontece
      for estado in estado_atual.movimentos_possiveis(movimentos,heuristica):
        if estado not in closed:
         fila_prioridade.add(estado) #aciciona a fila de prioridade o estado expandido para consumo posterior
        else:
         print 'Já Expandido!\n'
      closed.add(estado_atual)#aciciona que este estado já foi expandido

    #Caso o algoritmo não consiga solucionar
    else:
      print('Não foi possível solucionar')


#Somente teste
#puzzle = [i for i in range(10)]
#print(puzzle)
#shuffle(puzzle)
#print(puzzle)

#Cria o Puzzle
Puzzle = [2, 3, 1, 0, 5, 6, 4, 7, 8]

solucionador = Solucionador(Puzzle) #Cria o objeto solucionador
solucionador.resolver(sys.argv[1])#Chama o resolver com o parametro de calculo passado via terminal [ --EXPAND_ALL , --MANHATTAN , --PECAS_FORA ]

#solucionador.resolver('--EXPAND_ALL') #Tenta resolver o problema expandindo todas as possibilidades
#solucionador.resolver('--MANHATTAN') #Tenta resolver o problema expandindo utilizando a heuristica de --MANHATTAN para calculo de distancia
#solucionador.resolver('--PECAS_FORA') #Tenta resolver o problema expandindo utilizando a heuristica de --PECAS_FORA para calculo de distancia'''
