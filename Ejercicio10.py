# -*- coding: utf-8 -*-

# ejemplo sistema abierto básico
# versión que genera los arribos de N entidades

from SimPy.Simulation import *
import random

class Arribos(Process):
    # genera arribos aleatorios
    def run(self, N, lamb, mu):
        # genera los arribos de N entidades
        for i in range(N):
            a = Paciente(str(i))  # str(i) es el identificador de cliente
            activate(a, a.run(mu))
            # calcula el tiempo del próximo arrivo...
            t = random.expovariate(1./lamb)
            # ... y lo planifica para el futuro (tiempo actual de la simulación + t
            yield hold, self, t

class Paciente(Process):
    # se implementa init a los efectos de asignar un identificador a esta instancia de cliente
    def __init__(self, id):
        Process.__init__(self)
        self.id=id

    # modelamos el comportamiento de una entidad
    def run(self, mu):
        print(now(), "Arribo cliente ", self.id)
        # intenta tomar el recurso G.server
        yield request, self, G.server
        # en este punto el server ya fue asignado a la entidad
        t = random.expovariate(1./mu)
        print(now(), "Cliente ", self.id, " comienza servicio (tiempo servicio: ", t, ")")
        # planificamos el fin de servicio
        yield hold, self, t
        # en este punto el servicio ya fue ejecutado, resta liberar el server
        yield release, self, G.server
        print(now(), "Fin Cliente ", self.id)
        d = random.uniform(0,1)
        print(d)
        if(d >= 0 and d < 0.3):
            print('Ambulatorio')
        elif(d >= 0.3 and d < 0.5):
            print('Rayos x')
        elif(d >= 0.5 and d < 0.55):
            print('Hospital')
        elif(d >= 0.55 and d < 1):
            print('Laboratorio')



class G:
    server = 'dummy'

def model(c, N, lamb, mu, maxtime, rvseed):
    # inicialización del motor de simulación y semilla
    initialize()
    random.seed(rvseed)
    # definimos el recurso G.server con "c" unidades (será un parámetro de la simulación)
    G.server = Resource(c)

    #  ejecución
    s = Arribos()
    activate(s, s.run(N, lamb, mu))
    simulate(until=maxtime)

# Experimento
# lamb=tiempo entre arribos (media); mu=tiempo de servicio (media)
model(c=4, N=100, lamb=15, mu=3,
      maxtime=480,rvseed=234)
