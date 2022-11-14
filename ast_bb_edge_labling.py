# Import library
#import numpy as np

# Reading file
filename = 'a-test.cpp.023t.ssa' 
f = open(filename, 'r')
lines = []
for line in f:
    lines.append(line)
f.close()

# Find nodes that have jumps/branches
branching_node = []
current_bb = 0
branch_bb = 0
main_scope = 0
last_bb = 0
for line in lines:

    line_words_list = line.split()  
    if 'main' in line_words_list:
        main_scope = 1
    if 'return' in line_words_list:
        main_scope = 0

    if main_scope:
        if 'goto' in line_words_list:
            flag_bb_found = 0
            for word in line_words_list:
                if word == '<bb':
                    flag_bb_found = 1
                elif flag_bb_found:
                    branch_bb = int(word.split(sep='>')[0])
                    flag_bb_found = 0
            branching_node.append([current_bb, branch_bb])
        else:
            flag_bb_found = 0
            for word in line_words_list:
                if word == '<bb':
                    flag_bb_found = 1
                elif flag_bb_found:
                    current_bb = int(word.split(sep='>')[0])
                    flag_bb_found = 0
                    if current_bb > last_bb:
                        last_bb = current_bb


bb_edge_type = dict()
for i in range(2,last_bb+1):
    occurence_num = 0
    for j in branching_node:
        if j[0] == i:
            occurence_num += 1
    
    if occurence_num > 1:
        bb_edge_type[i] = 'Multi-branch'
    elif occurence_num == 1:
        bb_edge_type[i] = 'Jump'
    else:
        bb_edge_type[i] = 'Simple'


print(bb_edge_type)
