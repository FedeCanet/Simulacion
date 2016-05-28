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
        print(now(), "Arribo paciente ", self.id)
        tiempoEsperaRevisionInicial = 3

        # Paciente entra al triage
        print('Paciente ', self.id, ' entra al triage en el tiempo ', now())
        yield hold, self, tiempoEsperaRevisionInicial
        print('Paciente ', self.id, ' sale del triage y es derivado en el tiempo ', now())

        d = random.uniform(a=0, b=1)
        if(d >= 0 and d < 0.3):
            print('Paciente ', self.id, ' derivado a servicio ambulatorio en tiempo ', now())
            yield request, self, G.serverAt
            print('Paciente ', self.id, ' comienza a atenderse en servicio ambulatorio en tiempo ', now())

            tiempoServicioAt = abs(random.normalvariate(15, 6))

            yield hold, self, tiempoServicioAt
            print('Paciente ', self.id, ' finaliza tratamiento en tiempo ', now())

            yield release, self, G.serverAt

        elif(d >= 0.3 and d < 0.5):
            print('Paciente ', self.id, ' derivado a rayos x en tiempo ', now())
            yield request, self, G.serverAt
            print('Paciente ', self.id, ' comienza a atenderse en rayos x en tiempo ', now())

            tiempoServicioRrx = abs(random.normalvariate(15, 3))

            yield hold, self, tiempoServicioRrx
            print('Paciente ', self.id, ' finaliza tratamiento en tiempo ', now())

            yield release, self, G.serverAt

        elif(d >= 0.5 and d < 0.55):
            print('Paciente ', self.id, ' es derivado al hospital en tiempo ', now())

        elif(d >= 0.55 and d < 1):
            print('Paciente ', self.id, ' derivado al servicio de laboratorio en tiempo ', now())
            yield request, self, G.serverAt
            print('Paciente ', self.id, ' comienza a atenderse en el servicio de laboratorio en tiempo ', now())

            tiempoServicioRrx = abs(random.normalvariate(30, 6))

            yield hold, self, tiempoServicioRrx
            print('Paciente ', self.id, ' finaliza exámenes en tiempo ', now())

            yield release, self, G.serverAt



class G:
    serverAt = 'At. Ambulatoria'

    serverRrx = 'Rayos X'

    serverH = 'Hospital'

    serverLab = 'Serv. de laboratorio'

def model(c, N, lamb, mu, maxtime, rvseed):
    # inicialización del motor de simulación y semilla
    initialize()
    random.seed(rvseed)
    PROCmonitor = Monitor()
    # definimos el recurso G.server con "c" unidades (será un parámetro de la simulación)
    G.serverAt = Resource(c, 'At. Ambulatoria')
    #G.

    #  ejecución
    s = Arribos()
    activate(s, s.run(N, lamb, mu))
    simulate(until=maxtime)

# Experimento
# lamb=tiempo entre arribos (media); mu=tiempo de servicio (media)
model(c=1, N=100, lamb=15, mu=3,
      maxtime=480, rvseed=234)
