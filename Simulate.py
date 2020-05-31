'''
    Author      : Maxwells_Demon
    Student ID  : 2019217954
    Encoding    : UTF-8
    Language    : Python 3.7.0
'''

from Game import *
import numpy as np
import pandas as pd
import os, sys
import json

class Simulate(object):

    # 初始化函数
    def __init__(self, mode, times):
        self.times = times
        self.mode = mode
        
        self.path = sys.path[0]
        js = open(self.path + '\\' +'config.json', 'r', encoding='utf-8')
        # 如果是预设的难度，就直接读取
        self.data = json.loads(js.read())[mode]

        # 如果不是预设的难度
        if mode == 'custom_density':
            self.data['mine_number'] = [i for i in range(self.data['min_mine_number'], \
                                        self.data['max_mine_number']+1, self.data['step'])]
        if mode == 'custom_shape':
            self.data['height'] = [self.data['area'] // i for i in self.data['width']]
        if mode == 'custom_area':
            # 这里似乎不需要别的操作
            pass

    # 开始模拟
    def start(self):
        if self.mode in ['easy', 'normal', 'hard']:
            self.default()
        else:
            self.custom()
    
    # 预设值模拟
    def default(self):
        # 记录的数据有：种子、运行结果、耗时、是否打开地图、随机碰运气次数
        df = pd.DataFrame(columns=['Seed', 'Result', 'Time', 'Discovered', 'Random times'])
        for i in range(self.times):
            print('Mode:%s. Number %d simulating... %.2f%% complete'%(self.mode, i+1, (i+1)*100/self.times))
            b = Game(width=self.data['width'], height=self.data['height'], 
                        mine_number=self.data['mine_number'], seed=np.random.randint(2147483647))
            b.mainloop()
            d = {
                'Seed'      : b.seed,
                'Result'    : 'Win' if b.game_flag == 1 else 'Fail',
                'Time'      : b.tot_time,
                'Discovered': 'True' if b.discovered / (b.width * b.height) > 0.8 else 'False',
                'Random times': b.rand_time
            }
            df = df.append(d, ignore_index=True)
        # 结束后写入文件
        df.to_csv(self.path + '\\' + self.mode + '.csv', index=True)

    # 自定义模拟
    def custom(self):
        # 将数据格式化，便于操作
        custom_data = []
        if self.mode == 'custom_density':
            for mine_number in self.data['mine_number']:
                tmp_data = {
                    'width': self.data['width'],
                    'height': self.data['height'],
                    'mine_number': mine_number
                }
                custom_data.append(tmp_data)
        if self.mode == 'custom_shape':
            for shape in zip(self.data['width'], self.data['height']):
                tmp_data = {
                    'width': shape[0],
                    'height': shape[1],
                    'mine_number': self.data['mine_number']
                }
                custom_data.append(tmp_data)
        if self.mode == 'custom_area':
            for shape in zip(self.data['side_length'], self.data['mine_number']):
                tmp_data = {
                    'width': shape[0],
                    'height': shape[0],
                    'mine_number': shape[1]
                }
                custom_data.append(tmp_data)

        for tmp_data in custom_data:
            # 记录的数据有：种子、运行结果、耗时、是否打开地图、随机碰运气次数
            df = pd.DataFrame(columns=['Seed', 'Result', 'Time', 'Discovered', 'Random times'])
            for i in range(self.times):
                print('Mode:%s, width=%d, height=%d, mine_number=%d. Number %d is simulating... %.2f%% complete' 
                        %(self.mode, tmp_data['width'], tmp_data['height'], tmp_data['mine_number'], 
                            i+1, (i+1)*100/self.times))
                b = Game(width=tmp_data['width'], height=tmp_data['height'], 
                            mine_number=tmp_data['mine_number'], seed=np.random.randint(2147483647))
                b.mainloop()
                d = {
                    'Seed'      : b.seed,
                    'Result'    : 'Win' if b.game_flag == 1 else 'Fail',
                    'Time'      : b.tot_time,
                    'Discovered': 'True' if b.discovered / (b.width * b.height) > 0.8 else 'False',
                    'Random times': b.rand_time
                }
                df = df.append(d, ignore_index=True)
            df.to_csv(self.path + '\\' + self.mode + str(custom_data.index(tmp_data)) +'.csv', index=True)