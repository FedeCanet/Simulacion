# -*- coding: utf-8 -*-

# ejemplo sistema abierto básico
# versión que genera los arribos de N entidades
from SimPy.Simulation import *
import random
import matplotlib.pyplot as plt

class Arribos(Process):
    # genera arribos aleatorios
    def run(self, N, lamb, mu):
        # genera los arribos de N entidades
        for i in range(N):
            a = Paciente(str(i))  # str(i) es el identificador de cliente
            activate(a, a.run(mu))
            # calcula el tiempo del próximo arrivo...
            t = random.expovariate(1. / lamb)
            # ... y lo planifica para el futuro (tiempo actual de la simulación + t
            yield hold, self, t


class Paciente(Process):
    # se implementa init a los efectos de asignar un identificador a esta instancia de cliente
    def __init__(self, id):
        Process.__init__(self)
        self.id = id

    # modelamos el comportamiento de una entidad
    def run(self, mu):
        print(now(), "Arribo paciente ", self.id)
        tiempoEsperaRevisionInicial = mu

        # Paciente entra al triage
        print('Paciente ', self.id, ' entra al triage en el tiempo ', now())
        yield hold, self, tiempoEsperaRevisionInicial
        print('Paciente ', self.id, ' sale del triage y es derivado en el tiempo ', now())

        derivadoA = random.uniform(a=0, b=1)

        if 0 <= derivadoA < 0.3:
            print('Paciente ', self.id, ' derivado a servicio ambulatorio en tiempo ', now())

            G.monitorHistograma.observe(G.serverAt.waitQ)
            yield request, self, G.serverAt
            print('Paciente ', self.id, ' comienza a atenderse en servicio ambulatorio en tiempo ', now())

            tiempoServicioAt = abs(random.normalvariate(15, 6))

            yield hold, self, tiempoServicioAt
            print('Paciente ', self.id, ' finaliza tratamiento en tiempo ', now())
            yield release, self, G.serverAt


        elif 0.3 <= derivadoA < 0.5:
            print('Paciente ', self.id, ' derivado a rayos x en tiempo ', now())
            yield request, self, G.serverRrx
            print('Paciente ', self.id, ' comienza a atenderse en rayos x en tiempo ', now())

            tiempoServicioRrx = abs(random.normalvariate(15, 3))

            yield hold, self, tiempoServicioRrx
            print('Paciente ', self.id, ' finaliza tratamiento en tiempo ', now())
            yield release, self, G.serverRrx

            derivadoA = random.uniform(a=0, b=0)

            #COMIENZA segundas conexiones, desde rayos x a las diferentes secciones según las probabilidades de la letra
            if 0 <= derivadoA < 0.3:
                print('Paciente ', self.id, ' es derivado desde ', G.serverRrx.unitName, 'a ', G.serverH.unitName,
                      ' en tiempo ', now())

                yield request, self, G.serverH
                print('Paciente ', self.id, ' derivado a ', G.serverH.unitName, ' en tiempo ', now())
                yield release, self, G.serverH

            elif 0.3 <= derivadoA < 0.4:
                print('Paciente ', self.id, ' es derivado desde ', G.serverRrx.unitName, 'a ', G.serverLab.unitName,
                      ' en tiempo ', now())

                yield request, self, G.serverLab
                print('Paciente ', self.id, ' derivado a ', G.serverLab.unitName, ' en tiempo ', now())

                tiempoServicioLab = abs(random.normalvariate(30, 6))

                yield hold, self, tiempoServicioLab
                print('Paciente ', self.id, ' finaliza tratamiento en tiempo ', now())
                yield release, self, G.serverLab


        elif 0.5 <= derivadoA < 0.55:
            print('Paciente ', self.id, ' es derivado al hospital en tiempo ', now())
            yield request, self, G.serverH
            yield release, self, G.serverH

        elif 0.55 <= derivadoA < 1:
            print('Paciente ', self.id, ' derivado al servicio de laboratorio en tiempo ', now())

            yield request, self, G.serverLab
            print('Paciente ', self.id, ' comienza a atenderse en el servicio de laboratorio en tiempo ', now())

            tiempoServicioLab = abs(random.normalvariate(30, 6))

            yield hold, self, tiempoServicioLab
            print('Paciente ', self.id, ' finaliza exámenes en tiempo ', now())

            yield release, self, G.serverLab

            derivadoA = random.uniform(a=0, b=0)

            # COMIENZA segundas conexiones, desde rayos x a las diferentes secciones según las probabilidades de la letra
            if 0 <= derivadoA < 0.1:
                print('Paciente ', self.id, ' es derivado desde ', G.serverLab.unitName, 'a ', G.serverH.unitName,
                      ' en tiempo ', now())

                yield request, self, G.serverH
                print('Paciente ', self.id, ' derivado a ', G.serverH.unitName, ' en tiempo ', now())
                yield release, self, G.serverH


class G:
    c = 1
    serverAt = Resource(c, 'Emergencia', 'At. Ambulatoria', monitored=True, monitorType=Monitor, qType=FIFO)
    serverRrx = Resource(c, 'Emergencia', 'Rayos X', monitored=True, monitorType=Monitor, qType=FIFO)
    serverH = Resource(c, 'Emergencia', 'Hospital', monitored=True, monitorType=Monitor, qType=FIFO)
    serverLab = Resource(c, 'Emergencia', 'Serv. de laboratorio', monitored=True, monitorType=Monitor, qType=FIFO)

    monitorHistograma = Monitor()


def model(c, N, lamb, mu, maxtime, rvseed):
    # inicialización del motor de simulación y semilla
    initialize()
    random.seed(rvseed)
   #  ejecución
    s = Arribos()
    activate(s, s.run(N, lamb, mu))
    simulate(until=maxtime)

    #%matplotlib inline

    print('-----------------------------------------------------------------------------------------')
    print('\n')
    print('Estadísticas finales: ')
    print('\n')
    print('Total atendidos en servicio ambulatorio: ', G.serverAt.actMon.total(),
          ' tiempo promedio de servicio', (G.serverAt.actMon.timeAverage() * 480)/G.serverAt.actMon.total(),
          ' tiempo promedio en la cola', (G.serverAt.waitMon.timeAverage() * 480) / G.serverAt.actMon.total())
    print('Desvio estandar: ', G.serverAt.actMon.var())
    print('Promedio: ', G.serverAt.actMon.mean())

    plt.plot(G.serverAt.waitMon.tseries(), G.serverAt.waitMon.yseries())
    plt.show()
    print('\n')


    print('Total atendidos en rayos x: ', G.serverRrx.actMon.total(),
          ' tiempo promedio de servicio', (G.serverRrx.actMon.timeAverage() * 480)/G.serverRrx.actMon.total(),
          ' tiempo promedio en la cola', (G.serverRrx.waitMon.timeAverage() * 480) / G.serverRrx.actMon.total())
    print('Desvio estandar: ', G.serverRrx.actMon.var())
    print('Promedio: ', G.serverRrx.actMon.mean())

    plt.plot(G.serverRrx.waitMon.tseries(), G.serverRrx.waitMon.yseries())
    plt.show()

    print('\n')

    print('Total atendidos en hospital: ', G.serverH.actMon.total(),
          ' tiempo promedio de servicio', (G.serverH.actMon.timeAverage() * 480)/G.serverH.actMon.total(),
          ' tiempo promedio en la cola', (G.serverH.waitMon.timeAverage() * 480) / G.serverH.actMon.total())
    print('Desvio estandar: ', G.serverH.actMon.var())
    print('Promedio: ', G.serverH.actMon.mean())

    plt.plot(G.serverH.waitMon.tseries(), G.serverH.waitMon.yseries())
    plt.show()

    print('\n')

    print('Total atendidos en laboratorio: ', G.serverLab.actMon.total(),' ', G.serverLab.waitMon.count(),
          ' tiempo promedio de servicio', (G.serverLab.actMon.timeAverage() * 480) / G.serverLab.actMon.total(),
          ' tiempo promedio en la cola', (G.serverLab.waitMon.timeAverage() * 480) / G.serverLab.actMon.total())
    print('Desvio estandar: ', G.serverLab.actMon.var())
    print('Promedio: ', G.serverLab.actMon.mean())

    plt.plot(G.serverLab.waitMon.tseries(), G.serverLab.waitMon.yseries())
    plt.show()


# Experimento
# lamb=tiempo entre arribos (media); mu=tiempo de servicio (media)
model(c=1, N=100, lamb=15, mu=3,
      maxtime=480, rvseed=234)
