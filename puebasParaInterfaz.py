import sqlite3
from random import randint, choice

# Conexión a la base de datos
conn = sqlite3.connect('CRU_database.db')
cursor = conn.cursor()

# Creación de la tabla TopeFormaciones
cursor.execute('''CREATE TABLE IF NOT EXISTS TopeFormaciones (
                    id_Formacion INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
                    Formacion TEXT NOT NULL UNIQUE,
                    base_md INTEGER,
                    tope_md INTEGER,
                    espesor_md INTEGER
                )''')

# Creación de la tabla Metadata
cursor.execute('''CREATE TABLE IF NOT EXISTS Metadata (
                    id_metadata INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
                    Formacion TEXT NOT NULL,
                    compañia TEXT NOT NULL,
                    nombre_pozo TEXT NOT NULL,
                    fecha_inicio DATE,
                    fecha_final DATE,
                    longitud REAL,
                    latitud REAL
                )''')

# Creación de la tabla EditTopeFormaciones
cursor.execute('''CREATE TABLE IF NOT EXISTS EditTopeFormaciones (
                    id_Formacion INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
                    Formacion TEXT NOT NULL UNIQUE,
                    base_md INTEGER,
                    tope_md INTEGER,
                    espesor_md INTEGER,
                    FOREIGN KEY (Formacion) REFERENCES TopeFormaciones(Formacion)
                )''')

# Creación de la tabla EditMetadata
cursor.execute('''CREATE TABLE IF NOT EXISTS EditMetadata (
                    id_metadata INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
                    Formacion TEXT NOT NULL,
                    compañia TEXT NOT NULL,
                    nombre_pozo TEXT NOT NULL,
                    fecha_inicio DATE,
                    fecha_final DATE,
                    longitud REAL,
                    latitud REAL,
                    FOREIGN KEY (Formacion) REFERENCES Metadata(Formacion)
                )''')

# Guardar los cambios y cerrar la conexión
conn.commit()
conn.close()

print("Base de datos creada exitosamente.")


# Conexión a la base de datos
conn = sqlite3.connect('CRU_database.db')
cursor = conn.cursor()

# Función para generar valores aleatorios de fechas
def random_date():
    year = randint(2022, 2023)
    month = randint(1, 12)
    day = randint(1, 28)  # Para simplificar, asumimos que todos los meses tienen 28 días
    return f"{year}-{month:02d}-{day:02d}"

# Valores proporcionados
Formacion = ['Cansona', 'San Cayetano', 'Toluviejo', 'El Carmen', 'Porquero', 'Carrito', 'Sincelejo', 'Betulia']
compañia = ['Canacol Energy', 'CNE Oil and Gas SAS', 'Geoproduction Oil and Gas Company', 'Hocol', 'Ecopetrol', 'Cleanenergy Resources S.A.S', 'Captiva Resources LLC']
nombre_pozo = ['Pueblo Nuevo', 'Sahagún', 'Ciénaga de Oro', 'Chinú', 'Ayapel', 'Planeta Rica', 'Montería', 'Lorica']

# Inserción de datos en la tabla TopeFormaciones
for formacion in Formacion:
    tope_md = randint(0, 6400)
    base_md = randint(0, tope_md)
    espesor_md = tope_md - base_md
    cursor.execute("INSERT INTO TopeFormaciones (Formacion, base_md, tope_md, espesor_md) VALUES (?,?,?,?)", (formacion, base_md, tope_md, espesor_md))

# Inserción de datos en la tabla Metadata
for formacion in Formacion:
    fecha_inicio = '2022-01-01'  # fecha_inicio proporcionada
    fecha_final = '2024-04-01'   # fecha_final proporcionada
    longitud = randint(70, 75)   # Valor aleatorio para longitud
    latitud = randint(-5, 5)     # Valor aleatorio para latitud
    compania_random = choice(compañia)  # Se elige una compañía aleatoria
    pozo_random = choice(nombre_pozo)   # Se elige un pozo aleatorio
    cursor.execute("INSERT INTO Metadata (Formacion, compañia, nombre_pozo, fecha_inicio, fecha_final, longitud, latitud) VALUES (?,?,?,?,?,?,?)", (formacion, compania_random, pozo_random, fecha_inicio, fecha_final, longitud, latitud))

# Guardar los cambios y cerrar la conexión
conn.commit()
conn.close()

print("Datos insertados exitosamente.")
