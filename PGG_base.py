# _*_ coding:UTF-8 _*_
# 开发人员: 组织计算与组织智能-康洪炜，周佳
# 开发团队: 组织计算与组织智能
# 开发时间: ${2019-07-21} ${11:10}
# 文件名称: ${nx_PGG_2.0}.py
# 模块功能：基于复杂网络公共物品博弈基类
# 模块版本: ${2.0}
# 开发工具: ${Python 3.7.2 MSSql 2014}

import networkx as ne  # 导入复杂网络模型包，命名ne
import numpy as np
from random import choice
import math
import uuid
from xlrd import open_workbook
from xlutils.copy import copy
#from savegraph2mssql import Savegraph2SQLServer
# noinspection PyUnresolvedReferences
import matplotlib.pyplot as plt


alpha = 1
old_money_fac = 1
like = -5
unlike = 5
weaken = 1
T_value = 20


class PGGBase:
    # constructed function
    def __init__(self, graph_type, node_num, p0, graph_degree, saveDBflag):
        """
        初始化方法
            graph_type
                graph_type = {'regular_graph','erdos_renyi_graph','watts_strogatz_graph', 'barabasi_albert_graph'}
            node_num
                初始网络结点数
            p0
                初始网络结点选择C策略的概率
            graph_degree
                网络平均度
        """
        # create a complex network ID
        self.NetworkID = str(uuid.uuid1())
        self.graph_type = graph_type
        self.p0 = p0
        #self.saveDBflag = saveDBflag
        if graph_type == 'regular_graph':
            self.g = ne.random_graphs.random_regular_graph(graph_degree, node_num)
        elif graph_type == 'erdos_renyi_graph':
            self.g = ne.random_graphs.erdos_renyi_graph(node_num, 4/node_num)

            for n in self.g.nodes:
                if self.g.degree[n] == 0:
                    try:
                        nodes_mcsg = list(max(ne.connected_components(self.g), key=len))
                    except:
                        break
                    connect_to_nb = choice(nodes_mcsg)
                    self.g.add_edge(n, connect_to_nb)
                    self.g[n][connect_to_nb]['id'] = str(uuid.uuid1())
                    self.g[n][connect_to_nb]['Weight'] = 0

        elif graph_type == 'watts_strogatz_graph':
            self.g = ne.random_graphs.watts_strogatz_graph(node_num, 4, 0.005)


      
        elif graph_type == 'complete_graph':
            self.g =ne.random_graphs.complete_graph(node_num)

    
        else:
            self.g = ne.random_graphs.barabasi_albert_graph(node_num, graph_degree)
           

        # 创建MSSQL链接
        #if saveDBflag:
            #self.msg = Savegraph2SQLServer(server="localhost", user="sa", password="asdfhj", database="ComplexNetwork",
                                          # graph=self.g, NetworkID=self.NetworkID)
        #画图存放内容


        
        countnodeid = 0
        for n in self.g.nodes:
            self.g.nodes[n]['id'] = countnodeid
            self.g.nodes[n]['Money'] = 100
            if np.random.random() <= p0:  
                self.g.nodes[n]['Strategy'] = 'C'
            else:
                self.g.nodes[n]['Strategy'] = 'D'
            countnodeid += 1




        
        countedgeid = 0
        for n in self.g.edges:
            self.g.edges[n]['Satisfaction'] = [0,0]
            self.g.edges[n]['type'] = 'N'
            self.g.edges[n]['id'] = countedgeid
            self.g.edges[n]['Weight'] = 0
            self.g.edges[n]['income_i_o'] = 0
            self.g.edges[n]['income_i_p'] = 0
            self.g.edges[n]['income_j_o'] = 0
            self.g.edges[n]['income_j_p'] = 0
            countedgeid += 1

    # There are no nodes evolve rules in base class
    def nodes_evolve(self):
        pass

    # There are no edges evolve rules in base class
    def edges_evolve(self):
        pass

    
    def break_game(self, CCount):
        
        return CCount == 0 or CCount == self.g.number_of_nodes()

   
    def save_graph_stat_info(self, game_times, CCount):
        pass

    
    def fermi_fomula(self, n, LearnFrom):
        ret = False
        try:
            copy_poss = 1 / (1 + math.exp((self.g.nodes[n]['income'] - self.g.nodes[LearnFrom]['income'])*10))
        except:
            copy_poss = 0
        if copy_poss > np.random.random():
            self.g.nodes[n]['Strategy'] = self.g.nodes[LearnFrom]['Strategy']
            ret = True
        return ret

    
    def game(self, r, k, game_times):

        #if self.saveDBflag:
            #self.msg.SaveGraphEnv(P0=self.p0, r=r, k=k, gtimes=game_times, NodeNum=self.g.number_of_nodes(),
        #n_count = 0#记录博弈运行次数                          #NWType=self.graph_type, PGGClassName=self.__class__.__name__)

        for i in range(game_times):
            #0n_count += 1

            iCCount = 0


            for n in self.g.nodes:
                if self.g.nodes[n]['Strategy'] == 'C':
                    iCCount += 1
            #print('第',i,'次',iCCount)

            degree = ne.degree_histogram(self.g)

            for n in self.g.nodes:
                self.g.nodes[n]['income'] = 0

            for n, nbrs in self.g.adj.items():

                # 如果为孤立结点，则其收益为0
                if self.g.degree[n] == 0:
                    self.g.nodes[n]['income'] = 0
                    continue

                nc = 0
                # nc为团体中合作者的数量
                for nbr, eattr in nbrs.items():
                    st = self.g.nodes[nbr]['Strategy']
                    if st == 'C':
                        nc = nc + 1

                if self.g.nodes[n]['Strategy'] == 'C':
                    nc = nc + 1
                # pc = (r * nc / (self.g.degree[n] + 1) - 1) * alpha
                # pd = (r * nc / (self.g.degree[n] + 1)) * alpha

                pc = (r * ( nc ) / (self.g.degree[n] + 1 ) - 1)
                pd = (r * ( nc ) / (self.g.degree[n] + 1 ) )

                self.g.nodes[n]['Nc'] = nc
                if self.g.nodes[n]['Strategy'] == 'C':
                    self.g.nodes[n]['income'] = self.g.nodes[n]['income'] + pc
                else:
                    self.g.nodes[n]['income'] = self.g.nodes[n]['income'] + pd

                for nbr, eattr in nbrs.items():
                    if self.g.nodes[nbr]['Strategy'] == 'C':
                        self.g.nodes[nbr]['income'] = self.g.nodes[nbr]['income'] + pc
                        if self.g[n][nbr]['income_j_p'] == 0:   
                            self.g[n][nbr]['income_j_p'] = pc
                        else:
                            self.g[n][nbr]['income_i_p'] = pc
                        if self.g.nodes[n]['Strategy'] == 'D':
                            if self.g[n][nbr]['income_i_o'] == 0:   
                                self.g[n][nbr]['income_i_o'] = r / (self.g.degree[n] + 1)
                            else:
                                self.g[n][nbr]['income_j_o'] = r / (self.g.degree[n] + 1)
                        else:
                            if self.g[n][nbr]['income_i_o'] == 0:
                                self.g[n][nbr]['income_i_o'] = r / (self.g.degree[n] + 1) - 1/(self.g.degree[n] + 1)
                            else:
                                self.g[n][nbr]['income_j_o'] = r / (self.g.degree[n] + 1) - 1/(self.g.degree[n] + 1)
                    else:
                        self.g.nodes[nbr]['income'] = self.g.nodes[nbr]['income'] + pd
                        if self.g[n][nbr]['income_j_p'] == 0:
                            self.g[n][nbr]['income_j_p'] = pd
                        else:
                            self.g[n][nbr]['income_i_p'] = pc
                        if self.g.nodes[n]['Strategy'] == 'D':
                            if self.g[n][nbr]['income_i_o'] == 0:
                                self.g[n][nbr]['income_i_o'] = 0.0
                            else:
                                self.g[n][nbr]['income_j_o'] = 0.0
                        else:
                            if self.g[n][nbr]['income_i_o'] == 0:
                                self.g[n][nbr]['income_i_o'] = -1/(self.g.degree[n] + 1)
                            else:
                                self.g[n][nbr]['income_j_o'] = -1/(self.g.degree[n] + 1)

            for n in self.g.nodes:
                self.g.nodes[n]['Money'] = self.g.nodes[n]['Money']+ self.g.nodes[n]['income']

            for u,v in self.g.edges:

                if self.g.nodes[u]['Strategy'] == 'C' and self.g.nodes[v]['Strategy'] == 'C':
                    self.g[u][v]['Satisfaction'][0] += like
                    self.g[u][v]['Satisfaction'][1] += like
                elif self.g.nodes[u]['Strategy'] == 'D' and self.g.nodes[v]['Strategy'] == 'C':
                    if self.g.nodes[u]['id'] > self.g.nodes[v]['id']:
                        self.g[u][v]['Satisfaction'][0] += like
                        self.g[u][v]['Satisfaction'][1] += unlike
                    else:
                        self.g[u][v]['Satisfaction'][0] += unlike
                        self.g[u][v]['Satisfaction'][1] += like
                elif self.g.nodes[u]['Strategy'] == 'C' and self.g.nodes[v]['Strategy'] == 'D':
                    if self.g.nodes[u]['id'] > self.g.nodes[v]['id']:
                        self.g[u][v]['Satisfaction'][0] += unlike
                        self.g[u][v]['Satisfaction'][1] += like
                    else:
                        self.g[u][v]['Satisfaction'][0] += like
                        self.g[u][v]['Satisfaction'][1] += unlike
                else:
                    self.g[u][v]['Satisfaction'][0] += weaken
                    self.g[u][v]['Satisfaction'][1] += weaken

                if self.g[u][v]['Satisfaction'][0] < -T_value:
                    self.g[u][v]['Satisfaction'][0] = -T_value
                if self.g[u][v]['Satisfaction'][1] < -T_value:
                    self.g[u][v]['Satisfaction'][1] = -T_value
                if self.g[u][v]['Satisfaction'][0] > T_value:
                    self.g[u][v]['Satisfaction'][0] = T_value
                if self.g[u][v]['Satisfaction'][1] > T_value:
                    self.g[u][v]['Satisfaction'][1] = T_value





            '''
            for u, v in self.g.edges:
                if self.g[u][v]['income_i_o']+self.g[u][v]['income_i_p'] > 0:
                    self.g[u][v]['Weight'] = self.g[u][v]['Weight'] - 1
                if self.g[u][v]['income_i_o']+self.g[u][v]['income_i_p'] < 0:
                    self.g[u][v]['Weight'] = self.g[u][v]['Weight'] + 3
                if self.g[u][v]['income_j_o'] + self.g[u][v]['income_j_p'] > 0:
                    self.g[u][v]['Weight'] = self.g[u][v]['Weight'] - 1
                if self.g[u][v]['income_j_o'] + self.g[u][v]['income_j_p'] < 0:
                    self.g[u][v]['Weight'] = self.g[u][v]['Weight'] + 3
                if self.g[u][v]['income_i_o']+self.g[u][v]['income_i_p'] == 0:
                    self.g[u][v]['Weight'] = self.g[u][v]['Weight'] + 1
                if self.g[u][v]['Weight'] < -20:
                    self.g[u][v]['Weight'] = -20
                if self.g[u][v]['Weight'] > 20:
                    self.g[u][v]['Weight'] = 20
            '''


                # print(u, v, self.g[u][v])
                # print(self.g.degree)
                # print(len(self.g.edges))
            #if self.saveDBflag:
                #self.save_graph_stat_info(i, iCCount)
                #self.msg.SaveGraph(i)

            '''
            node_colors = []
            for n in self.g.nodes:
                if self.g.nodes[n]['Strategy']=='C':
                    node_colors.insert(n,'b')
                else:
                    node_colors.insert(n,'r')
                pos=ne.spring_layout(self.g)
                ne.draw(self.g, pos, with_labels=True, node_size=30, node_color=node_colors)
                plt.show()
            '''

            if self.break_game(iCCount):
                break
            #if n_count >= 1:
            self.edges_evolve()
                #n_count = 0

            self.nodes_evolve()

            for n, nbrs in self.g.adj.items():
                nb_set = []
                for nbr, eattr in nbrs.items():
                    nb_set.append(nbr)
                if len(nb_set) > 0 :
                    learn_from_nb = choice(nb_set)

                    # Fermi表达式
                    self.fermi_fomula(n, learn_from_nb)




        print(iCCount)
        degree = ne.degree_histogram(self.g)  
        print(degree)

        r_xls = open_workbook("sensitive.xlsx")  
        row = r_xls.sheets()[0].nrows 
        excel = copy(r_xls)  
        table = excel.get_sheet(0)  
        table.write(row, 0, iCCount)

        '''
        for col in range(0,len(degree)):
            table.write(row + 1, col, degree[col])
        '''
        excel.save("sensitive.xlsx")  




def main():
    repeat_times = 20

    p0 = 0.6
    r = 1.0
    k = 0.1
    game_times = 1000  
    node_num = 1000


    '''
    while r < 0.11:
        i = 0
        while i < repeat_times:
            ge = NxPGGBase('regular_graph', node_num, p0, 4, True)
            ge.game(r=r, k=k, game_times=game_times)
            i += 1
        r += 0.1
    '''

    while r < 8.01:
        print('r=',r)

        i = 0
        while i < repeat_times:
            ge = PGGBase('regular_graph', node_num, p0, 4, True)
            ge.game(r=r, k=k, game_times=game_times)
            i += 1
        r += 0.1


if __name__ == '__main__':
    main()