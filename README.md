# AST

This repo is for developing a tool to help extract simple features out of ASTs dumped by GCC

The ast_bb_edge_labling.py is the code that is responsible for making the JSON files and extracting features out of AST.

The main c++ code should be in the same directory as the python script. The script will ask for the name of the c++ file and the name of the function that we wanted to extract features. Then it tries to dump all the trees of the GCC.
