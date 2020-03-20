import datetime
import sys

def graphparse(graphformula):
    graphformula.insert(0, '(')
    graphformula.append(')')

    stack = []
    subGraph = 0

    # Assign every element in the formula a node.
    dot = Digraph(comment='FO')

    interConnectives = []
    #predicates
    for index in range(0, len(graphformula)):
        isPred = False
        for predicate in predDic:
            if predicate in graphformula[index]:
                stack.append(graphformula[index])
                isPred = True
        if not isPred:
            if graphformula[index][0] == '(' and graphformula[index+2][-1] == ')':
                stack.append('(')
                stack.append(graphformula[index][1:])
            elif graphformula[index][-1] == ')' and graphformula[index-2][0] == '(':
                stack.append(graphformula[index][:-1])
                stack.append(')')
            else:
                stack.append(graphformula[index])

        if stack[-1] is ')':
            subf = []
            while stack[-1] is not "(":
                toAdd = stack.pop()
                if toAdd != '':
                    subf.append(toAdd)
            subf.append(stack.pop())
            subf.reverse()

            middle = []
            for i, j in enumerate(subf):
                if j in connectives and j not in ['\\neg', 'NOT']:
                    middle.append(i)
                if j == '\\neg':
                    subf[i] = 'neg'
                if j in equality:
                    middle.append(i)

            # quantifier
            if not middle:
                # Create last nodes
                for element in range(1, len(subf)-2):
                    name = 'A{0}'.format(element)
                    dot.node(name, subf[element])
                # link last nodes
                for element in range(1, len(subf)-3):
                    dot.edge('A{0}'.format(element), 'A{0}'.format(element+1))
                dot.edge('A{0}'.format(element+1), '{0}0'.format(subf[element+2][1]))
            # subtree creation
            else:
                if len(middle) == 1:
                    middle = middle[0]
                    # root
                    middleName = '{0}{1}'.format(subGraph, 0)
                    dot.node(middleName, subf[middle])

                    # Create Nodes:
                    LHSFlag, LHSFirstFlag = 0, 0
                    prevName = middleName
                    for LHS in range(1, middle):
                        name = '{0}L{1}'.format(subGraph, LHS)
                        if subf[LHS][0] == '#':
                            interConnectives.append([prevName, '{0}0'.format(subf[LHS][1])])
                            LHSFlag = 1

                            if LHS == 1:
                                LHSFirstFlag = 1
                        else:
                            dot.node(name, subf[LHS])
                            prevName = name

                    RHSFlag, RHSFirstFlag = 0, 0
                    prevName = middleName
                    for RHS in range(middle+1, len(subf)-1):
                        name = '{0}R{1}'.format(subGraph, RHS)
                        if subf[RHS][0] == '#':
                            interConnectives.append([prevName, '{0}0'.format(subf[RHS][1])])
                            RHSFlag = 1

                            if RHS == middle+1:
                                RHSFirstFlag = 1
                        else:
                            dot.node(name, subf[RHS])
                            prevName = name

                    # To middle node
                    theleft = '{0}L{1}'.format(subGraph, 1)
                    theright = '{0}R{1}'.format(subGraph, middle + 1)
                    if LHSFirstFlag != 1:
                        dot.edge(middleName, theleft)
                    if RHSFirstFlag != 1:
                        dot.edge(middleName, theright)

                    # LHS
                    leftrange = middle
                    if LHSFlag == 1:
                        leftrange -= 1
                    prevName = theleft
                    for LHS in range(2, leftrange, 1):
                        currentName = '{0}L{1}'.format(subGraph, LHS)
                        dot.edge(prevName, currentName)
                        prevName = currentName

                    # RHS
                    rightrange = len(subf)-1
                    if RHSFlag == 1:
                        rightrange -= 1
                    prevName = theright
                    for RHS in range(middle+2, rightrange, 1):
                        currentName = '{0}R{1}'.format(subGraph, RHS)
                        dot.edge(prevName, currentName)
                        prevName = currentName

                stack.append('#{0}'.format(str(subGraph)))
                subGraph += 1

    # Connect all sub graphs.
    for x in interConnectives:
        dot.edge(x[0], x[1])

    dot.render('fograph', view=True)


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
    global errorMessage
    form[i] = 'pq'  # parsed quantifier
    if form[i + 1] in variables:
        form[i + 1] = 'pv'  # parsed variable
        if form[i + 2] == '(':
            newForm = collectForm(form, i + 2)
            # if brackets were found surrounding a new formula, call parse again
            if newForm == 0:
                # Invalid brackets. Formula is not properly encompassed.
                return 0, globform, flag
            else:
                result, globform = parse(newForm, startind + i + 3, globform, flag)
                if result == 0:
                    return 0, globform, flag
                else:
                    count = i + 3
                    for item in result:
                        form[count] = item
                        count += 1
                    form[i + 1] = 'pv'  # set variable to pv = parsed variable
                    form[i] = 'pq'  # parsed quantifier
                    formcopy = form.copy()
                    for j in range(startind + i, startind + i + 2 + len(newForm) + 2):  # +2 so includes brackets
                        globform[j] = flag
                    flag += 1
                    form = formcopy.copy()

        elif form[i + 2] == '\\neg':
            form[i + 2] = 'pn'  # parsed connective
            j = 0
            # in case there are more than one neg after another
            while form[j + i + 3] == '\\neg' and (j + i + 3) < len(form) + 1:
                form[j + i + 3] = 'pn'  # parsed connective
                j += 1
            if (j + i + 3) == len(form):
                print("Invalid formula. Error with \\neg.")
                if errorMessage == "":
                    errorMessage = "Error with \\neg connective."
                return 0, globform, flag
            # if there is a bracket after the last neg
            if form[j + i + 3] == '(':
                newForm = collectForm(form, j + i + 3)
                if newForm == 0:
                    print('Given formula is invalid. Error in brackets.')
                    if errorMessage == "":
                        errorMessage = "Invalid brackets"
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
                if errorMessage == "":
                    errorMessage = 'Value after quantifier ' + form[i] + ' is not a formula.'
                return 0, globform, flag
            else:
                form[i + 2] = result[0]
            for k in range(startind + i, startind + i + 3):
                globform[k] = flag
            flag += 1

    else:
        # item after a quantifier isn't a variable
        print("Given formula is invalid. Value after quantifier should be a variable.")
        if errorMessage == "":
            errorMessage = "Value after " + form[i] + " is not a variable."

        return 0, globform, flag
    return form, globform, flag



errorMessage = ""
def parse(form, startind, globform, flag):
    global errorMessage
    for i in range(len(form)):
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
            predVal = form[0].replace(',', '')
            predVal = predVal.replace(' ', '')
            openbrac = predVal.index('(')
            closedbrac = predVal.index(')')
            numVar = closedbrac - openbrac - 1
            predLet = predVal[:openbrac]
            if predVal[:openbrac] not in predLetters:
                if errorMessage == "":
                    errorMessage = form[i] + " is not a defined formula"
                print("Given formula is invalid. Form[i] is not a defined formula.")
                return 0, 0
            #Formula of length one is a predicate
            else:
                found = False
                for item in predicates:
                    #Finding letter in predicates that corresponds to given formula
                    if item == predLet + '[' + str(numVar) + ']':
                        found = True
                        for j in range(openbrac+1, closedbrac):
                            if predVal[j] not in variables:
                                print("Given formula is invalid. Variable in predicate is invalid.")
                                if errorMessage == "":
                                    errorMessage = "Variable " + str(predVal[j]) + " is not a valid variable in " \
                                                                                      "predicate " + str(form[0])
                                return 0, 0
                        #Predicate is correct
                        form = ['vf']
                        globform[startind] = flag
                        flag += 1
                        break
                if found == False:
                    print("Predicate with that many values not found.")
                    if errorMessage == "":
                        errorMessage = "Predicate " + predLet + " with " + str(numVar) + " values not valid"
                    return 0, 0

        elif form[i] == '(':
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

        elif (form[i].find('(') != -1) and (form[i].find(')') != -1):
            result, globform = parse([form[i]], startind + i, globform, flag)
            if result == 0:
                if errorMessage == "":
                    errorMessage = "Predicate " + form[i] + " is invalid"
                print("Predicate " + form[i] + " returned as incorrect.")
                return 0, 0
            else:
                form[i] = result[0]
                globform[startind + i] = flag
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
    return form, globform

givenFile = sys.argv[1]
with open(givenFile, "r") as inpFile:
    for aLine in inpFile:
        #Separate different parts of language definition
        currentLineArray = aLine.split()
        if currentLineArray[0] == 'variables:':
            variables = currentLineArray[1:]
        elif currentLineArray[0] == 'constants:':
            constants = currentLineArray[1:]
        elif currentLineArray[0] == 'predicates:':
            predicates = currentLineArray[1:]
            predDic = []
            predSize = {}
            for item in currentLineArray[1:]:
                for i, j in enumerate(item):
                    if j == '[':
                        leftBracket = i
                    if j == ']':
                        rightBracket = i
            name = item[:leftBracket]
            size = item[leftBracket + 1:rightBracket]
            predDic.append(name)
            predSize[name] = size
        elif currentLineArray[0] == 'equality:':
            equality = currentLineArray[1:]
        elif currentLineArray[0] == 'connectives:':
            connectives = currentLineArray[1:]
        elif currentLineArray[0] == 'quantifiers:':
            quantifiers = currentLineArray[1:]
        elif currentLineArray[0] == 'formula:':
            formula = currentLineArray[1:]
        else:
            formula += currentLineArray


#Printing out grammar of language defined

terminal = variables + constants + predicates
nonterminal = ['S', 'D', 'V', 'A', 'E', 'F', 'G']
print("The grammar generated from the input file is as follows:")
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
    predVal = predicates[i].replace(',', '')
    predVal = predVal.replace(' ', '')
    openbrac = predVal.index('[')
    closedbrac = predVal.index(']')
    numVar = int(predVal[openbrac+1:closedbrac])
    predLet = predVal[:openbrac]
    predProd.append(predLet + '(')
    predLetters.append(predLet)
    for j in range(numVar):
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
print('\n')

#Breaking up formula into list


def remove_values_from_list(the_list, val):
   return [value for value in the_list if value != val]

i = 0
formattedFormula = []
while i < len(formula):
    if formula[i][-1] == ',':
        inc = 0
        temp = ''
        while formula[i + inc][-1] == ',':
            temp += formula[i + inc]
            inc += 1
        temp += formula[i + inc]
        formattedFormula.append(temp)
        i += inc + 1
    else:
        formattedFormula.append(formula[i])
        i += 1
graphform = formattedFormula.copy()
finalform = formattedFormula.copy()
flag = 0
try:
    result, finalform = parse(formattedFormula, 0, finalform, flag)
except:
    print("Unspecified error")
    result = 0

if result != 0:
    finalCheckResult = result.copy()
    finalCheckResult = remove_values_from_list(finalCheckResult, ')')
    finalCheckResult = remove_values_from_list(finalCheckResult, '(')


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
    print('Your formula is invalid. See log.txt for more info.')
    if errorMessage == "":
        errorMessage = "Invalid formula"
    recordLog("Failure", errorMessage)
else:
    recordLog("Success", "None")
    print("Your formula was successfully validated. See log.txt for additional information.")
    print('Your tokenised formula is:')
    print(result)

from graphviz import Digraph
if result != 0:
    graphparse(graphform)







