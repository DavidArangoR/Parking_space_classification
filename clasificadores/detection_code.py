#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 28 20:00:51 2019

@author: david
"""

import matplotlib.pyplot as plt
import cv2
import numpy as np
import random
import pickle
import time 
import skimage
from skimage.io import imread
from skimage.transform import resize
import pymysql

''' -------- SOCKET CLIENTE --------- '''
'''
import zmq
import base64

context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.bind('tcp://*:8888')
socket.setsockopt_string(zmq.SUBSCRIBE, np.unicode(''))
'''
'''  ----------------------------  '''

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
        self.model = 0
        self.color = 0
        
    def cargar_plazas(self):
        
        self.plazas = np.load('Arreglo_Final.npy')
        self.pt_centrales = np.load('Arreglo_pt_centrales.npy')
        
        n_plazas = len(self.plazas)
        print(self.plazas)
        print('Numero de plazas cargadas: ', n_plazas)       
                
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
    
    
    def runpred(self):
        '''
          --------  CARGA DE MODELO ENTRENADO -----------
        '''
        filename = "clasificadores/svm_model.pkl"
        #print('Modelo Cargado: {}'.format(filename))
        with open(filename, 'rb') as file:
            self.model = pickle.load(file)
        return self.model
        
       
    def cargar_modelo(self):
        cv2.namedWindow('Video',cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Video',(800,800))
        #imagen = cv2.imread('zona1_10am.jpg')
        captura = cv2.VideoCapture('entradacarro.mp4')  
        #captura = cv2.VideoCapture('tcp://192.168.1.1:5555')              
        contador = 0     
        while True: 
            
            '''------ RECEPCION DE DATOS DE VIDEO DEL SOCKET SERVIDOR-------- '''
            '''
            image_string = socket.recv_string()
            raw_image = base64.b64decode(image_string)
            image = np.frombuffer(raw_image, dtype=np.uint8)
            frame = cv2.imdecode(image, 1)
            img = frame.copy()
            img_parche = frame.copy()
            t = time.time()
            '''
            '''--------------- '''
            
            (grabbed, imagen) = captura.read()            
            if not grabbed:
                break
                     
            t = time.time()
            img = imagen.copy()
            img_parche = img.copy()
            Busy = 0
            Free = 0
            list_plazas = []            
            if contador == 40: # condicion para ejecutar prediccion cada 40 frames 
                for i in range(0,len(self.plazas)):
                    a = self.plazas[i]
                    p_c = self.pt_centrales[i]
                    cv2.circle(img,(int(p_c[0]),int(p_c[1])),2,(0,0,255),-1)
                    cv2.putText(img,"PLAZA #" + str(i+1),(int(p_c[0])+3,int(p_c[1])),
                                cv2.FONT_HERSHEY_DUPLEX,0.5,(0,0,255),1)                
                    for j in a:
                        (x, y) = j  # Se extrae la coordenada de cada plaza                     
                        #----------------------------------------
                        #           ANALISIS DE REGIONES
                        #----------------------------------------
                        parche = img_parche[y-(self.dp+self.dpy): y + (self.dp+self.dpy), x- self.dp: x+ self.dp]#definicion de parche
                        #parche = img_parche[y-(self.dp+10): y + (self.dp+10), x- self.dp: x+ self.dp]#definicion de parche img7
                        # imagen como skimage: numpy array uint8 RGB
                        parche = cv2.cvtColor(parche,cv2.COLOR_BGR2RGB)
                        # Se redimensiona pero ahora los valores estan entre 0-1 (este cambio lo hace la funcion resize de skimage)
                        img_resized = resize(parche,(64,64),anti_aliasing=True, mode='reflect')
                        img_resized = img_resized.flatten()# esto fue adicionado a lo ultimo
                        img_flatten = img_resized.reshape((1,-1))
                        predicciones = self.runpred().predict(img_flatten)
                        
                        if predicciones[0] == 1: #1 es bussy segun el orden de lectura de dataset en entrenamiento
                           # print('Busy',i+1)
                            cv2.rectangle(img, (x-self.r_x, y-self.r_y), (x-self.r_x + self.w, y-self.r_y + self.w),(0,0,255), 2)
                            Busy = Busy + 1
                            est_plaza = 'p' + str(i+1) + ' ocupado'  # numero de plaza y estado para enviar a sql
                            list_plazas.append(est_plaza)
                        else:
                            #print('Free',i+1)
                            cv2.rectangle(img, (x-self.r_x, y-self.r_y), (x-self.r_x + self.w, y-self.r_y + self.w),(0,255,0), 2)
                            Free = Free + 1
                            est_plaza = 'p' + str(i+1) + ' libre'  # numero de plaza y estado para enviar a sql
                            list_plazas.append(est_plaza)                            
                
                contador = 0  
                tiempo = time.localtime()
                hora = str(tiempo[3])+':'+ str(tiempo[4])+':'+str(tiempo[5])
                ''' ____________ENVIO AL SERVIDOR_________________'''
                #prediccion.conexionservidor(Busy,Free,hora) #  descomentar esta linea en modo main, almacenamiento en el servidor
                #prediccion.conexionservidor(self,Busy,Free,tuple(list_plazas),hora) # almacenamiento en el servidor
                ''' ________________________________________'''  
                          
            
            elapsed = time.time() - t
            contador = contador +1
            #print('--------- Tiempo transcurrido ------- : ',elapsed)
            cv2.imshow('Video', img)
            #key = cv2.waitKey(5) & 0xFF 
            key = cv2.waitKey(1) & 0xFF 
            #-------------------------------------------
            #Salimos si la tecla presionada es ESC
            if key == 27:
                break
        #self.captura.release()
        captura.release()
        cv2.destroyAllWindows()      

if __name__ == '__main__':
    
    prediccion = prediccion(50,30) 
    prediccion.cargar_plazas()
    prediccion.cargar_modelo()