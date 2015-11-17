#! /usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Script de récupération, encryption et publication webdav d'une IP VPN pour accès extérieur

import os
import socket
import fcntl
import struct

debug = True
tps_actu = 60                                                                                              #temps à attendre entre deux vérifications
cheminWebdav = "/home/jason/Desktop/WebDav_Test"          #Rpi /home/pi/Box/VPN_IP
interface = "wlp3s0"                                                                                #Rpi tun0

def lireIP(interface, debug):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ip = socket.inet_ntoa(fcntl.ioctl(s.fileno(),0x8915,struct.pack('256s', interface[:15]))[20:24])
    if debug:
        print ip
    return ip
    
def ecrireIP(IP,debug):
    date_cmd = os.popen("date +%d%m%Y_%H%M%S")
    #Retourne une chaine : 11112015_235551
    date = date_cmd.read().replace("\n","")
    
    nom = "ipVPNchi_" + date + ".txt"
    
    if debug:
        print "\necho '" + IP + "' > " + nom
    os.system("echo '" + IP + "' > " + nom)     #On écrit un fichier contenant l'IP (echo IP > fichier)
    
    if debug:
        print "gpg -r opo --encrypt-files " + nom
    os.system("gpg -r opo --encrypt-files " + nom)  #On chiffre avec gpg le fichier

    if debug:
        print "rm " + nom
    os.system("rm " + nom)  #On supprime le fichier temporaire
    
    if debug:
        print "mv " + nom + ".gpg " + cheminWebdav
    os.system("mv " + nom + ".gpg " + cheminWebdav)   #On place le fichier chiffré dans le webdav

def sauvegarderIP(ip):
    fichier = open("ip","w")
    fichier.write(ip)
    fichier.close()

def lireSauvegardeIP(debug):
    try:
	    fichier = open("ip","r")
	    ip = fichier.readline()
        fichier.close()
    except IOError:
        ip = "vide"
     if debug:
            print ip
     return ip

if debug:
    print "Début pause..."
os.system("sleep 60")   #On attend que tout soit initialisé avant de commencer (lan,openvpn,webdav)
if debug:
    print "Fin pause..."

ip_ref  = lireSauvegardeIP(debug)        #Permet de charger la dernière IP téléchargée sur le webdav
while True:
    ip_lue = lireIP(interface,debug)
    if debug:
        print "ip_lue != ip_ref : " + str(ip_lue != ip_ref)
    if ip_lue != ip_ref:
        ecrireIP(ip_lue,debug)      #Mise à jour de l'adresse sur le webdav uniquement si l'IP a changée au reboot ou à cause du bail
        sauvegarderIP(ip_lue)      #Mise à jour du fichier de sauvegarde local pour pouvoir connaître l'ip d'avant un reboot non planifié
        ip_ref = ip_lue
    os.system("sleep " + str(tps_actu))
