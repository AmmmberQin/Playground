# -*- coding: utf-8 -*-
# @Author: Li Qin
# @Date:   2018-12-07 14:48:30
# @Last Modified by:   Li Qin
# @Last Modified time: 2018-12-14 15:05:51
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

class LifeGame():
    def __init__(self, w, h, mode=2):
        self.on = 255
        self.off = 0
        self.w = w
        self.h = h
        if mode == 0:
            self.grid = self.random_grid(w, h)
        elif mode == 1:
            self.grid = self.init_grid_in_place(1, 1, self.normalstart())
        elif mode == 2:
            self.grid = self.init_grid_in_place(1, 1, self.gosperGun())
        else:
            raise Exception("Unknow mode")
        

    def update(self, frameNum, img):
        next_round = np.full((self.w, self.h), self.off)
        directions = [(0,1),(0,-1),(1,0),(-1,0),(1,1),(1,-1),(-1,1),(-1,-1)]
        for r in range(self.w):
            for c in range(self.h):
                t = sum(self.grid[(r+i)%self.w, (c+j)%self.h] == self.on for i, j in directions)
                if self.grid[r, c] == self.on:
                    if t < 2 or t > 3:
                        next_round[r, c] = self.off
                    else:
                        next_round[r, c] = self.on
                else:
                    if t == 3:
                        next_round[r, c] = self.on
                    else:
                        next_round[r, c] = self.off
        img.set_data(next_round)
        self.grid[:] = next_round[:]
        return img

    def random_grid(self):
        return np.random.choice([self.off,self.on], self.w*self.h, p=[0.3, 0.7]).reshape(self.w,self.h)

    def gosperGun(self):
        w = 11
        h = 38
        grid = np.full((w, h), self.off)
        ons = [(5,1),(5,2),(6,1),(6,2),(5,11),(6,11),(7,11),(8,12),(9,13),(9,14),(8,16),
        (7,17),(6,17),(5,17),(6,18),(4,16),(4,12),(3,13),(3,14),(6,15),(5,21),(5,22),
        (4,21),(4,22),(3,21),(3,22),(2,13),(6,23),(2,25),(1,25),(6,25),(7,25),(3,35),
        (3,36),(4,35),(4,36)]

        for i,j in ons:
            grid[i,j] = self.on 
        return grid

    def normalstart(self):
        return np.array([[self.off, self.off, self.on], 
                         [self.on, self.off, self.on], 
                         [self.off, self.on, self.on]])

    def init_grid_in_place(self, i, j, grid):
        glider = np.full((self.w, self.h), self.off)
        n, m = grid.shape
        glider[i:i+n, j:j+m] = grid
        return glider

def update(frameNum, img, game):
    return game.update(frameNum, img)



if __name__ == "__main__":
    updateInterval = 100
    game = LifeGame(100, 100)
    fig, ax = plt.subplots()
    img = ax.imshow(game.grid, interpolation="nearest")
    ani = animation.FuncAnimation(fig, 
                                  update, 
                                  fargs=(img, game), 
                                  frames=10,
                                  interval=updateInterval,
                                  save_count=50)
    # cid = fig.canvas.mpl_connect('button_press_event')
    plt.show()

