import pandas as pd

from IPython.display import HTML as html_print
from IPython.display import display

import re

import numpy as np

##############
### Set Up ###
##############

### UPLOAD FROM GOOGLE DRIVE ####

def data_from_GD(file_name,tab_name):

  # mount
  from google.colab import auth
  auth.authenticate_user()

  import gspread
  from google.auth import default
  creds, _ = default()

  gc = gspread.authorize(creds)

  # real code
  worksheet = gc.open(file_name).worksheet(tab_name)

  # get_all_values gives a list of rows.
  rows = worksheet.get_all_values()

  import pandas as pd
  df_name = pd.DataFrame.from_records(rows)

  df_name.columns = df_name.iloc[0]  # Set the first row as header
  df_name = df_name[1:]  # Remove the first row from the data

  # Reset the index (optional)
  df_name.reset_index(drop=True, inplace=True)

  return df_name

### Dataset Construction ###

def construct_dataset(data,id,new_year,new_year_num,old_year,old_year_num): # data to load, position of the id column, position of the new_year column, position of the old_year column

  nyn = 'y_'+ str(new_year_num)
  oyn = 'y_'+ str(old_year_num)

  dataset = pd.DataFrame({'Statement ID' : [],
                         nyn : [],
                         oyn : []})

  if id != False:

    dataset['Statement ID']=data.iloc[:, id].apply(int)
    dataset[nyn]=data.iloc[:, new_year].apply(str)
    dataset[oyn]=data.iloc[:, old_year].apply(str)

  else:
    dataset['Statement ID']= range(len(data))
    dataset[nyn]=data.iloc[:, new_year].apply(str)
    dataset[oyn]=data.iloc[:, old_year].apply(str)

  return dataset[['Statement ID',nyn,oyn]]


##############################
### Text Reuse Definitions ###
##############################

### IDENTIFY REUSE ###

def id_reuse(str1,str2,l):

  new1 = str1.lower().split()
  new2 = str2.lower().split()

  #print(new1)
  #print(new2)

  long_answer = []

  for i in range(0,len(new1)-1):
    for j in range(0,len(new2)-1):
      ans = []
      if new1[i]==new2[j]:
        n=i
        m=j
        while new1[n]==new2[m]:

          ans.append(new1[n])
          if n<len(new1)-1 and m<len(new2)-1:
            n+=1
            m+=1
          else:
            break


      if len(ans)>=len(long_answer):
        long_answer = list(ans)

  if len(long_answer) >= l:
    return" ".join(long_answer)


### IDENTIFY ALL REUSE ###

def reuse_loops2(str1,str2,l):

  ##################
  # Pre Processing

  m_str1 = str1.lower()
  m_str1 = re.sub('([a-zA-Z.,;!?()-])([.,;!?()-])', r'\1 \2', m_str1) #  !()-[]{};:'"\,<>./?@#$%^&*_~
  m_str1 = re.sub('([.,;!?()-])([a-zA-Z])', r'\1 \2', m_str1)
  m_str1 = m_str1.replace("  ", " ")
  m_str2 = str2.lower()
  m_str2 = re.sub('([a-zA-Z.,;!?()-])([.,;!?()-])', r'\1 \2', m_str2)
  m_str2 = re.sub('([.,;!?()-])([a-zA-Z])', r'\1 \2', m_str2)
  m_str2 = m_str2.replace("  ", " ")

  ##################
  # First Split

  # Get reused phrase
  reuse = id_reuse(m_str1,m_str2,l)

  if reuse != None:

    # split phrases string #1
    new_str = []
    #try: 
    #  if m_str1 == reuse:
    #    print("YES")
    #    new_str.append((reuse,'black'))
    #  else:
    try:
      str1_pre = m_str1.split(reuse)[0]
      #print("m_str1:", m_str1)
      #print("reuse:", reuse)
      #print("pre:", str1_pre)
      #print(m_str1 == reuse)
      new_str.append((str1_pre, 'green'))
    except IndexError:
      False
    new_str.append((reuse,'black'))
    #print("reuse:", reuse)
    try:
      str1_post = m_str1.split(reuse)[1]
      new_str.append((str1_post, 'green'))
      #print("post:", str1_post)
    except IndexError:
      False
    #except IndexError:
    #    False
    #print(new_str)

    # split phrases string #2
    old_str = []
    try:
      str2_pre = m_str2.split(reuse)[0]
      old_str.append((str2_pre, 'red'))
    except IndexError:
      False
    old_str.append((reuse,'black'))
    try:
      str2_post = m_str2.split(reuse)[1]
      old_str.append((str2_post, 'red'))
    except IndexError:
      False
    #print(old_str[1][1])

    #####################
    # Additional Splits
    s = -1
    for s in range(round(int((len(m_str1.split()))/(l)),0)):

      #print('####') 
      #print(s)
      #print(new_str)
      #print(old_str)

      s+=1

      for x in range(len(new_str)):
        if new_str[x][1] != 'black':
          for y in range(len(old_str)):
            if old_str[y][1] != 'black':
              #print('x is:', x)
              #print('str x is:', new_str[x][0])
              #print('y is:', y)
              #print('str y is:', old_str[y][0])
              reuse_a = id_reuse(new_str[x][0],old_str[y][0],l)
              if reuse_a == None:
                #print('reuse_a is: NONE')
                continue
              else:
                #print('reuse_a is:', reuse_a)

                # split phrases string #1
                g = x
                #print('g is:', g)
                m_str_1_a = new_str[g][0]
                #print(new_str[g][0])
                #print(m_str_1_a.split(reuse_a))
                new_str.pop(g)

                try:
                  str1_pre = m_str_1_a.split(reuse_a)[0]
                  #print(g, (str1_pre, 'green'))
                  new_str.insert(g,(str1_pre, 'green'))
                except IndexError:
                  False
                new_str.insert(g+1,(reuse_a,'black'))
                #print(g+1, (reuse_a,'black'))
                try:
                  str1_post = m_str_1_a.split(reuse_a)[1]
                  new_str.insert(g+2,(str1_post, 'green'))
                  #print(g+2, (str1_post, 'green'))
                except IndexError:
                  False

                #print(new_str)

                # split phrases string #2
                w = y
                #print('w is:', w)
                m_str_2_a = old_str[w][0]
                old_str.pop(w)

                try:
                  str2_pre = m_str_2_a.split(reuse_a)[0]
                  old_str.insert(w,(str2_pre, 'red'))
                except IndexError:
                  False
                old_str.insert(w+1,(reuse_a,'black'))
                try:
                  str2_post = m_str_2_a.split(reuse_a)[1]
                  old_str.insert(w+2,(str2_post, 'red'))
                except IndexError:
                  False

              #print(old_str)

  else:
    new_str = []
    new_str.append((m_str1, 'green'))

    old_str = []
    old_str.append((m_str2, 'red'))


  #####################
  return new_str, old_str

### Dataset to Dataset ###

def reuse_dataset_to_dataset(data,id,new_year,old_year,l):

  ny = data.columns[new_year]
  oy = data.columns[old_year]

  nt = ny+'_N_Text'
  ntw = ny+'_N_Text_WC'

  na = ny+'_Added'
  naw = ny+'_Added_WC'
  nr = ny+'_Reused'
  nrw = ny+'_Reused_WC'
  nter = ny+'_Terminated'
  nterw = ny+'_Terminated_WC'

  ot = oy+'_O_Text'
  otw = oy+'_O_Text_WC'

  rmnt = ny+'_New_Ratio_of_Match'
  rmot = ny+'_Old_Ratio_of_Match'
  njs = ny+'_Jaccard_Similarity'

  clean_data = pd.DataFrame(columns = ['Statement ID', nt, ntw, na, naw, nr, nrw, nter, nterw, ot, otw, rmnt, rmot, njs])

  for x in range(len(data)):

    id_num = data.iloc[x,id]
    new = data.iloc[x,new_year]
    old = data.iloc[x,old_year]

    new_str, old_str = reuse_loops2(new,old,l)

    added = ""
    added2 = ""
    reuse = ""
    reuse2 = ""
    removed = ""
    removed2 = ""

    # Reused text

    for x in range(len(new_str)):
      if new_str[x][1] != 'black':
        if added != "":
          added = " ".join([added, "[...]"])
        added = " ".join([added, new_str[x][0]])
        added2 = " ".join([added2, new_str[x][0]])
      else:
        if reuse != "":
          reuse = " ".join([reuse, "[...]"])
        reuse = " ".join([reuse, new_str[x][0]])
        reuse2 = " ".join([reuse2, new_str[x][0]])

    for x in range(len(old_str)):
      if old_str[x][1] != 'black':
        if removed != "":
          removed = " ".join([removed, "[...]"])
        removed = " ".join([removed, old_str[x][0]])
        removed2 = " ".join([removed2, old_str[x][0]])

        # Counts

    if new != "" and new != "nan" and new != " nan":
      new_wc = len(re.findall(r'\w+', new))
    else:
      new_wc = 0

    if added2 != "" and added2 != "nan" and added2 != " nan":
      added_wc = len(re.findall(r'\w+', added2))
    else:
      added_wc = 0

    if reuse2 != "" and reuse2 != "nan" and reuse2 != " nan":
      reuse_wc = len(re.findall(r'\w+', reuse2))
    else:
      reuse_wc = 0

    if removed2 != "" and removed2 != "nan" and removed2 != " nan":
      removed_wc = len(re.findall(r'\w+', removed2))
    else:
      removed_wc = 0

    if old != "" and old != "nan" and old != " nan":
      old_wc = len(re.findall(r'\w+', old))
    else:
      old_wc = 0

    # Reuse Calculations

    if new_wc != 0:
      rom_new = reuse_wc/new_wc
    else:
      rom_new = 0
    if old_wc != 0:
      rom_old = reuse_wc/old_wc
    else:
      rom_old = 0

    if new_wc == 0 and old_wc == 0 :
      jac_sim = 0
    else:
      jac_sim = reuse_wc/(added_wc + reuse_wc + removed_wc)

    # Fill Empty Cells to Make Python Happy

    #if new == "" or new == " " or new == "nan":
    #  new = "EMPTY"

    #if added == "" or added == " " or added == "nan":
    #  added = "EMPTY"

    #if reuse == "" or reuse == " " or reuse == "nan":
    #  reuse = "EMPTY"

    #if removed == "" or removed == " " or removed == "nan":
    #  removed = "EMPTY"

    #if old == "" or old == " " or old == "nan":
    #  old = "EMPTY"

    #if added2 == "" or added2 == " " or added2 == "nan":
    #  added2= "EMPTY"

    #if reuse2 == "" or reuse2 == " " or reuse2 == "nan":
    #  reuse2 = "EMPTY"

    #if removed2 == "" or removed2 == " " or removed2 == "nan":
    #  removed2 = "EMPTY"

    clean_data = clean_data._append({'Statement ID':id_num,nt:new,ntw: new_wc, na:added, naw: added_wc, nr:reuse, nrw: reuse_wc, nter:removed, nterw: removed_wc, ot:old, otw: old_wc, rmnt: rom_new, rmot: rom_old, njs: jac_sim},ignore_index=True)
  return clean_data


###############
### MERGING ###
###############

### STRAINGHT MERGE ####
def straight_merge(new_df,old_df):

  n_suf = "_"+new_df.columns[1][:6]
  o_suf = "_"+old_df.columns[1][:6]

  matched_df = new_df.join(old_df.drop(old_df.columns[:1], axis=1), lsuffix=n_suf, rsuffix=o_suf)

  return matched_df

### STRAINGHT MERGE Text Only ####
def straight_merge_text_only(new_df,old_df):

  small_new_df = new_df.iloc[:, [0,1,3,5,7]]
  small_old_df = old_df.iloc[:, [1,3,5,7,9]]

  n_suf = "_"+new_df.columns[1][:6]
  o_suf = "_"+old_df.columns[1][:6]

  matched_df = small_new_df.join(small_old_df, lsuffix=n_suf, rsuffix=o_suf)

  return matched_df


#################################
### LOOP THROUGH GOOGLE SHEET ###
#################################

### SHEET LOOP ####
def sheet_loop(TAB,l):

  # get all column headings that contain the text "Stats" and put it into a list
  cols = [col for col in TAB.columns]
  c_prev = None
  results = []
  for i in range (len(cols) -1):
    c = construct_dataset(TAB,False,i,len(cols)-i,i+1,len(cols)-i]) # c = construct_dataset(TAB,False,i,cols[i],i+1,cols[i+1])
    c_out = reuse_dataset_to_dataset(c,0,1,2,l)
    #print(c_out)
    if c_prev is not None:
      c_prev = straight_merge(c_prev,c_out)
    else:
      c_prev = c_out


  return c_prev

################
### OUT PUTS ###
################

### Print in Color ###

from IPython.display import HTML as html_print
from IPython.display import display

def cstr(s, color='black'):
    return "<text style=color:{}>{}</text>".format(color, s)

def print_color(t):
    display(html_print(' '.join([cstr(ti, color=ci) for ti,ci in t])))

### Single Color ###

def reuse_color_coded(str1,str2,l):
  new_str, old_str = reuse_loops2(str1,str2,l)

  # PRINT
  print('New Language:')
  print_color((new_str))

  print('Old Language:')
  print_color((old_str))
