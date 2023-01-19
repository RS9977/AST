# Import library
#import numpy as np
import json
import os

#Functions

#Check if a word (seprated by space) is a variable
def check_var(var, word):
    asciis = [x for x in range(60,91)]
    asciis.extend([x for x in range(97,123)])
    asciis.extend([x for x in range(48,58)])
    asciis.append(95)
    if var in word:
        if (' ' + var + '[' in word) or (' ' + var + '(' in word) or (' ' + var + ' ' in word):
            return True
        for x in asciis:
            if var + chr(x) in word:
                return False
        for x in asciis:
            if chr(x) + var in word:
                return False
        return True


# Reading original file
print('Please type the name of file (The C++ program)')
filename = input() 
lines_original = []
try:
    f = open(filename, 'r')
    lines_original = f.readlines()
    f.close()

    #Add a dumb main function to make it possible for gcc to compile
    f = open(filename, 'a+')
    f.write('\n')
    f.write('int main(){return 1;}')
    f.close()
except:
    print('There is no such file')


# Reading the AST file
lines = []
try:
    os.system('g++ ' + filename + ' -fdump-tree-ssa' + ' -o out.o')
    AST_filename = 'out.o-' + filename + '.023t.ssa' 
    f = open(AST_filename, 'r')
    for line in f:
        lines.append(line)
    f.close()
except:
    print('You have not dumped the corresponded AST and the program cannot do it either')

#Remove main to restore actual code
try:
    f = open(filename, 'w')
    for line in lines_original:
        f.write(line)
    f.close()
except:
    print('Cannot retrieve the file')

# Find nodes that have jumps/branches
current_bb     = 0
branch_bb      = 0
main_scope     = 0
last_bb        = 0
branching_node = []
loops          = []
loops_initials = []

param_nums     = 0

args = dict()

#All possible variables to be declared in the scope
cpp_var = ['char', 'char16_t', 'char32_t', 'wchar_t',
           'signed char', 'signed short int', 'short int', 'signed short', 'short', 'signed int', 'int', 'signed long int', 'signed long', 'long int', 'long', 'signed long long int', 'signed long long', 'long long int', 'long long',
           'unsigned char', 'unsigned short int', 'unsigned short', 'unsigned int', 'unsigned', 'unsigned long int', 'unsigned long', 'unsigned long long int', 'unsigned long long',
           'float', 'double', 'long double',
           'bool',
           'void',
           'decltype(nullptr)',
           'size_t']

#Asking for the name of specific function to make the json file for
print('please type the function name:')
function_name = input()

#Going through each line of the AST to extract the features
for line in lines:

    #make a list of words splitted by space out of each line
    line_words_list = line.split()

    #checking if the requried function has started  
    if function_name in line_words_list and ';;' not in line_words_list:
        main_scope    = 1
        inside_args   = 0
        val_flag      = 0
        previous_word = ''

        #Find the args of the function
        for word in line_words_list:
            if not inside_args and '(' in word:
                inside_args   = 1
                previous_word = word[1:]
                val_flag      = 1

            elif inside_args and val_flag:
                if ')' in word:
                    inside_args         = 0
                    args[word[0:len(word)-1]] = previous_word
                    val_flag            = 0
                elif '*' in word:
                    previous_word      += '*'
                else:
                    args[word[0:len(word)-1]] = previous_word
                    val_flag            = 0
            
            elif inside_args and not val_flag:
                previous_word = word
                val_flag      = 1

    #Checking for the end of the function       
    if '{' in line_words_list:
        param_nums += 1
    if '}' in line_words_list:
        param_nums -= 1
        if param_nums == 0:
            main_scope = 0

    #Finding the requried features inside the main scope of the function
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

            if(current_bb > branch_bb):
                loops.append([x for x in range(branch_bb, current_bb+1)])
                loops_initials.append(current_bb)

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


# Define type
bb_edge_type = dict()
for i in range(2,last_bb+1):
    occurence_num = 0
    for j in branching_node:
        if j[0] == i:
            occurence_num += 1
    if i in loops_initials:
        bb_edge_type[i] = 'Start of loop'
    elif occurence_num > 1:
        bb_edge_type[i] = 'Multi-branch'
   # elif occurence_num == 1:
   #     bb_edge_type[i] = 'End of loop'
    else:
        bb_edge_type[i] = 'Simple'

#Printing the extracting features
print("BBs:")
print(bb_edge_type)

print("Loops:")
print(loops)

print('args:')
print(args)

#Convert argumants dictionary to the json format and save the json file
json_args = dict()
i = 0
for key in args.keys():
    json_args['@'+str(i)] = [key, args[key]]
    i += 1

json_vars = list()
i = 0
for key in args.keys():
    var_dict = dict()
    var_dict['Name'] = key
    var_dict['Argument'] = i
    i += 1
    var_dict['Type'] = args[key]
    if '*' in args[key]:
        var_dict['pointer'] = 1
    else:
        var_dict['pointer'] = 0
    j = 0
    first_seen = 0
    write = 0
    #Finding lines associated to each variable
    for line in lines_original:
        if write:
            break
        j += 1
        words = line.split()
        ind_eq = -1
        ind_eq_flag = 0
        ind_var = -1
        ind_var_flag = 0
        for word in words:
            if not ind_eq_flag:
                ind_eq += 1
            if not ind_var_flag:
                ind_var += 1
            if '=' in word:
                ind_eq_flag = 1
            if check_var(key, word):
                ind_var_flag = 1
                if not first_seen:
                    var_dict['decalaration_line_num'] = j
                    first_seen = 1 
        if ind_eq > ind_var:
            write = 1
    var_dict['read_only'] = not write
    json_vars.append(var_dict)
            

j = 0
nested_level            = 0
loop_ID_cnt             = 0
Immediate_Outer_Loop_ID = 0
nesting_loops = []
Loops_list_dict = list()

insertion_point = dict()

functions_var = ['+', '-', '*', '/']

loops_lines = []

scope_look = 0
par_cnt    = 0
par_loop_dict = dict()
insertion_function = []
assignment_check = 0
assignment_line  = 0
function_name_check = 0
#Parsing the Actual code line by line so that extractin features and corresponding lines
for line in lines_original:
    temp_dict = dict()
    temp_loop_iter = dict()
    j += 1
    while_main_line     = 0
    for_main_line       = 0
    for_par             = 0
    iter_var            = 0
    iter_var_check      = 0
    word_cnt            = 0
    for word in line.split():
        #Here I assume that the global line is the line which is the function is defined
        if function_name in word:
            insertion_point['Global'] = j-1

        #Looking for loops  
        #Looking for (for) loops   
        if check_var('for', word):
            loops_lines.append({'Loop ID': loop_ID_cnt, 'Line': j})
        
        #Looking for (while) loops
        if check_var('while', word):
            loops_lines.append({'Loop ID': loop_ID_cnt, 'Line': j})

        #Find function name        
        if check_var(function_name, word):
            function_name_check = 1
        if function_name_check:
            if '{' in word:
                function_name_check = 0
                insertion_point['Function'] = j+1
 
        word_cnt += 1  

insertion_point['Loops'] = loops_lines
         

json_args = dict({
				"@1": ["size_t", "Name"],
				"@2": [["int*", "char*", "double*", "float*"], "Name"],
				"@3": [["int*", "char*", "double*", "float*"], "Type"],
				"@4": ["size_block", "Name"]
					})


final_json_dict = dict({function_name: dict({
                            'insertion_point'   : insertion_point['Global'],
                            'template_chars'    : json_args,
                            'Functions'         : dict({ 
                                                    'kernel_' + function_name.split(sep='_')[0] : dict({
                                                                                                    "Function Variables": json_vars,
                                                                                                    'insertion_point'   : dict({
                                                                                                                            'Loops'    : insertion_point['Loops'],
                                                                                                                            'Function' : insertion_point['Function']
                                                                                                    }),
                                                                                                    'API'               : function_name + '(' + ', '.join(list(args.keys())) + ')'
                                                                                                })
                                                })   
                            
                        })
                 })

final_jason = json.dumps(final_json_dict, indent=4)
with open(function_name + '_features'+".json", "w") as outfile:
    outfile.write(final_jason)


