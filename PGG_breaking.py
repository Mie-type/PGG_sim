# coding = utf-8
import networkx as ne  # 导入建网络模型包，命名ne
import numpy as np
from random import choice
import math
import uuid
#from savegraph2mssql import Savegraph2SQLServer
from sensitiveT import PGGBase
import matplotlib.pyplot as plt

#PoissonCDF = [0.0000, 0.0005, 0.0076, 0.0458, 0.1550, 0.3472, 0.5760, 0.7720, 0.8987, 0.9626, 0.9884]
#PoissonCDF = [0.0000, 0.0404, 0.1246, 0.2650, 0.4404, 0.6159, 0.7621, 0.8666, 0.9319, 0.9681, 0.9863,0.9945,0.9979,0.9993,0.9997,0.99993,0.99998,0.99999,0.99999,0.99999,0.99999]
T_value = 40
PoissonCDF = [0.000000000,
              0.000499399,
              0.002769396,
              0.010336051,
              0.029252688,
              0.067085963,
              0.130141421,
              0.220220647,
              0.332819679,
              0.457929714,
              0.583039750,
              0.696776146,
              0.791556476,
              0.864464423,
              0.916541527,
              0.951259597,
              0.972958390,
              0.985722386,
              0.992813495,
              0.996545658,
              0.998411739,
              0.999300349,
              0.999704263,
              0.999704263,
              0.999953050,
              0.999982319,
              0.999993577,
              0.999997746,
              0.999999235,
              0.999999749,
              0.999999920,
              0.999999975,
              0.999999992,
              0.999999997,
              0.999999999,
              1,
              1,
              1,
              1,
              1,
              1]




class PGG_Edge_Breaking_Rule(PGGBase):

    def edges_evolve(self):
        #edge_remove_list = []

        for u, v in self.g.edges:
            d_times0 = int(self.g[u][v]['Satisfaction'][0])
            if d_times0 > T_value:
                d_times0 = T_value
            if d_times0 < 0:
                d_times0 = 0
            d_times1 = int(self.g[u][v]['Satisfaction'][1])
            if d_times1 > T_value:
                d_times1 = T_value
            if d_times1 < 0:
                d_times1 = 0
            p_remove_edge0 = PoissonCDF[d_times0]
            p_remove_edge1 = PoissonCDF[d_times1]

            if p_remove_edge0 > np.random.random() or p_remove_edge1 > np.random.random():

                self.g.remove_edge(u,v)
                if self.g.nodes[u]['Strategy'] == 'C':
                    oldnode = u
                else:
                    oldnode = v

                newnodes = []
               
                surroundings = 0
                surrounding = 0
                for neighbor in self.g.neighbors(oldnode):
                    if self.g.nodes[oldnode]['id'] > self.g.nodes[neighbor]['id']:
                        surroundings = surroundings + self.g[oldnode][neighbor]['Satisfaction'][0]
                    else:
                        surroundings = surroundings + self.g[oldnode][neighbor]['Satisfaction'][1]

                if self.g.degree[oldnode] != 0:
                    surrounding = surroundings/self.g.degree[oldnode]

                part_choice = (1 / (1 + np.exp(-surrounding)))
                #part_choice = surrounding/20
                #like = -5 and unlike = 5 and r = 2.9
                if np.random.random() > part_choice and surroundings < 0 and self.g.degree[oldnode] != 0:
                        
                    for neighbor in self.g.neighbors(oldnode):
                        if self.g.nodes[oldnode]['id'] > self.g.nodes[neighbor]['id']:
                            key = self.g[oldnode][neighbor]['Satisfaction'][0]
                        else:
                            key = surroundings + self.g[oldnode][neighbor]['Satisfaction'][1]

                        for k_nei in self.g.neighbors(neighbor):
                            if self.g.has_edge(oldnode,k_nei) == False:
                                newnodes.append(k_nei)
                    if newnodes != []:
                        newnode = choice(newnodes)
                        #if len(newnodes) != 0:
                            #print('内部选择')
                if newnodes == []:
                   
                    for j in self.g.nodes:
                        if (self.g.nodes[j]['id'] != self.g.nodes[u]) and (
                                self.g.nodes[j]['id'] != self.g.nodes[v]) and self.g.has_edge(oldnode,j) == False:
                            newnodes.append(j)
                    newnode = choice(newnodes)

                #newnode = choice(newnodes)

                self.g.add_edge(newnode, oldnode)

                self.g[oldnode][newnode]['id'] = str(uuid.uuid1())
                self.g[oldnode][newnode]['Satisfaction'] = [0,0]
                self.g[oldnode][newnode]['Weight'] = 0
                self.g[oldnode][newnode]['income_i_o'] = 0
                self.g[oldnode][newnode]['income_i_p'] = 0
                self.g[oldnode][newnode]['income_j_o'] = 0
                self.g[oldnode][newnode]['income_j_p'] = 0
                    #edge_remove_list.append(edge_remove)
        #self.g.remove_edges_from(edge_remove_list)
        '''
        for i in edge_remove_list:
            if np.random.random() > 0:
                #print('fc',fc)
                newnodes = []
                for j in self.g.nodes:
                    if (self.g.nodes[j]['id'] != self.g.nodes[i[0]]) and (self.g.nodes[j]['id'] != self.g.nodes[i[1]]):
                        newnodes.append(j)
                newnode = choice(newnodes)
                if self.g.nodes[i[0]]['Strategy'] == 'C':
                    oldnode = i[0]
                    self.g.add_edge(newnode,i[0])
                else:
                    self.g.add_edge(newnode, i[1])
                    oldnode = i[1]

                self.g[oldnode][newnode]['id'] = str(uuid.uuid1())
                self.g[oldnode][newnode]['Weight'] = 0
                self.g[oldnode][newnode]['type'] = 'N'
                self.g[oldnode][newnode]['income_i_o'] = 0
                self.g[oldnode][newnode]['income_i_p'] = 0
                self.g[oldnode][newnode]['income_j_o'] = 0
                self.g[oldnode][newnode]['income_j_p'] = 0
        '''


    def break_game(self, CCount):
        return self.g.number_of_edges()==0 or CCount == self.g.number_of_nodes()

    #def save_graph_stat_info(self, game_times, CCount):
        #self.msg.SaveGraphMDe(game_times, CCount)


def main():
    repeat_times = 10

    p0 = 0.55
    k = 0.1
    game_times = 1000 
    node_num = 1000
    '''
    r = 1.0
    while r < 8.01:
        i = 0
        while i < repeat_times:
            ge = NxPGG_Edge_Rule1('regular_graph', node_num, p0, 4, True)
            ge.game(r=r, k=k, game_times=game_times)
            i += 1
        r += 1.0
    '''
    r = 2
    while r < 2.001:
        print('r:',r)
        i = 0
        while i < repeat_times:
            ge = PGG_Edge_Breaking_Rule('regular_graph', node_num, p0, 4, True)
            ge.game(r=r, k=k, game_times=game_times)
            i += 1
        r += 0.1




if __name__ == '__main__':
    main()