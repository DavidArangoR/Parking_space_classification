#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 26 20:17:06 2019

@author: david
"""

import cv2
import numpy as np
import os
from tkinter import *
import sys

class plazas():

    def __init__(self,num_plazas,dp,dpy): # PARA INSTANCIAR EL OBJETO ESCRIBIR (self,n_plazas,img)

        self.refPt = []          # Lista de puntos de Plaza
        self.plazas = []         # Lista de listas de Plazas
        self.n_plazas = num_plazas
        self.n_puntos_plaza = 1  # numero de puntos por plaza
        self.puntos_centro = []  # Lista de puntos centrales de cada plaza definida
        self.dp = dp
        self.dpy = dpy
        self.indice_puntos = 0   # Contador auxiliar numero de puntos en lista de Plaza
        self.indice_plazas = 0   # Contador auxiliar numero de listas en lista de Plazas
        self.nueva_plaza = True
        self.path ='Regiones'

    # FUNCION DE ROI
    def roi_select(self,event,x,y,flags,param):

        if (event == cv2.EVENT_LBUTTONDBLCLK):
            # si la bandera es True y el numero de plazas < a la cantidad seleccionada
            if self.nueva_plaza == True and len(self.refPt) <= self.n_puntos_plaza -1:

                if self.indice_puntos == 0:
                    self.refPt = [(x,y)]
                else:
                    self.refPt.append(x,y)

            if self.indice_puntos == self.n_puntos_plaza:
                self.nueva_plaza = False
                #indice_puntos = 0
            self.indice_puntos = self.indice_puntos+1
            print('numero de puntos plaza',self.indice_puntos)
            print('punto seleccionado {},{}'.format(x,y))
            print('vector almacenado ', self.refPt)

    def guardarplazas(self):
        textmessage = 'Presione doble click en cada zona de parqueo.\n Cuando aparezca el punto indicador presione la tecla G y repita el proceso con las zonas restantes. \n Presione la tecla ESC para finalizar'
        messagebox.showinfo(message=textmessage, title="Información")
        #imagen = cv2.imread('zona1_10am.jpg') # prueba con una imagen
        captura = cv2.VideoCapture('entradacarro.mp4')
        cv2.namedWindow('Video',cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Video',(800,800))
        cv2.setMouseCallback('Video',self.roi_select)

        while True:
            #Capturamos frame a frame
            (grabbed, imagen) = captura.read()

            # Si hemos llegado al final del vídeo salimos
            if not grabbed:
                break
            img = imagen.copy()
            img_copy = img.copy()
            '''
            --------------------------------------------
            DIBUJAR EL PUNTO SELECCIONADO SOBRE LA IMAGEN
            ---------------------------------------------
            '''
            if len(self.refPt) > 0 & len(self.refPt) <= self.n_puntos_plaza -1:

                for i in self.refPt:
                    pt = i  # variable con las coordenadas xy del punto
                    cv2.circle(img,pt,5,(0,0,255),-1)

                cv2.putText(img,'CANTIDAD PLAZAS SELECCIONADAS: '+ str(self.indice_plazas),(10,40),
                            cv2.FONT_HERSHEY_DUPLEX,0.5,(0,0,255),1)

            cv2.imshow('Video', img)
            key = cv2.waitKey(1) & 0xFF

            '''
            TECLA DE GUARDAR
            '''
            if key == ord("g"):
                if self.indice_plazas <= (self.n_plazas-1) and len(self.refPt) == self.n_puntos_plaza:   # la siguiente condicion se ejecuta de acuerdo al numero de plazas definidas inicialmente para el parqueadero
                    if self.indice_plazas == 0: # adicionar el primer elemento a lista de plazas
                        self.plazas = [self.refPt]
                    else:
                        self.plazas.append(self.refPt)

                    arreglo_p = self.plazas[self.indice_plazas] # con esta linea se toma el valor de cada posicion del arreglo plazas
                    c = 0
                    suma_x = 0
                    suma_y = 0

                    ''' Comprobar si no se ha seleccionado una ROI cercana al borde de la imagen'''
                    try:
                        for p in arreglo_p:
                            (x , y) = p
                            roi = img_copy[y-(self.dpy) : y+(self.dpy) , x-self.dp : x+self.dp]
                            roi = cv2.resize(roi, (64, 64))
                            filename = 'p'+str(self.indice_plazas+1)+'-'+str(c+1)+'.jpg'

                            cv2.imwrite(os.path.join(self.path , filename), roi)
                            c = c+1
                            suma_x = suma_x + x  # acumulador coordenada x
                            suma_y = suma_y + y  # acumulador coordenada y
                    except cv2.error:
                        error = 'Region cecana al borde de la imagen, intentelo de nuevo'
                        print(error)
                        self.plazas = []
                        self.indice_plazas = -1
                        pass
                    ''' -----------------'''
                    coord_x = int(suma_x)
                    coord_y = int(suma_y)
                    print('coordenadas {} {}'.format(coord_x, coord_y ))

                    if self.indice_plazas == 0: # Creacion de puntos centrales de plaza
                            self.puntos_centro = [(coord_x,coord_y)]
                    else:
                            self.puntos_centro.append((coord_x,coord_y))

                     #------ contador de plazas seleccionadas
                    self.indice_plazas = self.indice_plazas + 1
                    print('cantidad plazas: ',self.indice_plazas)
                    print('vector puntos centro', self.puntos_centro)
                    self.nueva_plaza = True
                    self.refPt = []
                    self.indice_puntos = 0
                else:
                    print('Faltan puntos por definir')

            if self.indice_plazas == self.n_plazas:
                print('Se definiron {} plazas!'.format(self.indice_plazas))
                arreglo_final = np.array(self.plazas,dtype=np.int32)
                np.save('Arreglo_Final', arreglo_final)
                arreglo_pt_centrales = np.array(self.puntos_centro,dtype=np.int32)
                print(arreglo_pt_centrales)
                np.save('Arreglo_pt_centrales', arreglo_pt_centrales)
                #captura.release()
                break
            """
            -------------------------------------------------------------------
            GUARDAR ARREGLO DE PLAZA EN LISTA DE PLAZAS
            """
            if key == ord("b"):
                self.nueva_plaza = True
                self.refPt = []
                self.indice_puntos = 0
                print('Eliminaste plaza!!!')
            if self.indice_plazas == self.n_plazas:
                break
            if key == 27:
                break
        #self.captura.release()
        captura.release()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    plazasdef = plazas(14,50,30) # dentro de la clase especificar(numero de plazas, distancia al punto central de la ROI, dpy)
    plazasdef.guardarplazas()
