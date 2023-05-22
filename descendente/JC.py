import random
import string

#gramatica por entrada
new_gramatica = {}
cfg = True
try:
    while(cfg):
        lenguaje = input("Ingrese el CFG: ")
        if lenguaje == "":
            cfg = False
        else:
            for linea in lenguaje.split('\n'):
                izq, der = linea.split(' -> ')
                new_gramatica[izq] = der.split(' | ')
except:
    print("Error al definir CFG")
    cfg = False

'''
#casos de prueba aleatorios:
import gramaticas as cfg
new_gramatica = cfg.cfg_tratada ['producciones']
'''

# se crea para generar un no terminal aleatorio para eliminarle recursividad por izquierda a una gramatica porque no 
# reconoce por ejemplo S'
def nTerminal_aleatorio(gramatica):
    # Generamos un sufijo aleatorio
    sufijo = ''.join(random.choices(string.ascii_lowercase, k=1))
    sufijo = sufijo.upper()
    # Verificamos si el sufijo ya está presente en la gramática
    for nTerminal in gramatica:
        if nTerminal.endswith(sufijo):
            return nTerminal_aleatorio(gramatica)
    return sufijo

def Eliminar_r_izq(gramatica):
    new_Gramatica = {}

    for nTerminal in gramatica:
        producciones = gramatica[nTerminal]
        new_producciones = []
        
        recursion = False
        rProducciones = []
        no_rProducciones = []
        # Verificamos si hay recursividad izquierda en el caso de que la primera letra sea un nTerminal
        for produccion in producciones:
            if produccion[0] == nTerminal:
                recursion = True
                rProducciones.append(produccion[1:])
            else:
                no_rProducciones.append(produccion)
        # Generar una nueva variable no terminal para las producciones recursivas
        if recursion:
            new_nTerminal = nTerminal_aleatorio(gramatica)
            new_producciones += [alpha + new_nTerminal for alpha in rProducciones]
            new_producciones += no_rProducciones + ['ε']
            new_Gramatica[nTerminal] = [produccion + new_nTerminal for produccion in no_rProducciones]
            new_Gramatica[new_nTerminal] = [produccion + new_nTerminal for produccion in rProducciones] + ['ε']
        else:
            new_Gramatica[nTerminal] = producciones

    return new_Gramatica

#ahora tenemos la nueva gramatica sin recursividad izq
gramatica = Eliminar_r_izq(new_gramatica)

# reunimos todos los no terminales con valores vacios
first = {nTerminal: set() for nTerminal in gramatica.keys()}

def First(nTerminal):
    # Si el conjunto First de este no terminal ya se ha calculado, retorna el conjunto existente
    if first[nTerminal]:
        return first[nTerminal]
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
                simbolo_first = First(simbolo)
                first[nTerminal] |= simbolo_first
                if 'ε' not in simbolo_first:
                    first[nTerminal] -= {'ε'}
                    break
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

# Verifica si la gramática es LL(1)
def gramatica_LL1(gramatica, first, follow):

    # Comprueba si hay más de una producción por no terminal que empieza con el mismo símbolo
    for nTerminal, producciones in gramatica.items():
        start_simbolos = set()
        for produ in producciones:
            simbolo = produ[0]
            if simbolo in  start_simbolos:
                return False
            start_simbolos.add(simbolo)
    '''
    Comprueba si cada producción empieza con un símbolo que no es un no terminal o,
    en su defecto, si el conjunto First de los símbolos iniciales de cada producción es disjunto
    '''
    for nTerminal, producciones in gramatica.items():
        start_simbolos = set()
        for produ in producciones:
            simbolo = produ[0]
            if simbolo not in gramatica.keys():
                if simbolo in start_simbolos:
                    return False
                start_simbolos.add(simbolo)
            else:
                if len(first[simbolo] & follow[nTerminal]) > 0:
                    return False
    return True

def Tabla(gramatica, first, follow):
    tabla = {}
    '''
        - Para cada no terminal Creamos una entrada en la tabla de análisis sintáctico.
    '''
    for nTerminal in gramatica.keys():
        tabla[nTerminal] = {}

        '''
            - Para cada producción del no terminal
            Si la producción deriva en ε, agrega la acción ε a todas las entradas
            de la tabla de análisis sintáctico correspondientes a los símbolos en 
            el conjunto Follow del no terminal.
        '''
        for produ in gramatica[nTerminal]:

            if produ == 'ε':
                for simbolo in follow[nTerminal]:
                    tabla[nTerminal][simbolo] = 'ε'
            else:
                # Calculamos el conjunto First de la producción
                first_produ = set()
                for simbolo in produ:
                    if simbolo in gramatica.keys():
                        first_simbolo = first[simbolo]
                        if 'ε' not in first_simbolo:
                            first_produ |= first_simbolo
                            break
                        else:
                            first_produ |= (first_simbolo - {'ε'})
                    else:
                        first_produ.add(simbolo)
                        break
                '''
                    Agregamos a la tabla de análisis sintáctico el First de la producción,
                    con la acción correspondiente
                '''
                for simbolo in first_produ:
                    tabla[nTerminal][simbolo] = produ
                '''
                    Si ε está en el First, agrega la acción ε a todos
                    los símbolos del Follow del no terminal en la tabla
                '''
                if 'ε' in first_produ:
                    for simbolo in follow[nTerminal]:
                        parsing_table[nTerminal][simbolo] = 'ε'
    return tabla


def Analizar_cadena(input_, tabla):
    # Inicializa la pila con el símbolo de fin de cadena ($) y el símbolo inicial de la gramatica
    stack = ['$',lista_nTerminales[0]]  
    output = []  # podemos Almacenar los pasos del análisis, pero solo se requiere de salida si y no
    input_ = f"{input_}$"
    #print(f"go{input_}")
    # Itera hasta que la pila esté vacía o se haya analizado toda la entrada
    while len(stack) > 0 and len(input_) > 0:
        top = stack[-1]  # Obtiene el símbolo en la cima de la pila
        current_input = input_[0]  # Obtiene el símbolo actual de la entrada
        if top == current_input:
            '''
                Si el símbolo en la cima de la pila coincide con el símbolo actual de la entrada un terminal,
                pues se hace pop y se libera
            '''
            stack.pop()
            input_ = input_[1:]
            #output.append(f"entró {current_input}")
        elif top in tabla and current_input in tabla[top]:
            '''
                Si el símbolo en la cima de la pila es un no terminal y hay una entrada 
                correspondiente en la tabla de análisis sintáctico,
                se busca en lo que deriva hasta encontrar el terminal.
            '''
            production = tabla[top][current_input]
            stack.pop()
            if production != 'ε':
                stack += list(production)[::-1]  # Agrega los símbolos de la producción en orden inverso a la pila
            #output.append(f"produccion: {top} -> {production}")
        elif top == 'ε':
            # Si el símbolo en el top de la pila es ε, se hace pop y se libera
            stack.pop()
            #output.append(f"encontró ε")
        else:
            # ya Si no encuenta coincidencias en la pila y la entrada, se produce un error
            #output.append(f"Error: {current_input} no encontró camino")
            break
    #entonces comprobamos la entrada y la pila
    if len(stack) == 0 and len(input_) == 0:
        #Si la pila y la entrada están vacías al mismo tiempo, la cadena es válida
        output.append("si")
    else:
        # Si la pila o la entrada no están vacías, la cadena es inválida
        output.append("no")
    return output

print("FIRST:")
# Imprime los conjuntos First
for nt, f in first.items():
    print(f"First({nt}) = {f}")
print("Follow:")
# Imprime los conjuntos Follow
for nt, f in follow.items():
    print(f"Follow({nt}) = {f}")

ll1 = gramatica_LL1(gramatica, first, follow)
def Solucion(ll1):
    if ll1 == True:
        #si es ll(1) construimos la tabla para procesar cadenas
        print("la gramatica es LL(1)")
        tabla = Tabla(gramatica, first, follow)
        print(tabla)
        #lee los datos linea por linea y los guardo en un arreglo
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
    else:
        print("la gramatica NO es LL(1)")
Solucion(ll1)