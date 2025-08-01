import simpy
import random
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# Parámetros de la simulación
random.seed(42)  # Para reproducibilidad
TIEMPO_SIMULACION = 4 * 60 * 60  # 4 horas en segundos (de 11:00 a 15:20)
CAPACIDAD_SALON_ROJO = 30
CAPACIDAD_SALON_AZUL = 20

# Funciones para generar tiempos aleatorios
def tiempo_llegada():
    return random.uniform(30, 90)  # 60 +/- 30 segundos

def tiempo_atencion_caja():
    return random.uniform(15, 45)  # 30 +/- 15 segundos

def tiempo_preparacion_local():
    return random.uniform(80, 100)  # 90 +/- 10 segundos

def tiempo_preparacion_llevar():
    return random.uniform(100, 140)  # 120 +/- 20 segundos

def tiempo_permanencia_salon(horario, salon):
    if salon == 'rojo':
        if horario == '11-12':
            return random.uniform(5 * 60, 35 * 60)  # 20 +/- 15 minutos
        elif horario == '12-13:30':
            return random.uniform(15 * 60, 45 * 60)  # 30 +/- 15 minutos
        elif horario == '13-14:35':
            return random.uniform(20 * 60, 50 * 60)  # 35 +/- 15 minutos
        elif horario == '14-15:20':
            return random.uniform(5 * 60, 35 * 60)  # 20 +/- 15 minutos
    elif salon == 'azul':
        if horario == '11-12':
            return random.uniform(20 * 60, 40 * 60)  # 30 +/- 10 minutos
        elif horario == '12-13:30':
            return random.uniform(30 * 60, 50 * 60)  # 40 +/- 10 minutos
        elif horario == '13-14:35':
            return random.uniform(35 * 60, 55 * 60)  # 45 +/- 10 minutos
        elif horario == '14-15:20':
            return random.uniform(25 * 60, 45 * 60)  # 35 +/- 10 minutos

# Función para determinar el horario actual
def obtener_horario(tiempo):
    if tiempo < 60 * 60:
        return '11-12'
    elif tiempo < 90 * 60:
        return '12-13:30'
    elif tiempo < 155 * 60:
        return '13-14:35'
    else:
        return '14-15:20'

# Clase para el negocio de hamburguesas
class Hamburgueseria:
    def __init__(self, environment):
        self.env = environment
        self.caja = simpy.Resource(environment, capacity=1)
        self.mostrador = simpy.Resource(environment, capacity=3)
        self.salon_rojo = simpy.Container(environment, init=0, capacity=CAPACIDAD_SALON_ROJO)
        self.salon_azul = simpy.Container(environment, init=0, capacity=CAPACIDAD_SALON_AZUL)
        self.cola_caja = []
        self.cola_mostrador = []
        self.datos = []

    def atender_cliente(self, cliente):
        with self.caja.request() as req:
            yield req
            tiempo_llegada_cola = self.env.now
            yield self.env.timeout(tiempo_atencion_caja())
            tiempo_salida_cola = self.env.now
            tiempo_cola = tiempo_salida_cola - tiempo_llegada_cola
            self.cola_caja.append(tiempo_cola)

            if random.random() < 0.2:
                # Pedido para llevar
                yield self.env.timeout(tiempo_preparacion_llevar())
            else:
                # Pedido para consumir en el local
                yield self.env.timeout(tiempo_preparacion_local())
                salon = 'rojo' if random.random() < 0.3 else 'azul'
                if salon == 'rojo':
                    yield self.salon_rojo.put(1)
                    tiempo_permanencia = tiempo_permanencia_salon(obtener_horario(self.env.now), 'rojo')
                    yield self.env.timeout(tiempo_permanencia)
                    yield self.salon_rojo.get(1)
                else:
                    yield self.salon_azul.put(1)
                    tiempo_permanencia = tiempo_permanencia_salon(obtener_horario(self.env.now), 'azul')
                    yield self.env.timeout(tiempo_permanencia)
                    yield self.salon_azul.get(1)

            # Retirar el pedido en el mostrador
            with self.mostrador.request() as req_mostrador:
                yield req_mostrador
                yield self.env.timeout(5)  # Tiempo para retirar el pedido

            self.datos.append({
                'tiempo_permanencia': self.env.now - cliente['tiempo_llegada'],
                'tiempo_cola_caja': tiempo_cola,
                'salon': salon if 'salon' in locals() else None,
                'salon_rojo': self.salon_rojo.level,
                'salon_azul': self.salon_azul.level
            })

    def generar_clientes(self):
        i = 0
        while True:
            yield self.env.timeout(tiempo_llegada())
            i += 1
            cliente = {'id': i, 'tiempo_llegada': self.env.now}
            self.env.process(self.atender_cliente(cliente))

    def monitorear_colas(self):
        while True:
            yield self.env.timeout(15 * 60)  # Cada 15 minutos
            self.cola_mostrador.append(len(self.mostrador.queue))

    def monitorear_salones(self):
        while True:
            yield self.env.timeout(30 * 60)  # Cada 30 minutos
            self.datos.append({
                'salon_rojo': self.salon_rojo.level,
                'salon_azul': self.salon_azul.level
            })

# Configuración de la simulación
env = simpy.Environment()
hamburgueseria = Hamburgueseria(env)
env.process(hamburgueseria.generar_clientes())
env.process(hamburgueseria.monitorear_colas())
env.process(hamburgueseria.monitorear_salones())

# Ejecutar la simulación
env.run(until=TIEMPO_SIMULACION)

# Análisis de resultados
df = pd.DataFrame(hamburgueseria.datos)

# Guardar resultados en un archivo CSV
df.to_csv('resultados_simulacion.csv', index=False)

# Crear la interfaz gráfica


# Función para mostrar gráficos
def mostrar_graficos():
    plt.figure(figsize=(12, 8))

    # Gráfico de tiempo de permanencia
    plt.subplot(2, 2, 1)
    sns.histplot(df['tiempo_permanencia'], kde=True)
    plt.title('Distribución del Tiempo de Permanencia')
    plt.xlabel('Tiempo (segundos)')
    plt.ylabel('Frecuencia')

    # Gráfico de tiempo en cola en la caja
    plt.subplot(2, 2, 2)
    sns.histplot(df['tiempo_cola_caja'], kde=True)
    plt.title('Distribución del Tiempo en Cola en la Caja')
    plt.xlabel('Tiempo (segundos)')
    plt.ylabel('Frecuencia')



    # Gráfico de cantidad de personas en los salones
    plt.subplot(2, 2, 4)
    df_salones = df[['salon_rojo', 'salon_azul']].dropna()
    plt.plot(df_salones.index, df_salones['salon_rojo'], label='Salón Rojo')
    plt.plot(df_salones.index, df_salones['salon_azul'], label='Salón Azul')
    plt.title('Cantidad de Personas en los Salones')
    plt.xlabel('Tiempo (segundos)')
    plt.ylabel('Cantidad de Personas')
    plt.legend()

    plt.tight_layout()
    plt.show()

mostrar_graficos()