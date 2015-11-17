#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Script de récupération, encryption et publication webdav d'une IP VPN pour accès extérieur
# Jason GOMBERT, 12/11/2015 02:20:05  (V1.4)

import os

debug = False

def lireIP(debug):
    ip = os.popen("/sbin/ifconfig tun0 | grep inet\ adr")     
    #Retourne une chaine : inet adr:10.99.4.208  P-t-P:10.99.4.208  Masque:255.255.255.0
    chaine = ip.read()
    if debug:
        print "chaine =",chaine    
    ligneTun = chaine.split("  ")[5]    #On garde que : inet adr:10.99.4.208
    if debug:
        print "ligneTun =",ligneTun
    ipTun = ligneTun.split(":")[1]      #On garde que : 10.99.4.208
    if debug:
        print "ipTun =",ipTun
    return ipTun
    
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
        print "mv " + nom + ".gpg /home/pi/Box/VPN_IP"
    os.system("mv " + nom + ".gpg /home/pi/Box/VPN_IP")   #On place le fichier chiffré dans le webdav

if debug:
    print "Début pause..."
os.system("sleep 60")   #On attend que tout soit initialisé avant de commencer (lan,openvpn,webdav)
if debug:
    print "Fin pause..."
ecrireIP(lireIP(debug),debug)
