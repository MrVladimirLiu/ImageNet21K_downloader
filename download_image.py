import argparse
import os
import threading
import urllib
import glob
import urllib.request
import json
import numpy as np
import sys
import time

data_dir = '../data/'



def clean(path):
    exist_file = os.listdir(path)
    cnt = 0
    for filename in exist_file:
        name, ext = os.path.splitext(filename)
        if ext != '':
            cnt +=1
            if ext =='.tar':
                cmd = 'rm ' + os.path.join(path, filename)
            if ext =='.lock':
                cmd = 'rm -r %s' % os.path.join(path, filename)
            os.system(cmd)
    print('cleaned', cnt)


def report(count, blockSize, totalSize):
    percent = int(count*blockSize*100/totalSize)
    sys.stdout.write("\r%d%%" % percent + ' complete ')
    sys.stdout.flush()

def formatSize(bytes):
    try:
        bytes = float(bytes)
        kb = bytes / 1024
    except:
        print("传入的字节格式不对")
        return "Error"

    if kb >= 1024:
        M = kb / 1024
        if M >= 1024:
            G = M / 1024
            return "%fG" % (G)
        else:
            return "%fM" % (M)
    else:
        return "%fkb" % (kb)

def download(vid_file, path):
    with open(vid_file) as fp:
        vid_list = [line.strip() for line in fp]
    url_list = 'https://image-net.org/data/winter21_whole/'
    # url_key = '&username=%s&accesskey=%s&release=latest&src=stanford' % (args.user, args.key)
#    print(args.user)
#    print(args.key)

#    testfile = urllib.URLopener()
    exist_list = []
    exist_file = os.listdir(path)
    for filename in exist_file:
        name, ext = os.path.splitext(filename)
        if ext == '':
            exist_list.append(name)

    need_list = set(vid_list) - set(exist_list)
    need_list = list(need_list)
    # with open('vid_list.txt', 'w') as f:
    #     json.dump(vid_list,f)
    # with open('exist_list.txt', 'w') as f:
    #     json.dump(exist_list, f)
    # with open('need_list.txt', 'w') as f:
    #     json.dump(need_list, f)
    print('All: ', len(vid_list))
    print('Exist: ', len(exist_list))
    print('Need download: ', len(need_list))

    for i in range(len(need_list)):
        wnid = need_list[i]
#        print(wnid)
        url_acc = url_list + wnid + '.tar' #+ url_key
#        print(url_acc)
        save_dir = os.path.join(scratch_dir, wnid)
        lockname = save_dir + '.lock'
        if i % 10 == 0:
            print('%d / %d' % (i, len(need_list)))
        #print(lockname)
        if os.path.exists(save_dir):
            #print('1')
            continue
        if os.path.exists(lockname):
            #print('2')
            continue
        try:
            #print(lockname)
            os.makedirs(lockname)
        except:
            continue
        tar_file = os.path.join(scratch_dir, wnid + '.tar')
        #print(tar_file)
        try:
            #print('D')
            urllib.request.urlretrieve(url_acc, tar_file, reporthook=report)
            size = os.path.getsize(tar_file)
            size = formatSize(size)
            print('%s Download %s ' % (size, wnid))
            sys.stdout.flush()
        except:
            print('!!! Error when downloading', wnid)
            continue

        if not os.path.exists(os.path.join(scratch_dir, wnid)):
            os.makedirs(os.path.join(scratch_dir, wnid))
        cmd = 'tar -xf ' + tar_file + ' --directory ' + save_dir
        os.system(cmd)
        cmd = 'rm ' + os.path.join(tar_file)
        os.system(cmd)
        cmd = 'rm -r %s' % lockname
        os.system(cmd)


def rm_empty(vid_file):
    with open(vid_file) as fp:
        vid_list = [line.strip() for line in fp]
    cnt = 0
    for i in range(len(vid_list)):
        save_dir = os.path.join(scratch_dir, vid_list[i])
        jpg_list = glob.glob(save_dir + '/*.JPEG')
        if len(jpg_list) < 10:
            print(vid_list[i])
            cmd = 'rm -r %s ' % save_dir
            os.system(cmd)
            cnt += 1
    print(cnt)




def parse_arg():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--save_dir', type=str, default='/home/ljx/data/images',
                        help='path to save images')
    parser.add_argument('--multi', type=str, default='0',
                        help='multiprocess(1) or not(0)')
    args = parser.parse_args()
    if args.save_dir is None:
        print('Please set directory to save images')
    return args


args = parse_arg()
scratch_dir = args.save_dir
multi = args.multi

if __name__ == '__main__':

    list_file = 'winter_2021.txt'
    if multi == '0':
        clean(scratch_dir)
    download(list_file, scratch_dir)


