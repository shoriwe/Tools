from string import ascii_letters, digits, punctuation, whitespace
from time import time
class Crunch:
    def __init__(self, letras=ascii_letters + digits + punctuation + whitespace, remover=''):
        self.letras = letras
        for caracter in remover:
            self.letras.replace(caracter, '')
        self.tamano = len(self.letras) - 1

    def generar(self, min_l,sep='', max_l=None, funcion=None,out_list=True):
        if max_l == None:
            max_l = min_l
        salida = []
        for numero in range(min_l, max_l + 1):
            puestos = [0 for x in range(numero)]
            for n in range((self.tamano + 1) ** numero):
                palabra, puestos = self._crear_palabra(puestos,sep)
                if out_list:
                    salida.append(palabra)
                if funcion != None:
                    funcion(palabra)
        if out_list:
            return salida

    def _actualizar_puestos(self, puestos):
        aumentar = True
        for n in range(len(puestos)):
            if puestos[n] <= self.tamano:
                if aumentar:
                    puestos[n] += 1
                    if puestos[n] > self.tamano:
                        puestos[n] = 0
                        aumentar = True
                    else:
                        aumentar = False
            else:
                puestos[n] = 0
        return puestos

    def _crear_palabra(self, puestos,sep):
        salida = '{}'.format(sep).join(self.letras[n] for n in puestos)
        puestos = self._actualizar_puestos(puestos)
        return salida, puestos
