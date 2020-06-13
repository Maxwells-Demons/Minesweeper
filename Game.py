'''
    Author      : Maxwells_Demon
    Student ID  : 2019217954
    Encoding    : UTF-8
    Language    : Python 3.7.0
'''

import numpy as np
import random
from scipy.signal import convolve2d
from queue import Queue
import time
import os,sys

class Game(object):

    # 初始化
    def __init__(self, width = 10, height = 10, mine_number = 10, seed = np.random.randint(2147483647), debug = 0, delay = -1):
        # 初始化各项属性
        self.width, self.height = width, height
        self.mine_number = mine_number
        self.seed = seed
        self.delay = delay
        np.random.seed(seed)    # 初始化随机数种子
        random.seed(seed)
        self.missions = Queue()
        self.debug = debug      # 为1代表调试模式，可观看扫雷过程

        # 初始化01向量board，1代表地雷
        self.board = np.ones(mine_number)
        self.board = np.append(self.board, np.zeros(width * height -mine_number))
        # 打乱顺序，把board重整为矩阵
        np.random.shuffle(self.board)
        self.board = self.board.reshape(width, height)
        self.board = self.board.astype(int)
        '''
        矩阵number记录雷数
        为了在雷数矩阵中区分普通数字以及地雷，我们特意设置卷积核矩阵中心为10，
        以确保在雷数矩阵中，地雷位置的元素值大于9，方便我们加以区分。
        '''
        self.number = convolve2d(self.board, [[1, 1, 1], [1, 10, 1], [1, 1, 1]], 'same')
        self.number = self.number.astype(int)
        '''
        矩阵know用于记录已知区域的情况
        在已知矩阵know中（初始全为-1）:
            -1，表示该处情况未知【显示'■'('-')】
            >0时，1-8表示该处情况已知且周围有雷
            ==0时，表示该处情况已知且周围无雷
            -2，表示该处标记为雷【显示'●'('*')】
        '''
        self.know = -np.ones(width * height).reshape(width, height)
        self.know = self.know.astype(int)
        # 游戏状态，0代表正常，1代表胜利，其余代表失败
        self.game_flag = 0
        # 如果靠逻辑搞不出来了，随机碰运气的次数
        self.rand_time = 0

    # 便于使用print()直接输出扫雷情况
    def __str__(self, mine = '*', unknown='-'):
        def __num2mine__(number, mine = mine):
            if number == -1:
                return ' ' + unknown
            elif number == -2:
                return ' ' + mine
            elif number > 9:
                return ' ' + mine
            elif number == 0:
                return '  '
            elif number == -666:
                return ' !' # 代表这里踩雷炸了
            return ' ' + str(int(number))
        self.know = self.know.transpose()
        all=''
        for i in range(0, self.height):
            line=''
            for j in range(0, self.width):
                line += __num2mine__(self.know[i][j])
            all += line + '\n'
        self.know = self.know.transpose()
        return all
    
    # 判断是否在边界内部
    def boundary(self, x, y):
        if (-1 < x < self.width) and (-1 < y < self.height): return True
        return False

    # 获取当前位置周围已知雷和未知格子的数量，返回元组
    def getCount(self, x, y):
        dx=[1, 1, 1, 0,-1,-1,-1, 0]
        dy=[1, 0,-1,-1,-1, 0, 1, 1]
        cnt1=0
        cnt2=0
        for i in range(len(dx)):
            nx = x + dx[i]
            ny = y + dy[i]
            if self.boundary(nx, ny) == True:
                if self.know[nx][ny] == -2:
                    cnt1 += 1
                if self.know[nx][ny] == -1:
                    cnt2 += 1
        return (cnt1,cnt2)
    
    # 未知的格子总共还有多少个
    def getUnknown(self):
        return sum(sum(self.know == -1))
    
    # 选取周围有未知格子的已知格子，将其放入队列
    def putKnown(self):
        dx=[1, 1, 1, 0,-1,-1,-1, 0]
        dy=[1, 0,-1,-1,-1, 0, 1, 1]
        s = set()   # 用集合去重
        for i in range(self.width):
            for j in range(self.height):
                if self.know[i][j] == -1:
                    for k in range(len(dx)):
                        nx = i + dx[k]
                        ny = j + dy[k]
                        if self.boundary(nx, ny) and 0 < self.know[nx][ny] < 9:
                            s.add((nx, ny))
        for i in s:
            self.missions.put(i)
        return s

    # 开始时随机选取一个空格子
    def empty_choice(self):
        l=[]
        for i in range(self.width):
            for j in range(self.height):
                if self.number[i][j] == 0:
                    l.append((i,j))
        return random.choice(l)

    # 从当前没来过的格子中随机选取一个
    def rand_choice(self):
        l=[]
        for i in range(self.width):
            for j in range(self.height):
                if self.know[i][j] == -1:
                    l.append((i,j))
        return random.choice(l)
    
    # 给周围未知格子标上雷
    def markUnknown(self, x, y):
        dx=[1, 1, 1, 0,-1,-1,-1, 0]
        dy=[1, 0,-1,-1,-1, 0, 1, 1]
        for i in range(len(dx)):
            nx = x + dx[i]
            ny = y + dy[i]
            if self.boundary(nx, ny) == True and self.know[nx][ny] == -1:
                self.know[nx][ny] = -2
    
    # 打开周围未知的格子
    def openUnknown(self, x, y):
        dx=[1, 1, 1, 0,-1,-1,-1, 0]
        dy=[1, 0,-1,-1,-1, 0, 1, 1]
        for i in range(len(dx)):
            nx = x + dx[i]
            ny = y + dy[i]
            if self.boundary(nx, ny) == True and self.know[nx][ny] == -1:
                self.know[nx][ny] = self.number[nx][ny]
                self.missions.put((nx, ny))

    # 调试打印函数，可以标明当前位置
    def debug_print(self, x, y):
        def __num2mine__(number, sp, mine = '*'):
            if number == -1:
                return sp + '-'
            elif number == -2:
                return sp + mine
            elif number > 9:
                return sp + mine
            elif number == 0:
                return sp+' '
            elif number == -666:
                return sp+'!' # 代表这里踩雷炸了
            return sp + str(int(number))
        
        if self.delay < 0:
            os.system('pause')
        else:
            time.sleep(self.delay)
        os.system('cls')

        for i in range(0, self.width):
            line=''
            for j in range(0, self.height):
                if i == x and j == y:
                    line += __num2mine__(self.know[i][j], 'X')
                else:
                    line += __num2mine__(self.know[i][j], ' ')
            print(line)

    # 广度优先，层次遍历
    def bfs(self):
        while not self.missions.empty() and self.game_flag == 0:
            tmp = self.missions.get()
            nowx = tmp[0]
            nowy = tmp[1]
            # 以下是简单的逻辑判断
            # 如果这个位置是数字
            if 0 < self.number[nowx][nowy] < 9:
                self.know[nowx][nowy] = self.number[nowx][nowy]
                num_count = self.getCount(nowx, nowy)
                # 如果周围未知格子和标记过的雷数量之和等于这个数字，说明剩下的未知格子全都是雷，把未知格子打上雷的标记
                if num_count[0] + num_count[1] == self.know[nowx][nowy]:
                    self.markUnknown(nowx, nowy)
                # 如果周围标记过的雷的数量等于当前数字，就把周围未知的格子全部打开
                elif num_count[0] == self.number[nowx][nowy]:
                    self.openUnknown(nowx, nowy)
            # 如果这个位置是空的
            elif self.number[nowx][nowy] == 0:
                self.know[nowx][nowy] = 0
                self.openUnknown(nowx, nowy)
            # 如果这个位置是地雷，那么游戏结束
            elif self.number[nowx][nowy] > 9:
                self.game_flag = 2
                self.know[nowx][nowy] = -666
            
            # 调试模式，输出每一步
            if self.debug == 1:
                self.debug_print(nowx, nowy)
                print(nowx, nowy)
    
    # 组合逻辑推导，本作品精华中的精华，烧毁了我无数的脑细胞
    def logic(self, edge_set):
        # 获得某个格子周围的格子的集合
        def get_surround(x, y, mode):
            ans = set()
            dx=[1, 1, 1, 0,-1,-1,-1, 0]
            dy=[1, 0,-1,-1,-1, 0, 1, 1]
            for i in dx:
                for j in dy:
                    nx = x + i
                    ny = y + j
                    if self.boundary(nx, ny) == False:  continue
                    if 0 < self.know[nx][ny] < 9 and mode == 'digit':
                        ans.add((nx, ny))
                    if self.know[nx][ny] == -2 and mode == 'mine':
                        ans.add((nx,ny))
                    if self.know[nx][ny] == -1 and mode == 'unknown':
                        ans.add((nx,ny))
            return ans
        
        # 统计集合中，未知格子和已标记雷的数量
        def count_set(surround):
            d = {
                'mine': 0,
                'unknown': 0
            }
            for pos in surround:
                if self.know[pos[0]][pos[1]] == -1:
                    d['unknown'] += 1
                if self.know[pos[0]][pos[1]] == -2:
                    d['mine'] += 1
            return d

        result = 0 # 本次逻辑操作数
        
        for now in edge_set:
            neighs = get_surround(now[0], now[1], mode='digit')
            # 扫自己周围的那些有效的数字格子（能够用于未知格子的判断）
            for neigh in neighs & edge_set:
                now_val = self.know[now[0]][now[1]]
                neigh_val = self.know[neigh[0]][neigh[1]]

                # 获得这两个格子周围标记的雷和未知格子
                now_surround = get_surround(now[0], now[1], mode='mine') | get_surround(now[0], now[1], mode='unknown')
                neigh_surround = get_surround(neigh[0], neigh[1], mode='mine') | get_surround(neigh[0], neigh[1], mode='unknown')
                
                # 双方共享的格子share
                share = now_surround & neigh_surround
                # 双方自己所在的两个格子selves
                selves = {(now[0], now[1]), (neigh[0], neigh[1])}

                # 删除掉共享的和自己的格子后，剩下的私有的格子
                now_surround = now_surround - share - selves
                neigh_surround = neigh_surround - share - selves

                # 统计两个格子周围各种格子的数量
                now_dict = count_set(now_surround)
                neigh_dict = count_set(neigh_surround)
                share_dict = count_set(share)

                # 如果now在公共最多存在的地雷数 = neigh在公共最少存在的地雷数
                if min(now_val - now_dict['mine'] - share_dict['mine'], 2) == \
                    neigh_val - neigh_dict['mine'] - neigh_dict['unknown'] - share_dict['mine'] and \
                        share_dict['unknown'] == 2:
                        # neigh未知的格子都标上雷
                        for pos in neigh_surround:
                            if self.know[pos[0]][pos[1]] == -1:
                                self.know[pos[0]][pos[1]] = -2
                                result += 1
                                break
                        # 调试模式，输出每一步
                        if self.debug == 1:
                            self.debug_print(now[0], now[1])
                            print(now[0], now[1])
                        continue
                # 如果now在公共最少存在的地雷数 = neigh所有的雷
                if share_dict['unknown'] == 2 and \
                    now_val - now_dict['unknown'] - now_dict['mine'] - share_dict['mine'] == 1 and \
                        neigh_val - neigh_dict['mine'] - share_dict['mine'] == 1:
                        # neigh未知的格子都打开，这里记得入广搜的队列
                        for pos in neigh_surround:
                            if self.know[pos[0]][pos[1]] == -1:
                                self.know[pos[0]][pos[1]] = self.number[pos[0]][pos[1]]
                                self.missions.put(pos)
                                result += 1
                                break
                        # 调试模式，输出每一步
                        if self.debug == 1:
                            self.debug_print(now[0], now[1])
                            print(now[0], now[1])
                        continue

        return result

    # 主循环
    def mainloop(self):
        # 一开始选取到的必定是空格子
        self.missions.put(self.empty_choice())

        # 添加计时器
        start = time.time()
        unknown_last = 0    # 上次循环结束后，未知的格子数
        # 游戏未结束时，进行循环
        while self.game_flag == 0:
            unknown_last = self.getUnknown()
            # 广搜里都是简单的逻辑判断
            self.bfs()
            # 每次搜完之后，尝试将与未知格子相邻的数字格子入队，继续进行简单逻辑判断
            edge_set = self.putKnown()

            unknown_mine = sum(sum(self.number > 10)) - sum(sum(self.know == -2))
            # 如果剩下的未知格子全都是地雷
            if self.getUnknown() == unknown_mine:
                # 把所有未知格子标上雷，然后就赢了
                for i in range(self.width):
                    for j in range(self.height):
                        if self.know[i][j] == -1:
                            self.know[i][j] == -2
                self.game_flag = 1
                break
            # 如果未知格子数量没有变，说明本轮没有进行任何开采
            if self.getUnknown() == unknown_last:
                # 这里就需要复杂逻辑了，复杂逻辑判断不出来再随机
                logic_result = self.logic(edge_set)
                if logic_result == 0 and self.getUnknown() != 0:
                    self.missions.put(self.rand_choice())
                    self.rand_time += 1

            if self.getUnknown() == 0:
                self.game_flag = 1
                break
        end = time.time()
        # 模拟耗时
        self.tot_time = end - start
        # 已发现的格子数
        self.discovered = self.width * self.height - sum(sum(self.know == -1))

