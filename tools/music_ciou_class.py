import pickle
import json
import cv2
import sklearn.metrics
import numpy as np

#load bounding box and predicted avmap result
gt = json.load(open('/home/yuxi/ruiq/faster-rcnn.pytorch/duettest.json', 'r'))
pred = pickle.load(open('duet.pkl', 'rb'))
corr = np.load('corr.npy')
keylist = ['trumpet', 'xylophone', 'acoustic_guitar', 'flute', 'violin', 
           'saxophone', 'accordion', 'cello', 'erhu', 'tuba', 'clarinet']
duetkeys = {13: 'accordion', 3: 'acoustic_guitar', 1: 'cello', 12: 'flute', 8: 'saxophone', 
            10: 'trumpet', 11: 'violin'}

cious = []
thres = 0.2#threshold to determine whether positive on avmap

for k in pred:
    if k not in gt:
        continue
    if len(gt[k]['bbox']) == 0:
        continue
    
    boxs = {}
    for box in gt[k]['bbox']:
        category = box['category_id']
        index = keylist.index(duetkeys[category])
        index = corr[index]
        if index not in boxs:
            boxs[index] = []
        boxs[index].append(box['normbox'])

    ciou = []
    for idx in boxs:
        gtmap = np.zeros((224, 224))
        for i in range(len(boxs[idx])):
            box = boxs[idx][i]
            box = np.array(box) * 224
            gtmap[int(box[1]): int(box[1]+box[3]), int(box[0]): int(box[0]+box[2])] = 1
        #resize predited avmap to (224, 224)
        predmap = cv2.resize(pred[k][idx], (224, 224))
        #calculate ciou
        ciou.append(np.sum((predmap>thres) * (gtmap>0)) / (np.sum(gtmap) + np.sum((predmap>thres) * (gtmap==0))))
    ciou = np.mean(ciou)
    cious.append(ciou)
    
results = []
for i in range(21):
    result = np.sum(np.array(cious) >= 0.05 * i)
    result = result / len(cious)
    results.append(result)
x = [0.05 * i for i in range(21)]
auc = sklearn.metrics.auc(x, results)
print(auc, results[10])