import os
import torch
import numpy as np

from base64 import b64encode
from cotracker.utils.visualizer import Visualizer, read_video_from_path
from cotracker.predictor import CoTrackerPredictor
from IPython.display import HTML

path_vid = os.path.abspath('../data/lucia/anim.mp4') #path of a video

video = read_video_from_path(path_vid)
video = torch.from_numpy(video).permute(0, 3, 1, 2)[None].float()

def show_video(video_path): #function that display a video
    os.startfile(video_path)
    
#show_video(path_vid)

#Importing CoTrackerPredictor and creating an instance of it
"""model = CoTrackerPredictor(
    checkpoint=os.path.join(
        './checkpoints/cotracker2.pth'
    )
)"""

model = CoTrackerPredictor(
    checkpoint=os.path.join(
        'C:/Users/dofel/Desktop/cotracker2.pth'
    )
)

if torch.cuda.is_available():
    model = model.cuda()
    video = video.cuda()

#We will start by tracking points queried manually. We define a queried point as: [time, x coord, y coord]
#So, the code below defines points with different x and y coordinates sampled on frames 0, 10, 20, and 30


eps_L,eps_l = 100., 100.
n=50

x_rand = np.random.rand(n,1)*(float(video.shape[4])-2*eps_L) + eps_L
y_rand = np.random.rand(n,1)*(float(video.shape[3])-2*eps_l) + eps_l
frames_num = np.zeros((1,n),dtype=int).T

points = np.hstack((frames_num,x_rand,y_rand))

queries = torch.tensor(points.tolist())


if torch.cuda.is_available():
    queries = queries.cuda()
    


pred_tracks, pred_visibility = model(video, queries=queries[None])

def sum_dist(liste):
    res = 0
    norml = [np.linalg.norm(liste[-1])]
    for i in range(len(liste)-1):
        res += np.linalg.norm(liste[i]-liste[i+1])
        norml.append(np.linalg.norm(liste[i]))
    norm = sum(norml)
    return res/norm

def is_Positive(pt,tresh):
    if sum_dist(pt) > tresh: return False
    else: return True
    
plist=[]
for i in range(n):
    plist.append(pred_tracks[0,:,i].cpu().numpy())

c=0
point_hash={} #hasmap with the points index in key and the label True if positive, False if negative in values
for idx,p in enumerate(plist):
    #print(sum_dist(p))
    #print(is_Positive(p,0.02))
    if is_Positive(p,0.02):
        c+=1
        point_hash[idx] = True
    else: point_hash[idx] = False
  
print(c) #counter
print(point_hash) #point list with labels


min_x,max_x,min_y,max_y = np.inf,0.0,np.inf,0.0
x_neg,y_neg=0.0,0.0
for i in range(len(points)):
    if point_hash[i]:
        if min_x >= points[i][1] : min_x = points[i][1]
        if max_x <= points[i][1] : max_x = points[i][1]
        if min_y >= points[i][2] : min_y = points[i][2]
        if max_y <= points[i][2] : max_y = points[i][2]
    else:
        x_neg,y_neg = points[i][1],points[i][2]
    

##########

n_2=3

x_rand_2 = np.random.rand(n_2+1,1)*(max_x-min_x) + min_x
x_rand_2[-1] = x_neg
y_rand_2 = np.random.rand(n_2+1,1)*(max_y-min_y) + min_y
y_rand_2[-1] = y_neg

frames_num_2 = np.zeros((1,n_2+1),dtype=int).T

points_2 = np.hstack((frames_num_2,x_rand_2,y_rand_2))

queries_2 = torch.tensor(points_2.tolist())

###########
nom='queries_lucia.txt'      #on crée une variable de type string
fichier=open(nom,'w')#ouverture du fichier en écriture : 'w' pour write
ecr_pos,ecr_neg='',''
for i in range(len(points_2)-1):
    ecr_pos+=str(points_2[i][1])+','+str(points_2[i][2])+' ' #si le fichier n'existe pas, il est créé, sinon son contenu est écrasé

ecr_neg+=str(points_2[-1][1])+','+str(points_2[-1][2])+' '

final = str(int(points_2[0][0]))+';' + ecr_pos +ecr_neg
fichier.write(str(n_2)+'\n')
fichier.write(final)
fichier.close()

    

vis = Visualizer(
    save_dir='./videos',
    linewidth=6,
    mode='cool',
    tracks_leave_trace=-1
)
vis.visualize(
    video=video,
    tracks=pred_tracks,
    visibility=pred_visibility,
    filename='queries');

path_show = os.path.abspath("./videos/queries.mp4")
show_video(path_show)