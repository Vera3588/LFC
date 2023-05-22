import random
import string

grammar = {}

def NTerminal_aleatorio(grammar):
    # Generar un sufijo aleatorio
    suffix = ''.join(random.choices(string.ascii_lowercase, k=1))
    suffix = suffix.upper()
    # Verificar si el sufijo ya está presente en la gramática
    for non_terminal in grammar:
        if non_terminal.endswith(suffix):
            return NTerminal_aleatorio(grammar)
    return suffix

def Terminal_aleatorio(grammar):
    # Generar una elección aleatoria entre sufijo o épsilon
    choices = ['suffix', 'epsilon']
    choice = random.choice(choices)

    if choice == 'suffix':
        # Generar un sufijo aleatorio
        suffix = ''.join(random.choices(string.ascii_lowercase, k=1))
        # Verificar si el sufijo ya está presente en la gramática
        for non_terminal in grammar:
            if non_terminal.endswith(suffix):
                return Terminal_aleatorio(grammar)
        return suffix
    else:
        return 'ε'

def generar_cfg_random(num_terminales, num_no_terminales, num_producciones, grammar):
    terminales = set(Terminal_aleatorio(grammar) for _ in range(num_terminales))

    no_terminales = set(NTerminal_aleatorio(grammar) for _ in range(num_no_terminales))
    producciones = {}

    for nt in no_terminales:
        producciones[nt] = []
        for _ in range(num_producciones):
            # Generar una producción con al menos un terminal
            produccion = ''
            while not any(t in produccion for t in terminales):
                produccion = ''.join(random.choice(list(terminales | no_terminales)) for _ in range(random.randint(1, 3)))
            producciones[nt].append(produccion)

    inicial = random.choice(list(no_terminales))

    cfg = {
        'terminales': terminales,
        'no_terminales': no_terminales,
        'producciones': producciones,
        'inicial': inicial
    }

    return cfg

def tratamientoCFG(cfg):
    new_producciones = {}

    for nt, producciones in cfg['producciones'].items():
        new_producciones[nt] = []

        for produccion in producciones:
            if produccion == 'ε':
                new_producciones[nt].append('ε')
            else:
                # Reemplazar 'ε' por eliminar las ocurrencias
                nueva_produccion = produccion.replace('ε', '')
                if nueva_produccion == '':
                    new_producciones[nt].append('ε')
                else:
                    new_producciones[nt].append(nueva_produccion)

    cfg['producciones'] = new_producciones

    return cfg

cfg_random = generar_cfg_random(3, 2, 2, grammar)
cfg_tratada = tratamientoCFG(cfg_random)
print(cfg_tratada)

grammar = cfg_tratada ['producciones']
print(grammar)

def Cadena():
    # Generar un sufijo aleatorio
    x = list(cfg_tratada['terminales'])
    suffix = ''.join(random.choices(x,k=random.randint(1, 10)))
    if "ε" in suffix:
        suffix = suffix.replace('ε', '')
    return suffix


    

with open("input.txt", "w") as cadenas:
            j=0
            while j < 10:
                cadenas.write(f"{Cadena()}\n")
                j+=1


