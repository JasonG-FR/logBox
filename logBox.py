#! /usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Script de récupération, encryption et publication webdav d'une IP VPN pour accès extérieur

import os
import socket
import fcntl
import struct

def genDefauts():
    params = {"debug":False,
                         "tps_actu":"300",
                         "cheminWebdav":"/home/pi/Box/VPN_IP",
                         "interface":"tun0",
                         "destinataireGPG":"opo"}
                         
    config = open("/home/pi/logBox/config","w")
    for key in params:
        config.write(str(key)+":"+str(params[key])+"\n")
    config.close()
    
def lireParametres():
    try:
        config = open("/home/pi/logBox/config","r")
    except IOError:
        genDefauts()
        config = open("/home/pi/logBox/config","r")
    params = formaterParams(config)
    config.close()
    return params
    
def formaterParams(fichier):
    params = {}     #inutile?
    for line in fichier:
            key = line.split(":")[0]
            item = line.split(":")[1]
            if key == "debug":
                params[key] = bool(item)
            else:
                params[key] = item.replace("\n","")
    return params

def lireIP(interface, debug):
    if debug:
        print interface
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ip = socket.inet_ntoa(fcntl.ioctl(s.fileno(),0x8915,struct.pack('256s', interface[:15]))[20:24])
    if debug:
        print ip
    return ip
    
def ecrireIP(IP,destinataireGPG,cheminWebdav,debug):
    date_cmd = os.popen("date +%d%m%Y_%H%M%S")          #Retourne une chaine : 11112015_235551
    date = date_cmd.read().replace("\n","")
    nom = "ipVPNchi_" + date + ".txt"
    
    if debug:
        print "\necho '" + IP + "' > " + nom
    os.system("echo '" + IP + "' > " + nom)     #On écrit un fichier contenant l'IP (echo IP > fichier)
    
    if debug:
        print "gpg -r " + destinataireGPG + " --encrypt-files " + nom
    os.system("gpg -r " + destinataireGPG + " --encrypt-files " + nom)  #On chiffre avec gpg le fichier

    if debug:
        print "rm " + nom
    os.system("rm " + nom)  #On supprime le fichier temporaire
    
    if debug:
        print "mv " + nom + ".gpg " + cheminWebdav
    os.system("mv " + nom + ".gpg " + cheminWebdav)   #On place le fichier chiffré dans le webdav

def sauvegarderIP(ip):
    fichier = open("/home/pi/logBox/ip","w")
    fichier.write(ip)
    fichier.close()

def lireSauvegardeIP(debug):
    try:
        fichier = open("/home/pi/logBox/ip","r")
        ip = fichier.readline()
        fichier.close()
    except IOError:
        ip = "vide"
    if debug:
        print ip
    return ip



parametres = lireParametres()
ip_ref = lireSauvegardeIP(parametres["debug"])        #Permet de charger la dernière IP téléchargée sur le webdav

if parametres["debug"]:
    print "Début pause..."

os.system("sleep 60")   #On attend que tout soit initialisé avant de commencer (lan,openvpn,webdav)

if parametres["debug"]:
    print "Fin pause..."

while True:
    ip_lue = lireIP(parametres["interface"],parametres["debug"])        #On récupère l'IP actuelle
    
    if parametres["debug"]:
        print "ip_lue != ip_ref : " + str(ip_lue != ip_ref)
    
    if ip_lue != ip_ref:                                                                                                                                                                            #Si celle qu'on a sur le webdav est différente alors on doit la mettre à jour !
        ecrireIP(ip_lue,parametres["destinataireGPG"],parametres["cheminWebdav"],parametres["debug"])        #Mise à jour de l'adresse sur le webdav uniquement si l'IP a changée au reboot ou à cause du bail DHCP
        sauvegarderIP(ip_lue)                                                                                                                                                              #Mise à jour du fichier de sauvegarde local pour pouvoir connaître l'ip d'avant un reboot non planifié
        ip_ref = ip_lue                                                                                                                                                                              #On garde la nouvelle IP écrite en mémoire
    os.system("sleep " + parametres["tps_actu"])                                                                                                                       #On attend avant de faire de nouveau une lecture de l'IP
