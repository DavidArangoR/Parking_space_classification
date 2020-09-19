#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan  5 16:45:04 2020
@author: david
"""

from tkinter import *
import tkinter as tk
import cv2
from tkinter import messagebox, Menu
from modulo_seleccionar.Definicion_plazas import *
#from clasificadores.detectionHOG import * // SVM HOG
#from clasificadores.detection_code_CNN import * // red neuronal convolucional 
from clasificadores.detection_code import *
import time

color_backg = 'LightYellow2'
colorbox = 'DeepSkyBlue2'
def ex_deteccion():
    dist_punto = 20 # medida en pixeles, corresponde a la mitad del ancho
    dist_py = 10   #medida en pixeles, corresponde la mitad de la altura         
    executepred= prediccion(dist_punto,dist_py)
    root = Tk()      
    root.title('SMART PARKING DETECTION')    
    ''' DIMENSIONES DE LA INTERFAZ'''
    root.geometry('1100x600')
    root.configure(background= color_backg)
    root.minsize(1000,550)  
    root.maxsize(1050,580)   
     
    def info():
        mensaje = "Este programa ha sido creado por David Arango y Ricardo Roa, estudiantes de la\n Universidad Surcolombiana de Neiva."
        messagebox.showinfo(message=mensaje,title="Creadores")
    def helpoption():
        mensaje2 = "Para Seleccionar el tramaño de cada plaza, tenga en cuenta que el valor ingresado en la casilla de ancho y alto, corresponden a la mitad de la dimensión en pixeles."
        messagebox.showwarning(message=mensaje2,title="Configurar dimensiones")
    def infoversiones():
        mensaje3 = "Se requiere las siguientes versiones instaladas: \n * Tensorflow 1.13.1 \n * Opencv 4.1 \n * Scikit-Learn 0.21.2 \n * Scikit-Image 0.15.0 "
        messagebox.showinfo(message=mensaje3, title='Versiones librerias')
    ''' MENU BAR '''
    menubar = Menu(root)
    root.config(menu=menubar)
    infomenu = Menu(menubar,tearoff=1)
    helpmenu = Menu(menubar,tearoff=0)
    versionmenu = Menu(menubar,tearoff=2)
    
    menubar.add_cascade(label="Informacion", menu=infomenu)    
    menubar.add_cascade(label="Ayuda", menu=helpmenu)
    menubar.add_cascade(label="Software", menu=versionmenu)
    infomenu.add_command(label="Acerca de..", command=info)
    helpmenu.add_command(label="¿Como elegir dimensiones?", command=helpoption)
    versionmenu.add_command(label="Versiones", command=infoversiones)    
    
    '''-----'''
    mainwindow = Frame(root,bg=color_backg)
    mainwindow.grid(row=0, column=0, padx=1, pady=1)
    
    secondwindow = Frame(root,bg=color_backg)
    secondwindow.grid(row=1, column=0, padx=1, pady=1)
    
    thirdwindow = Frame(root,bg=color_backg)
    thirdwindow.grid(row=2, column=0, padx=1, pady=1)
    
    fourthwindow = Frame(root,bg=color_backg)
    fourthwindow.grid(row=3, column=0, padx=1, pady=1)
       
    textitle = 'DETECCIÓN ZONAS DE PARQUEO'
    maintitle = Label(mainwindow, text=textitle, font = ('Arial Bold',20), fg='white', justify='center', anchor='n',bg='red4') #red4
    maintitle.grid(row=0, column=0, padx=300, pady=1)  # row = 7  
    
    text1 = '\n Antes de ejecutar el programa tenga en cuenta las siguientes instrucciones:'
    text2 = '\n 1) Si desea ajustar los tamaños de las regiones y la cantidad de plazas a detectar oprima \n el botón configuración. \n 2) Luego presione el botón seleccionar plazas y defina el punto central en cada una.\n 3) El paso a seguir es cargar los datos recopilados en la etapa previa. \n 4) Finalmente seleccione el botón predicción para la detección en tiempo real.'
    cuadro1 = Label(secondwindow, text=text1, font = ('Arial Bold',15), fg='black', anchor='e', justify='center', background=color_backg)
    cuadro1.grid(row=1, column=0, padx=1, pady=2)
    cuadro2 = Label(secondwindow, text=text2, font = ('Arial Bold',15), fg='black', anchor='n',justify='left',background=color_backg)
    cuadro2.grid(row=2, column=0, padx=1, pady=2)
    
    botones = Label(thirdwindow,height=10, width=100,background=color_backg)
    botones.grid(row=0, column=0, padx=1, pady=2)    
    
    imgmuestra = PhotoImage(file='IMGinterfaz.png')
    imgmuestrawindow = Label(fourthwindow,height=200, width=350,image=imgmuestra)
    imgmuestrawindow.grid(row=0, column=2, padx=30, pady=1) 
    
    messagebox.showinfo(message='BIENVENIDO AL SISTEMA DE DETECCIÓN DE ZONAS DE PARQUEO', title="Información")    
    ''' funcion dimensiones de cada ROI y numero de plazas '''
    def asigdimensiones():
        respuesta = messagebox.askyesno(message='¿Desea asignar dimensiones de cada plaza?',title='Pregunta')
        if respuesta == True: 
            # ENTRADA DIMENSION ANCHO
            mitadancho = Entry(botones,width=8, justify='center')
            mitadancho.place(x=10,y=50)
            # ENTRADA DIMENSION ALTO
            alto= Entry(botones,width=8, justify='center')
            alto.place(x=10,y=70)
            # ENTRADA DE NUMERO DE PLAZAS   
            cuadroplazas = Entry(botones,width=8, justify='center')
            cuadroplazas.place(x=200,y=10)
            # ETIQUETAS DE CADA TEXTBOX
            textalto = Label(thirdwindow,text='Alto', font = ('Arial Bold',9), fg='white', anchor='n', justify='left',background='black')
            textalto.place(x = 80,y=70)
            textancho = Label(thirdwindow,text='Ancho', font = ('Arial Bold',9), fg='white', anchor='n', justify='left',background='black')
            textancho.place(x = 80,y=50)
            textp = Label(thirdwindow,text='cantidad plazas', font = ('Arial Bold',9), fg='white', anchor='n', justify='left',background='black')
            textp.place(x = 180,y=30)
            def valoresconfig():
                 dist_punto = int(mitadancho.get())
                 dist_py = int(alto.get()) 
                 numplazas_ing = float(cuadroplazas.get())
                 ''' ----------'''
                 btn_selplazas = Button(botones, text = 'Seleccionar',font=('Helvetica',12), padx=3, pady=3, width=12, height=2, justify='center',command=plazas(numplazas_ing,dist_punto,dist_py).guardarplazas, bg=colorbox).place(x=200,y=60)
                 executepred= prediccion(dist_punto,dist_py)
                 btn_cargarplazas= Button(botones,text = 'Cargar plazas', font=('Helvetica',12), padx=5, pady=4, width=15, height=2, justify='center',command=executepred.cargar_plazas, bg=colorbox).place(x=350,y=60)
                 btn_prediccion = Button(botones,text = 'Predicción', font=('Helvetica',12), padx=5, pady=4, width=12, height=2, justify='center',command=executepred.cargar_modelo,bg=colorbox).place(x=500,y=60)
            enviardimensiones = Button(botones, text = 'Agregar',font=('Helvetica',9), padx=3, pady=3, width=12, height=1, justify='center',command=valoresconfig, bg=colorbox).place(x=10,y=90)  
           
        else:
            cuadroplazas = Entry(botones,width=8, justify='center')
            cuadroplazas.place(x=200,y=10)
            textp = Label(thirdwindow,text='cantidad plazas', font = ('Arial Bold',9), fg='white', anchor='n', justify='left',background='black')
            textp.place(x = 180,y=30)
            def getnumplazas():
                numplazas_ing = float(cuadroplazas.get())
                btn_selplazas = Button(botones, text = 'Seleccionar',font=('Helvetica',12), padx=3, pady=3, width=12, height=2, justify='center',command=plazas(numplazas_ing,dist_punto,dist_py).guardarplazas, bg='DeepSkyBlue2').place(x=120,y=60)
            btn_numplazas = Button(botones, text = 'Asignar\n número plazas',font=('Helvetica',9), padx=3, pady=3, width=15, height=2, justify='center',command=getnumplazas).place(x=300,y=10)
    btn_cargarplazas= Button(botones,text = 'Cargar plazas', font=('Helvetica',12), padx=5, pady=4, width=12, height=2, justify='center',command=executepred.cargar_plazas, bg=colorbox).place(x=350,y=60)
    btn_prediccion = Button(botones,text = 'Predicción', font=('Helvetica',12), padx=5, pady=4, width=12, height=2, justify='center',command=executepred.cargar_modelo,bg=colorbox).place(x=500,y=60)
    btn_dimensiones = Button(botones, text = 'Configuración',font=('Helvetica',9), padx=3, pady=3, width=15, height=2, justify='center',command=asigdimensiones, bg=colorbox).place(x=10,y=10)  
    root.mainloop()

ex_deteccion()
