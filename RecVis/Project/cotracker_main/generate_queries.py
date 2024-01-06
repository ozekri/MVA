import os
import torch
import numpy as np

from base64 import b64encode
from cotracker.utils.visualizer import Visualizer, read_video_from_path
from cotracker.predictor import CoTrackerPredictor
from IPython.display import HTML

##Parameters
path_vid = os.path.abspath('../data/bus/anim.mp4') #path of a video
is_checkpoint = False #True if the cotracker chkpt is in the right folder, False otherwise (if False, put the path to the checkpoint in "checkpoint_path")
checkpoint_path = 'C:/Users/dofel/Desktop/cotracker2.pth'

display_blank_vid = False #True if you want to display the original video at the beginning of the code, False otherwise
display_vid = True #True if you want to display the video after the code executes, False otherwise
display_details = True #True if you want to display the number of positive points and their classification during the first sampling

n=50 #Number of points for the first sampling
eps_L,eps_l = 100., 100. #Sampling edges

video = read_video_from_path(path_vid)
video = torch.from_numpy(video).permute(0, 3, 1, 2)[None].float()

def show_video(video_path): #function that display a video
    os.startfile(video_path)
    
if display_blank_vid: show_video(path_vid)

#Importing CoTrackerPredictor and creating an instance of it
if is_checkpoint:
    model = CoTrackerPredictor(checkpoint=os.path.join('./checkpoints/cotracker2.pth'))
else:
    model = CoTrackerPredictor(checkpoint=os.path.join(checkpoint_path))


if torch.cuda.is_available():
    model = model.cuda()
    video = video.cuda()

#We will start by tracking points queried manually. We define a queried point as: [time, x coord, y coord]
#So, the code below defines points with different x and y coordinates sampled on frames 0, 10, 20, and 30


eps_L,eps_l = 100., 100.
n=150

x_rand = np.random.rand(n,1)*(float(video.shape[4])-2*eps_L) + eps_L
y_rand = np.random.rand(n,1)*(float(video.shape[3])-2*eps_l) + eps_l
frames_num = np.zeros((1,n),dtype=int).T

points = np.hstack((frames_num,x_rand,y_rand))

queries = torch.tensor(points.tolist())

if torch.cuda.is_available():
    queries = queries.cuda()



pred_tracks, pred_visibility = model(video, queries=queries[None])

def sum_speed(l):
    res = 0
    for i in range(len(l)-1):
        res += np.linalg.norm(l[i]-l[i+1])
    return res
#create a big list L with the couples [res,normk]

def normalized_speed(L): #return a list with all the normalized speed
    norm = np.amax(np.array(L))
    res = []
    for elem in L:
        res.append(elem/norm)
    return res

def is_positive(p,tresh):
    if p > tresh: return False
    else: return True

traj_list=[]
for i in range(n):
    traj_list.append(pred_tracks[0,:,i].cpu().numpy())

L=[]
for traj in traj_list:
    L.append(sum_speed(traj))

normalized_s = normalized_speed(L)

c=0
point_hash={} #hasmap with the points index in key and the label True if positive, False if negative in values
tresh = 0.5
for idx,p in enumerate(normalized_s):
    if is_positive(p,tresh):
        c+=1
        point_hash[idx] = True
    else: point_hash[idx] = False
  
if display_details:
    print(c) #counter
    print(point_hash) #point list with labels

nom='queries_bus.txt'      #on crée une variable de type string
fichier=open(nom,'w')#ouverture du fichier en écriture : 'w' pour write
ecr_pos,ecr_neg='',''
for i in range(len(points)):
    if point_hash[i]:
        ecr_pos+=str(points[i][1])+','+str(points[i][2])+' ' #si le fichier n'existe pas, il est créé, sinon son contenu est écrasé
    else:
        ecr_neg+=str(points[i][1])+','+str(points[i][2])+' '
final = str(int(points[0][0]))+';' + ecr_pos +ecr_neg
fichier.write(str(c)+'\n')
fichier.write(final)
fichier.close() #close the document

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
if display_vid: show_video(path_show)