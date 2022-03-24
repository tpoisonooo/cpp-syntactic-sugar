import os

def add_extra(extra):
    for root, dirs, files in os.walk("./"):
        for name in files:
            if ".comp" not in name:
                continue
            fullpath = os.path.join(root, name)
            lines = []
            with open(fullpath) as fin:
                lines = fin.readlines()
                fin.flush()
                fin.close()
            writelines = []
            for line in lines:
                writelines.append(line)
                if "#version 450" in line:
                    writelines.append(extra)
            with open(fullpath, "w") as fout:
                fout.writelines(writelines)
                fout.flush()
                fout.close()

def proc_file(fullpath):
    lines = []
    start_idx = -1
    end_idx = -1
    with open(fullpath) as fin:
        lines = fin.readlines()
        fin.flush()
        fin.close()
    
    record_clause = False
    prefix_empty = -1
    all_clauses = []
    act_clause = []
    for idx,line in enumerate(lines):
        if record_clause:
            act_clause.append(line.strip())
    
            temp = line[prefix_empty:]
            if temp.count("}") > 1 :
                print("warning: {} {} {}".format(name, idx, temp))
    
            if "}" in temp:
                assert("{" in act_clause[0])
                assert("}" in act_clause[-1])
                all_clauses.append(act_clause[1:-1])
                act_clause = []
                end_idx = idx
                record_clause = False
    
        if "activation_type ==" in line:
            if start_idx == -1:
                start_idx = idx
    
            record_clause = True
            prefix = line.find("if (") 
            prefix_empty = line[0:prefix].count(" ")
            print(prefix)
    
    if start_idx == -1:
        return [] 
    ## start_idx  end_idx
    print("file {} start {} end {}".format(fullpath, start_idx, end_idx))
    ## copy first part
    new_lines = lines[0:start_idx]
    emptys = " " * prefix_empty 
    new_lines.append(emptys + "switch(activation_type)\n")
    new_lines.append(emptys + "{\n")

    for i,clauses in enumerate(all_clauses):
        new_lines.append(emptys + " " * 4 + "case " + str(i+1) + ":\n")

        for clause in clauses:
            new_lines.append(emptys+ " "*8 + clause+ "\n")

        new_lines.append(emptys + " "*8 + "break;\n" )
    
    new_lines.append(emptys + "}\n")
    new_lines.extend(lines[end_idx+1:])

    return new_lines

        

def ifelse_to_switch():
    for root, dirs, files in os.walk("./"):
        for name in files:
            if ".comp" not in name:
                continue
            fullpath = os.path.join(root, name)
            nlines = proc_file(fullpath)
            if len(nlines) <= 0:
                continue
            with open(fullpath, "w") as fout:
                fout.writelines(nlines)
                fout.flush()
                fout.close()



if __name__ == "__main__":
#    nlines = proc_file("./innerproduct_gemm.comp")
#    for line in nlines:
#        print(line)

    ifelse_to_switch()
