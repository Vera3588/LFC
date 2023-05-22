import random
import string
from tabulate import tabulate

#gramatica por entrada
gramatica = {}
cfg = True
try:
    while(cfg):
        lenguaje = input("Ingrese el CFG: ")
        if lenguaje == "":
            cfg = False
        else:
            for linea in lenguaje.split('\n'):
                izq, der = linea.split(' -> ')
                gramatica[izq] = der.split(' | ')
except:
    print("Error al definir CFG")
    cfg = False

# reunimos todos los no terminales con valores vacio
first = {nt: set() for nt in gramatica.keys()}

def First(nTerminal, visited=None):
    '''
        modificamos el first, por si la gramatica tiene recursividad
        1. Si el conjunto First de este no terminal ya se ha calculado, devuleve el conjunto existente
        2. Conjunto para realizar el seguimiento de los no terminales visitados en la recursión
        3. Verificar si el no terminal ya ha sido visitado en la recursión actual
    '''
    if first[nTerminal]:
        return first[nTerminal]
    if visited is None:
        visited = set()
    if nTerminal in visited:
        return first[nTerminal]
    visited.add(nTerminal)

    '''
    Calcula el conjunto First del no terminal actual
        1. Si deriva en una cadena vacía, agrega ε a First
        2. Si la producción comienza con un símbolo terminal, agrega ese símbolo a First
        3. Si la producción comienza con un símbolo no terminal, calcula el conjunto 
            First de ese no terminal y agrega los elementos a First.
        3.1. si el no terminal no deriva en epsilon, no debe continuar calculando first
    '''
    for produ in gramatica[nTerminal]:
        if produ == 'ε':
            first[nTerminal].add('ε')
        elif produ[0] not in gramatica.keys():
            first[nTerminal].add(produ[0])
        else:
            for simbolo in produ:
                first_simbolo = First(simbolo, visited)
                first[nTerminal] |= first_simbolo
                if 'ε' not in first_simbolo:
                    first[nTerminal] -= {'ε'}
                    break
    visited.remove(nTerminal)
    return first[nTerminal]

# se agrega al conjunto vacio de first
for nTerminal in gramatica.keys():
    First(nTerminal)

# reunirmos todos los no terminales con valores vacios
follow = {nt: set() for nt in gramatica.keys()}

# Agregamos el símbolo de '$' al conjunto Follow de la primera produccion obligatoriamente
lista_nTerminales = list(gramatica.keys())
follow[lista_nTerminales[0]].add('$')

def Follow(nTerminal):
    for left_nTerminal, producciones in gramatica.items():
        for produ in producciones:
            for i, simbolo in enumerate(produ):
                if simbolo == nTerminal:
                    if i == len(produ) - 1:
                        # Si el no terminal está al final de la producción, agrega el conjunto Follow del no terminal de la izquierda al conjunto Follow del no terminal actual
                        if left_nTerminal != nTerminal:
                            follow[nTerminal] |= Follow(left_nTerminal)
                    else:
                        '''
                        en el caso de Si el no terminal no está al final de la producción.

                        Si el siguiente símbolo es un no terminal, agrega el conjunto First del 
                        siguiente símbolo al conjunto Follow del no terminal actual,
                        a menos que ese conjunto contenga la cadena vacía (ε), en cuyo caso 
                        se agrega el conjunto Follow del no terminal de la izquierda
                        '''

                        next_simbolo = produ[i+1]
                        if next_simbolo in gramatica.keys():
                            
                            follow_next_simbolo = First(next_simbolo)
                            follow[nTerminal] |= (follow_next_simbolo - {'ε'})
                            if 'ε' in follow_next_simbolo:
                                follow[nTerminal] |= Follow(next_simbolo)
                        else:
                            # Si el siguiente símbolo es un terminal, simplemente agrégalo al conjunto Follow del no terminal actual
                            follow[nTerminal].add(next_simbolo)
    return follow[nTerminal]

# Calcula los conjuntos Follow de todos los no terminales
for nTerminal in gramatica.keys():
    Follow(nTerminal)

print("FIRST:")
# Imprime los conjuntos First
for nt, f in first.items():
    print(f"First({nt}) = {f}")

print("Follow:")
# Imprime los conjuntos Follow
for nt, f in follow.items():
    print(f"Follow({nt}) = {f}")


def Closure(items):
    closure_i = set(items)
    '''
        se coloca el punto al inicio de cada produccion, y si ya tiene el punto lo pone en la siguiente posicion,
        hasta que llegue al final
    '''
    while True:
        nItems = set()
        for item in closure_i:
            produccion = item[1]
            punto = item[2]
            if punto < len(produccion) and produccion[punto] in gramatica.keys():
                nTerminal = produccion[punto]
                for produ in gramatica[nTerminal]:
                    new_item = (nTerminal, produ, 0)
                    if new_item not in closure_i:
                        nItems.add(new_item)
        if not nItems:
            break
        closure_i |= nItems
    return closure_i

def Goto(items, X):
    goto_items = set()
    for item in items:
        produccion = item[1]
        punto = item[2]
        if punto < len(produccion) and produccion[punto] == X:
            nItem = (item[0], produccion, punto + 1)
            goto_items.add(nItem)
    return Closure(goto_items)

def Tabla():
    tabla = {}

    # Construir los conjuntos LR(0) canónicos
    produccion_ini = list(gramatica.keys())[0]
    item_ini = (produccion_ini, gramatica[produccion_ini][0], 0)
    set_ini = Closure({item_ini})
    item_sets = [set_ini]

    i = 0
    while i < len(item_sets):
        item_set = item_sets[i]
        print(f"I{i}: {item_set}")  # Imprimir el conjunto de elementos actual
        for item in item_set:
            produccion = item[1]
            punto = item[2]

            if punto < len(produccion):
                siguiente_simbolo = produccion[punto]
                siguiente_set = Goto(item_set, siguiente_simbolo)
                if siguiente_set and siguiente_set not in item_sets:
                    item_sets.append(siguiente_set)
        i += 1
    # Construir la tabla de análisis sintáctico
    for i, item_set in enumerate(item_sets):
        tabla[i] = {}

        for item in item_set:
            produccion = item[1]
            punto = item[2]

            if punto < len(produccion):
                siguiente_simbolo = produccion[punto]
                if siguiente_simbolo in gramatica.keys():
                    goto_set = Goto(item_set, siguiente_simbolo)
                    if goto_set in item_sets:
                        tabla[i][siguiente_simbolo] = ('goto', item_sets.index(goto_set))
                else:
                    # Shift: mover el punto a la siguiente posición y cambiar de estado
                    shift = Goto(item_set, siguiente_simbolo)
                    if shift in item_sets:
                        tabla[i][siguiente_simbolo] = ('shift', item_sets.index(shift))
        # Añadir los reduces en el estado actual
        for item in item_set:
            produccion = item[1]
            punto = item[2]
            if punto == len(produccion):
                if item[0] == produccion_ini and item[1] == gramatica[produccion_ini][0]:
                    tabla[i]['$'] = 'accept'
                else:
                    for terminal in follow[item[0]]:
                        if terminal != 'ε':
                            if terminal in tabla[i]:
                                # Error: Conflicto en la tabla de análisis sintáctico
                                raise Exception('Error: Conflicto en la tabla de análisis sintáctico no es LR(0)')
                            tabla[i][terminal] = ('reduce', item[0], item[1])
    return tabla

# Construir la tabla de análisis sintáctico
parser = Tabla()
print(parser)
# Imprimir la tabla de análisis sintáctico

def Mostrar_tabla(parser):
    terminales = list(set([simbol for estado in parser for simbol in parser [estado]]))
    terminales.sort()

    datos = []
    for estado, acciones in parser.items():
        row = [f"I{estado}"]
        for simbolo in terminales:
            if simbolo in acciones:
                accion = acciones[simbolo]
                if accion[0] == 'shift':
                    row.append(f"S{accion[1]}")
                elif accion[0] == 'reduce':
                    row.append(f"R{accion[1]}")
                elif accion[0] == 'goto':
                    row.append(f"{accion[1]}")
                elif accion == 'accept':
                    row.append("Accept")
            else:
                row.append("")
        datos.append(row)

    headers = [""] + terminales
    table = tabulate(datos, headers, tablefmt="grid")
    print("Tabla de análisis sintáctico:")
    print(table)
Mostrar_tabla(parser)

def Analizar_cadena(parser, input_):
    stack = [0]  # Pila de estados
    simbolos = ['$'] + list(input_)  # Cadena de entrada
    output = []  # Producciones de la gramática aplicadas

    while True:
        estado = stack[-1]
        simbolo = simbolos[0]

        if simbolo in parser[estado]:
            accion = parser[estado][simbolo]

            if accion == 'accept':
                print("La cadena es válida.")
                return output
            elif accion[0] == 'shift':
                stack.append(simbolo)
                stack.append(accion[1])
                simbolos = simbolos[1:]
            elif accion[0] == 'reduce':
                nTerminal = action[1]
                produccion = action[2]
                reduce_length = len(grammar[nTerminal][produccion])  # Longitud de la producción a reducir
                for _ in range(2 * reduce_length):
                    stack.pop()
                state = stack[-1]
                stack.append(nTerminal)
                stack.append(parser[estado][nTerminal])
                output.append((nTerminal, gramatica[nTerminal][produccion]))
        else:
            print("La cadena no es válida.")
            return output



tabla = Tabla()
print(tabla)
datos = []
with open("input.txt") as cadenas:
    for lineas in cadenas:
        datos.extend(lineas.split())
print (datos)
output = []
i = 0
while i < len(datos):
    aux = Analizar_cadena(datos[i], tabla)
    output.extend(aux)
    i+=1
print(output)  
with open("output.txt","w") as respuesta:
    j=0
    while j < len(datos):
        respuesta.write(f"{output[j]}\n")
        j+=1