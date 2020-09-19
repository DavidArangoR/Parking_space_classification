#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 29 22:38:53 2019

@author: david
"""

from sklearn.svm import SVC
import matplotlib.pyplot as plt
import cv2
import numpy as np
import random
import skimage
from skimage.io import imread
from skimage.transform import resize
import time
import tensorflow as tf
from tensorflow.keras.models import load_model
import pymysql.cursors

class prediccion():

    def __init__(self,dp,dpy):
        self.puntos_plaza = 1
        self.w = dp * 2 # parametro del ancho de la cuadricula que se dibuja sobre cada plaza
        #self.w = 60 #para img7
        self.r_x = int(self.w/2)
        self.r_y = int(self.w/2)
        self.dp = dp
        self.dpy = dpy
        #self.dp = 30   #para img7
        self.plazas = 0
        self.pt_centrales = 0
        self.model = load_model('clasificadores/classifier_model.h5')
        self.color = 0

    def conexionservidor(self,Busy,Free,Estado,hora):
        connection = pymysql.connect(host = 'localhost',
                             user = 'david',
                             port = 3306,
                             password = '1234',
                             db = 'PARKINGSPACE',
                             cursorclass = pymysql.cursors.DictCursor)
        with connection.cursor() as cursor:
            sqlQuery = 'INSERT INTO registros(HORA,ESTADO,LIBRES,OCUPADOS) VALUES (%s,%r,%s,%s)'
            cursor.execute(sqlQuery,(hora,Estado,Free,Busy)) # el segundo argumento de .execute es una tupla con los valores a adicionar aL db
            connection.commit()
        connection.close()

    def cargar_plazas(self):

        self.plazas = np.load('Arreglo_Final.npy')
        self.pt_centrales = np.load('Arreglo_pt_centrales.npy')

        n_plazas = len(self.plazas)
        print(self.plazas)
        print('Numero de plazas cargadas: ', n_plazas)

    def cargar_modelo(self):
        cv2.namedWindow('Video',cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Video',(800,800))
        #imagen = cv2.imread('zona1_10am.jpg')
        captura = cv2.VideoCapture('entradacarro.mp4')
        #captura = cv2.VideoCapture('tcp://192.168.1.1:5555')
        contador = 0
        while True:
            (grabbed, imagen) = captura.read()
            if not grabbed:
                break
            t = time.time()
            img = imagen.copy()
            img_parche = img.copy()
            #contador = 0
            Free = 0
            Busy = 0
            list_plazas = []
            if contador == 40: #20
                for i in range(0,len(self.plazas)):
                    a = self.plazas[i]
                    p_c = self.pt_centrales[i]
                    cv2.circle(img,(int(p_c[0]),int(p_c[1])),4,(0,0,255),-1)
                    cv2.putText(img,"PLAZA #" + str(i+1),(int(p_c[0])+3,int(p_c[1])),
                        cv2.FONT_HERSHEY_DUPLEX,0.5,(0,0,255),1)
                    for j in a:
                        (x, y) = j
                        #----------------------------------------
                        #           ANALISIS DE REGIONES
                        #----------------------------------------
                        parche = img_parche[y-(self.dp+self.dpy): y + (self.dp+self.dpy), x- self.dp: x+ self.dp]#definicion de parche
                        # imagen como skimage: numpy array uint8 RGB
                        parche = cv2.cvtColor(parche,cv2.COLOR_BGR2RGB)
                        # Se redimensiona pero ahora los valores estan entre 0-1 ( la funcion resize cambia los valores)
                        x_resize = resize(parche,(300,300))
                        x = np.expand_dims(x_resize, axis=0) # se adiciona una dimension al comienzo del arreglo la cual indica el numero de muestras que se ingresan a la CNN
                        imageint = np.vstack([x]) # todos los datos de la imagen se organizan en una columna para ingresarlos a la CNN
                        predicciones = self.model.predict(imageint, batch_size=10)# batch_size = 10
                        #print('valor prediccion: {}'.format(predicciones[0]))
                        if predicciones[0] >= 0.5: #0 es bussy segun el orden de lectura de dataset en entrenamiento predicciones[0] ==1
                            cv2.circle(img,(int(p_c[0]),int(p_c[1])),4,(0,255,0),-1)
                            est_plaza = 'p' + str(i+1) + ' libre'  # numero de plaza y estado para enviar a sql
                            list_plazas.append(est_plaza)
                            Free = Free+1
                        if predicciones[0] < 0.5:
                            Busy = Busy+1
                            cv2.circle(img,(int(p_c[0]),int(p_c[1])),4,(0,0,255),-1)
                            est_plaza = 'p' + str(i+1) + ' ocupado'  # numero de plaza y estado para enviar a sql
                            list_plazas.append(est_plaza)
                contador = 0
                tiempo = time.localtime()
                hora = str(tiempo[3])+':'+ str(tiempo[4])+':'+str(tiempo[5])
                ''' ____________ENVIO AL SERVIDOR_________________'''
                #prediccion.conexionservidor(Busy,Free,hora) #  descomentar esta linea en modo main, almacenamiento en el servidor
                #prediccion.conexionservidor(self,Busy,Free,tuple(list_plazas),hora) # almacenamiento en el servidor
                ''' ________________________________________'''
            contador = contador + 1
            elapsed = time.time() - t
            #print('---- tiempo ----- : ', elapsed)
            cv2.imshow('Video', img)
            key = cv2.waitKey(5) & 0xFF
            #-------------------------------------------
            #Salimos si la tecla presionada es ESC
            if key == 27:
                break
            #print('total free: ',totalfree)
            #print('total bussy: ',totalbussy
        captura.release()
        cv2.destroyAllWindows()

if __name__ == '__main__':

    prediccion = prediccion(50,30)
    prediccion.cargar_plazas()
    prediccion.cargar_modelo()
