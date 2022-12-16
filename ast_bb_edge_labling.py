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
print('Pleas type the name of file (The C++ program)')
filename = input() 
lines_original = []
try:
    f = open(filename, 'r')
    for line in f:
        lines_original.append(line)
    f.close()
except:
    print('There is no such file')


# Reading the AST file
lines = []
try:
    os.system('g++ ' + filename + ' -fdump-tree-all-graph ' + '-o out.o')
    AST_filename = 'a-' + filename + '.023t.ssa' 
    f = open(AST_filename, 'r')
    for line in f:
        lines.append(line)
    f.close()
except:
    print('You have not dumped the corresponded AST and the program cannot do it either')



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

Loops_list_dict = list()

insertion_point = dict()

functions_var = ['+', '-', '*', '/']

loops_lines = []

#Parsing the Actual code line by line so that extractin features and corresponding lines
for line in lines_original:
    temp_dict = dict()
    temp_loop_iter = dict()
    j += 1
    for_main_line  = 0
    for_par        = 0
    iter_var       = 0
    iter_var_check = 0
    for word in line.split():
        #Here I assume that the global line is the line which is the function is defined
        if function_name in word:
            insertion_point['Global'] = j

        #Here I assume that the function line is where an mathematical operation is occured        
        for op in functions_var:
            if op in word:
                insertion_point['Function'] = j   

        #Looking for loops     
        if check_var('for', word):
            loops_lines.append({'Loop ID': loop_ID_cnt, 'Line': j})
            loop_ID_cnt   += 1
            for_main_line  = 1
            temp_dict['ID']                      = loop_ID_cnt
            temp_dict['Nested Level']            = nested_level
            temp_dict['Immediate_Outer_Loop_ID'] = Immediate_Outer_Loop_ID
            Immediate_Outer_Loop_ID = loop_ID_cnt
        if check_var('while', word):
            loops_lines.append({'Loop ID': loop_ID_cnt, 'Line': j})
            loop_ID_cnt   += 1
            temp_dict['ID']                      = loop_ID_cnt
            temp_dict['Nested Level']            = nested_level
            temp_dict['Immediate_Outer_Loop_ID'] = Immediate_Outer_Loop_ID
            Immediate_Outer_Loop_ID = loop_ID_cnt
            temp_dict['loop_iterator'] = {}

        if for_main_line:
            if '(' in word:
                for_par = 1
            if ')' in word:
                for_par       = 0
                for_main_line = 0
                Loops_list_dict.append(temp_dict)
            if iter_var:
                iter_var       = 0
                iter_var_check = 1
                temp_loop_iter['Name']                 = word
                temp_loop_iter['declaration_line_num'] = j
                temp_loop_iter['read_only']            = 0
                temp_dict['loop_iterator'] = temp_loop_iter
            if not (iter_var_check or iter_var):
                for var in cpp_var:
                    if check_var(var, word):
                        iter_var = 1
                        temp_loop_iter['Type'] = var
                        break

insertion_point['Loops'] = loops_lines

#I don't know what exactly is VarSpecifier
insertion_point['VarSpecifier'] = ''
            
            
        
final_json_dict = dict({
                       'File Name': filename.split(sep='.')[0][2:],
                       'Function Name': function_name,
                      # 'template_chars': json_args,
                       'Notes': '',
                       "Function Variables": json_vars,
                       'Loops' : Loops_list_dict,
                       'insertion_point': insertion_point
                 })

final_jason = json.dumps(final_json_dict, indent=4)
with open(function_name + '_features'+".json", "w") as outfile:
    outfile.write(final_jason)


