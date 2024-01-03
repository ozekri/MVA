import os
import numpy as np

"""
def show_video(video_path): #function that display a video
    os.startfile(video_path)
pathh = os.path.abspath("./videos/queries.mp4")
show_video(pathh)

"""

eps_L,eps_l = 100., 100.
n=5
x_rand = np.random.rand(n,1)*(1920-2*eps_L) + eps_L
y_rand = np.random.rand(n,1)*(1080-2*eps_l) + eps_l
frames_num = np.zeros((1,n)).T
print(frames_num)
print("x",x_rand)
print("y",y_rand)

y = np.hstack((frames_num,x_rand,y_rand))
print("conc",y)

hashmap = {0 : True, 1: False, 2: False, 3:True, 4 :False}
c=str(2)
nom='queries_bus.txt'      #on crée une variable de type string
fichier=open(nom,'w')#ouverture du fichier en écriture : 'w' pour write
ecr_pos,ecr_neg='',''
for i in range(len(y)):
    if hashmap[i] == True:
        ecr_pos+=str(y[i][1])+','+str(y[i][2])+' ' #si le fichier n'existe pas, il est créé, sinon son contenu est écrasé
    else:
        ecr_neg+=str(y[i][1])+','+str(y[i][2])+' '
final = str(y[0][0])+';' + ecr_pos +ecr_neg
fichier.write(c+'\n')
fichier.write(final)
fichier.close()