import datetime

def recordLog(status, message):
    global inpFile
    filename = inpFile.name
    dt = str(datetime.datetime.now())
    logfile = open("log.txt", "a")
    logfile.write(f"{dt[:19]}\t Input: {filename}\t Status: {status}\t Further info: {message}\n")
    logfile.close()

def collectForm(form, i):
    endBrac = False
    if form[i] == '(':
        j = i+1
        bracCount = 1
        while (endBrac == False) and j < len(form):
            if form[j] == '(':
                bracCount += 1
            elif form[j] == ')':
                bracCount -= 1
            if bracCount == 0:
                endBrac = True
            else:
                j += 1
        # if brackets were found surrounding a new formula, call parse again
        if endBrac == True:
            return form[i+1:j]
        else:
            return 0
    elif form[i] == ')':
        j = i-1
        bracCount = 1
        while (endBrac == False) and j>=0:
            if form[j] == ')':
                bracCount += 1
            elif form[j] == '(':
                bracCount -= 1
            if bracCount == 0:
                endBrac = True
            else:
                j -=1
        if endBrac == True:
            return form[j+1:i]
        else:
            return 0

def quantEncounter(form, i, startind, globform, flag):
    print('in quantifiers')
    form[i] = 'pq'  # parsed quantifier
    print(form)
    print('in encounterquant, form[i+1]:')
    print(form[i+1])
    if form[i + 1] in variables:
        form[i + 1] = 'pv'  # parsed variable
        print('in variables')
        print(form)
        if form[i + 2] == '(':
            newForm = collectForm(form, i + 2)
            print('newform is ' + str(newForm))
            # if brackets were found surrounding a new formula, call parse again
            if newForm == 0:
                # Invalid brackets. Formula is not properly encompassed.
                print("Given formula is invalid. Error in brackets")
                return 0, globform, flag
            else:
                print('newForm in encounterQuant')
                print(newForm)
                result, globform = parse(newForm, startind + i + 3, globform, flag)
                print('just returned parsing in encounterquant and the result is:')
                print(result)
                print('and globform is: ')
                print(globform)
                if result == 0:
                    print("Given formula is invalid.")
                    return 0, globform, flag
                else:
                    count = i + 3
                    print('form before editing:')
                    print(form)
                    for item in result:
                        form[count] = item
                        count += 1
                    form[i + 1] = 'pv'  # set variable to pv = parsed variable
                    form[i] = 'pq'  # parsed quantifier
                    print('new form after editing')
                    print(form)
                    formcopy = form.copy()
                    for j in range(startind + i, startind + i + 2 + len(newForm) + 2):  # +2 so includes brackets
                        globform[j] = flag
                    flag += 1
                    form = formcopy.copy()
                    print('form after for loop')
                    print(form)

        elif form[i + 2] == '\\neg':
            form[i + 2] = 'pn'  # parsed connective
            j = 0
            # in case there are more than one neg after another
            while form[j + i + 3] == '\\neg' and (j + i + 3) < len(form) + 1:
                form[j + i + 3] = 'pn'  # parsed connective
                j += 1
            if (j + i + 3) == len(form):
                print("Invalid formula. Error with negs.")
                return 0, globform, flag
            # if there is a bracket after the last neg
            if form[j + i + 3] == '(':
                newForm = collectForm(form, j + i + 3)
                if newForm == 0:
                    print('Given formula is invalid. Error in brackets.')
                    return 0, globform, flag
                else:
                    result, globform = parse(newForm, startind + i + j + 4, globform, flag)
                    if result == 0:
                        print("Formula is invalid")
                        return 0, globform, flag
                    else:
                        count = j + i + 4
                        for item in result:
                            form[count] == item
                            count += 1
                for k in range(startind + i, startind + i + j + 3 + len(newForm) + 2):
                    globform[k] = flag
                flag += 1

            else:
                # the item after the neg should be a formula
                result, globform = parse([form[j + i + 3]], startind + i + j + 3, globform, flag)
                if result == 0:
                    print('Given formula is invalid')
                    return 0, globform, flag
                else:
                    form[j + i + 3] = result[0]
                for k in range(startind + i, startind + i + j + 4):
                    globform[k] = flag
                flag += 1

        else:
            # return next item to check its a formula
            # in next iteration make sure its not a constant or variable
            result, globform = parse([form[i + 2]], startind + i + 2, globform, flag)
            if result == 0:
                print('Invalid formula. Value after quantifier ' + form[i] + ' is not a formula.')
                return 0, globform, flag
            else:
                form[i + 2] = result[0]
            for k in range(startind + i, startind + i + 3):
                globform[k] = flag
            flag += 1

    else:
        # item after a quantifier isn't a variable
        print("Given formula is invalid")
        return 0, globform, flag
    print('form to be returned: ')
    print(form)
    return form, globform, flag



errorMessage = ""
def parse(form, startind, globform, flag):
    global errorMessage
    for i in range(len(form)):
        print('i is ' + str(i))
        print('form:')
        print(form)
        print('form[i]:')
        print(form[i])

        if form[i] in equality:
            print("Equality symbol out of place.")
            if errorMessage == "":
                errorMessage = "Equality symbol out of place"
            return 0, 0
        elif form[i] in constants:
            print("Given formula is invalid. Constant found rogue.")
            if errorMessage == "":
                errorMessage = "Constant symbol out of place"
            return 0, 0
        elif form[i] in variables:
            print("Given formula is invalid. Variable found rogue.")
            if errorMessage == "":
                errorMessage = "Variable symbol out of place"
            return 0, 0
        #if a formula of length one is returned, it must be a predicate
        elif len(form) == 1:
            print('len form is 1')
            predVal = form[0].replace(',', '')
            if predVal[0] not in predLetters:
                if errorMessage == "":
                    errorMessage = str(form[i]) + " is not a defined formula"
                print("Given formula is invalid. Form[i] is not a defined formula.")
                return 0, 0
            #Formula of length one is a predicate
            else:
                #Counting number of variable letters in given predicate
                numVar = len(predVal) - 3
                for item in predicates:
                    #Finding letter in predicates that corresponds to given formula
                    if item[0] == predVal[0]:
                        if int(item[2]) != int(numVar):
                            print("Given formula is invalid. Number of variables in predicate is invalid.")
                            if errorMessage == "":
                                errorMessage = "Invalid number of variables in predicate " + str(form[i])
                            return 0, 0
                        else:
                            print("Correct number of variables in predicate")
                            print(form)
                            print(len(form[0]))
                            for j in range(2, len(form[0])-1):
                                print('in for loop')
                                print(form[0][j])
                                if form[0][j] != ',':
                                    print('variable: ' + str(form[0][j]))
                                    if form[0][j] not in variables:
                                        print("Given formula is invalid. Variable in predicate is invalid.")
                                        if errorMessage == "":
                                            errorMessage = "Variable " + str(form[0][j]) + " is not a valid variable in predicate " + str(form[0])
                                        return 0, 0
                            #Predicate is correct
                            form = ['vf']
                            globform[startind] = flag
                            flag += 1

        elif form[i] == '(':
            print(form[i])
            if len(form) > 1:
                if (form[i+1] != 'vf') and (form[i+1] != 'vfe'):
                    newForm = collectForm(form, i)
                    if newForm == 0:
                        if errorMessage == "":
                            errorMessage = "Invalid brackets"
                        print("Given formula is invalid. Error in brackets.")
                        return 0, 0
                    else:
                        result, globform = parse(newForm, startind+i+1, globform, flag)
                        if result == 0:
                            return 0,0
                        else:
                            count = i + 1
                            for item in result:
                                form[count] = item
                                count += 1
                            for j in range(startind+i, startind+i+len(newForm)+2 ): #+2 so includes brackets
                                globform[j] = flag
                            flag +=1
            else:
                print('( is not a formula.')
                if errorMessage == "":
                    errorMessage = "Rogue '(' exists where a formula should"
                return 0, 0



        elif form[i] in quantifiers:
            form, globform, flag = quantEncounter(form, i, startind, globform, flag)
            if form == 0:
                return 0, 0

        elif form[i][0] in predLetters:
            result, globform = parse([form[i]], startind+i, globform, flag)
            if result == 0:
                if errorMessage == "":
                    errorMessage = "Predicate " + form[i] + " is invalid"
                print("Predicate " + form[i] + " returned as incorrect.")
                return 0, 0
            else:
                form[i] = result[0]
                globform[startind+i] = flag
                flag += 1

        elif len(form[i]) == 2 and form[i][0] == '(':
            try:
                if (form[i][1] in constants or form[i][1] in variables) and (form[i+1] in equality) and (form[i+2][0] in variables or form[i+2][0] in constants):
                        form[i] = 'vfe' #valid formula equality
                        form[i+1] = 'vfe'
                        form[i+2] = 'vfe'
                        for k in range(startind+i, startind+i+3):
                            globform[k] = flag
                        flag+=1
                else:
                    print('Given formula is invalid. Error in equality, ' + str(form[i]) + str(form[i+2]) + str(form[i+3]))
                    if errorMessage == "":
                        errorMessage = "Error in equality, " + str(form[i]) + str(form[i+2]) + str(form[i+3])
                    return 0, 0
            except:
                if errorMessage == "":
                    errorMessage = "Equality expected after " + form[i] + " but not received"
                print("Equality expected after " + form[i] + " but not received")
                return 0, 0

        elif form[i] in connectives:
            # the item before the connective (already parsed) should be a formula
            # no need to check item before if connective is neg
            if form[i] != "\\neg":
                try:
                    if form[i - 1] == ')':
                        j = 0
                        while form[i - 1 - j] == ')':
                            j += 1
                        if (form[i - 1 - j] != 'vf') and (form[i - 1 - j] != 'vfe'):
                            print('Given formula is invalid. Item before connective ' + form[i] + ' is not a formula.')
                            if errorMessage == "":
                                errorMessage = 'Item before connective ' + form[i] + ' is not a formula.'
                            return 0, 0
                    elif form[i-1] != 'vf' and form[i-1] != 'vfe':
                        if errorMessage == "":
                            errorMessage = 'Item before connective ' + form[i] + ' is not a formula.'
                        print('Given formula is invalid. Item before connective ' + form[i] + ' is not a formula.')
                        return 0, 0
                except:
                    if errorMessage == "":
                        errorMessage = 'Connective ' + form[i] + ' cannot start a formula'
                    print('Connective ' + form[i] + ' cannot start a formula.')
                    return 0, 0
            conn = form[i]
            if conn == "\\neg":
                form[i] = 'pn' #parsed connective
            else:
                form[i] = 'pc'
            #if there is a bracket after the connective, it should contain a formula
            try:
                testVal = form[i+1]
            except:
                print("Given formula is invalid. No value after connective " + conn)
                if errorMessage == "":
                    errorMessage = 'No value after connective ' + conn
                return 0, 0

            if form[i+1] == '(':
                newForm = collectForm(form, i+1)
                if newForm == 0:
                    print('Given formula is invalid. Error in brackets.')
                    if errorMessage == "":
                        errorMessage = 'Item before connective ' + form[i] + ' is not a formula.'
                    return 0, 0
                else:
                    result, globform = parse(newForm, startind+i+2, globform, flag)
                    if result == 0:
                        print("Formula is invalid")
                        return 0, 0
                    else:
                        count = i + 2
                        for item in result:
                            form[count] == item
                            count += 1
                        for j in range(startind+i+1, startind+i+1+len(newForm)+2):
                            globform[k] = flag
                        flag +=1
            #if there is an equality after connective
            elif len(form[i]) == 2 and form[i][0] == '(':
                try:
                    if (form[i][1] in constants or form[i][1] in variables) and (form[i + 1] in equality) and (
                            form[i + 2][0] in variables or form[i + 2][0] in constants):
                        form[i] = 'vfe'  # valid formula equality
                        form[i + 1] = 'vfe'
                        form[i + 2] = 'vfe'
                        for k in range(startind + i, startind + i + 3):
                            globform[k] = flag
                        flag += 1
                    else:
                        print('Given formula is invalid. Error in equality, ' + str(form[i]) + str(form[i + 2]) + str(
                            form[i + 3]))
                        if errorMessage == "":
                            errorMessage = 'Error in equality, ' + str(form[i]) + str(form[i + 2]) + str(form[i + 3])
                        return 0, 0
                except:
                    print("Equality expected after " + form[i] + " but not received")
                    if errorMessage == "":
                        errorMessage = 'Equality expected after ' + form[i] + ' but not received'
                    return 0, 0


            #if there is a neg after the connective


            elif form[i+1] == '\\neg':
                form[i+1] = 'pn'
                print('form in connectives part neg')
                print(form)
                j= 0
                #in case there are more than one neg after another
                try:
                    while form[j+i+2] == '\\neg' and (j +i+2) < len(form) + 1:
                        if (j + i + 2) == len(form):
                            print("Invalid formula. Error with \\neg.")
                            if errorMessage == "":
                                errorMessage = 'Error with \\neg.'
                            return 0, 0
                        else:
                            form[j+i+2] = 'pn'
                            j += 1
                except:
                    print("Given formula is invalid. Error after \\neg.")
                    if errorMessage == "":
                        errorMessage = 'Error with \\neg.'
                    return 0, 0

                #if there is a bracket after the last neg
                if form[j+i+2] == '(':
                    newForm = collectForm(form, j+i+2)
                    if newForm == 0:
                        print('Given formula is invalid. Error in brackets.')
                        if errorMessage == "":
                            errorMessage = 'Invalid brackets'
                        return 0, 0
                    else:
                        result, globform = parse(newForm, startind+j+i+3, globform, flag)
                        if result == 0:
                            print("Formula is invalid")
                            return 0, 0
                        else:
                            count = j + i + 3
                            for item in result:
                                form[count] == item
                                count += 1
                            for k in range(startind+i+1, startind+i+j+2+len(newForm)+2): # i+j+2 = (
                                globform[k] = flag
                            flag +=1

                else:
                    #the item after the neg should be a formula
                    result, globform = parse([form[j + i + 2]], startind+i+j+2, globform, flag)
                    if result == 0:
                        print('Given formula is invalid')
                        return 0, 0
                    else:
                        form[j + i + 2] = result[0]
                        for k in range(startind+i+1, startind+j+i+2):
                            globform[k] = flag
                        flag+=1
            elif form[i+1] in quantifiers:
                form, globform, flag = quantEncounter(form, i+1, startind, globform, flag)
                if form == 0:
                    return 0, 0


            #the single item after the connective should be a formula
            else:
                try:
                    testVal = form[i+1] #seeing if there is a value after the current one
                except:
                    print("There is no value after connective " + form[i])
                    if errorMessage == "":
                        errorMessage = 'No value found after connective ' + form[i]
                    return 0, 0
                result, globform = parse([form[i+1]], startind+i+1, globform, flag)
                if result == 0:
                    print('Given formula is invalid')
                    return 0, 0
                else:
                    form[i+1] = result[0]
                    globform[startind+i+1] = flag
                    flag +=1

    print('Parsed form:')
    print(form)
    return form, globform

with open('example.txt', "r") as inpFile:
    for aLine in inpFile:
        #Separate different parts of language definition
        currentLineArray = aLine.split()
        if currentLineArray[0] == 'variables:':
            variables = currentLineArray[1:]
            print(variables)
        elif currentLineArray[0] == 'constants:':
            constants = currentLineArray[1:]
            print(constants)
        elif currentLineArray[0] == 'predicates:':
            predicates = currentLineArray[1:]
            print(predicates)
        elif currentLineArray[0] == 'equality:':
            equality = currentLineArray[1:]
            print(equality)
        elif currentLineArray[0] == 'connectives:':
            connectives = currentLineArray[1:]
            print(connectives)
        elif currentLineArray[0] == 'quantifiers:':
            quantifiers = currentLineArray[1:]
            print(quantifiers)
        elif currentLineArray[0] == 'formula:':
            formula = currentLineArray[1:]
        else:
            formula += currentLineArray
    print(formula)


#Printing out grammar of language defined

terminal = variables + constants + predicates
nonterminal = ['S', 'D', 'V', 'A', 'E', 'F', 'G']
if "\\neg" in connectives:
    print('S -> (S) | SDS | NS | A | E | \\neg S | \epsilon')
else:
    print('S -> (S) | SDS | NS | A | E | \epsilon')
varPrint = ' | '.join(variables)
print('V -> ' + varPrint)
connPrint = ' | '.join(connectives)
connPrint1 = connectives.remove("\\neg")
print('D -> ' + connPrint)
quantifiersProd = []
for i in range(0, len(quantifiers)):
    quantifiersProd.append(quantifiers[i] + ' VS')
quantPrint = ' | '.join(quantifiersProd)
print('N -> ' + quantPrint)
predProd = []
predLetters = []
for i in range(len(predicates)):
    predProd.append(predicates[i][0] + '(')
    predLetters.append(predicates[i][0])
    for j in range(int(predicates[i][2])):
        predProd[i] = predProd[i] + 'V'
    predProd[i] = predProd[i] + ')'
predProdPrint = ' | '.join(predProd)
print('A -> ' + predProdPrint)
if equality != []:
    print('E -> F' + equality[0] + 'F')
formattedConst = constants.copy()
for i in range(len(formattedConst)):
    formattedConst[i] = 'const' + formattedConst[i]
constPrint = ' | '.join(formattedConst)
print('C -> ' + constPrint)
if (constants != []) and (variables != []):
    print('F -> V | C')

#Breaking up formula into list


def remove_values_from_list(the_list, val):
   return [value for value in the_list if value != val]


finalform = formula
flag = 0
try:
    result, finalform = parse(formula, 0, finalform, flag)
except:
    print("Unspecified error")
    result = 0

if result != 0:
    finalCheckResult = result.copy()
    finalCheckResult = remove_values_from_list(finalCheckResult, ')')
    finalCheckResult = remove_values_from_list(finalCheckResult, '(')
    print('finalCheckResult')
    print(finalCheckResult)


    for i in range(len(finalCheckResult) -1 ):
        if finalCheckResult[i] == 'vf':
            if finalCheckResult[i+1] == 'vf' or finalCheckResult[i+1] == 'vfe' or finalCheckResult[i+1] == 'pq' or finalCheckResult[i+1] == 'pn':
                print("Given formula is incorrect. Two formulae are placed adjacent.")
                errorMessage = "Two formulae are placed adjacent"
                result = 0
                break
        elif finalCheckResult[i] == 'vfe':
            if finalCheckResult[i+1] == 'vf' or finalCheckResult[i+1] == 'pq' or finalCheckResult[i+1] == 'pn':
                print("Given formula is incorrect. Two formulae are placed adjacent.")
                errorMessage = "Two formulae are placed adjacent"
                result = 0
                break

if result == 0:
    print('result = 0. Invalid formula')
    if errorMessage == "":
        errorMessage = "Invalid formula"
    recordLog("Failure", errorMessage)
else:
    recordLog("Success", "None")
    print('Result:')
    print(result)
    print('finalform/globform:')
    print(finalform)







